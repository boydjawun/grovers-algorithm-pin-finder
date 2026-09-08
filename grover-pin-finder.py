import argparse
import math
import random
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

""" Builds an oracle that flips the phase of the |target> basis state"""
def build_oracle(n_qubits: int, target: str) -> QuantumCircuit:
    oracle = QuantumCircuit(n_qubits, name="Oracle")
    # Flip qubits that should be 0 in the target, so the target maps to |11...1>
    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            oracle.x(i) 
            # Multi-controlled Z: flips the phase of |11...1> to -|11>
            oracle.h(n_qubits -1)
            oracle.mcx(list(range(n_qubits - 1)), n_qubits - 1)
            oracle.h(n_qubits - 1)
    # Undo the X flips
    for i, bit in enumerate(reversed(target)):
        if bit == "0":
            oracle.x(i)
    return oracle

"""Builds the standard Grover diffuser (inversion about the mean)."""
def build_diffuser(n_qubits: int) -> QuantumCircuit:
    diffuser = QuantumCircuit(n_qubits, name="Diffuser")
    diffuser.h(range(n_qubits))
    diffuser.x(range(n_qubits))
    diffuser.h(n_qubits - 1)
    diffuser.mcx(list(range(n_qubits - 1)), n_qubits - 1)
    diffuser.h(n_qubits - 1)
    diffuser.x(range(n_qubits))
    diffuser.h(range(n_qubits))
    return diffuser

def build_grover_circuit(n_qubits:int, target: str, iterations: int) -> QuantumCircuit:
    qc = QuantumCircuit(n_qubits, n_qubits) # qubits, classical bits

    # Start in equal superposition
    qc.h(range(n_qubits))

    oracle_gate = build_oracle(n_qubits, target).to_gate()
    diffuser_gate = build_diffuser(n_qubits).to_gate()

    for _ in range(iterations):
        qc.append(oracle_gate, range(n_qubits))
        qc.append(diffuser_gate, range(n_qubits))
    qc.measure(range(n_qubits), range(n_qubits))
    return qc

def optimal_iterations(n_qubits: int) -> int:
    N = 2 ** n_qubits
    return max(1, round((math.pi / 4) * math.sqrt(N))) # pi / 4 * sqrt of N

def main():
    parser = argparse.ArgumentParser(
        description="Find a secret PIN using Grover's algorithm."
    )
    parser.add_argument(
        "--pin", type=int, help="Secret PIN as a deciaml number."
    )
    parser.add_argument(
        "--random", action="store_true", help="Pick a random secret PIN instead."
    )
    parser.add_argument(
        "--bits", type=int, default=4, help="Number of measurement shots."
    )
    parser.add_argument(
        "--shots", type=int, default=1024, help="Number of measurement shots."
    )
    args = parser.parse_args()
    n_qubits = args.bits
    max_pin = 2 ** n_qubits -1
    if args.random:
        pin = random.randint(0, max_pin)
    elif args.pin is not None:
        if not (0 <= args.pin <= max_pin):
            parser.error(f"--pin must be between 0 and {max_pin} for {n_qubits} bits.")
        pin = args.pin
    else:
        parser.error("Provide --pin <number> or use --random.")

    target = format(pin, f"0{n_qubits}b")
    iterations = optimal_iterations(n_qubits)

    print(f"Secret PIN (hidden from the algorithm): {pin} -> bitstring {target}")
    print(f"Search space size: {2 ** n_qubits} possibilities")
    print(f"Grover iterations used: {iterations}")

    qc = build_grover_circuit(n_qubits, target, iterations)
    sim  = AerSimulator()
    qc_transpiled = transpile(qc, sim)
    result = sim.run(qc_transpiled, shots=args.shots).result()
    counts = result.get_counts()

    best_guess = max(counts, key=counts.get)
    best_guess_decimal = int(best_guess, 2)
    confidence = counts[best_guess] / args.shots * 100

    print("\n--- Results ---")
    print(f"Grover's found PIN: {best_guess_decimal} (bitstring {best_guess})")
    print(f"Confidence: {confidence:.1f}% of {args.shots} shots")
    correct = best_guess_decimal == pin

    print(f"Correct? {'YES' if correct else 'NO -- try more shots or check circuit'}")
    classical_avg_tries = (2 ** n_qubits) / 2
    print("\n--- Classical comparison ---")
    print(f"Classical brute force would need ~{classical_avg_tries:.0f} tries on average")
    print(f"Grover's needed {iterations} oracle calls")

if __name__ == "__main__":
    main()

