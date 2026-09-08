<h1 align="Center"> Grover's Algorithm PIN Finder 🔐 </h1>

<p align="center">
  <kbd>
    <img src="https://github.com/boydjawun/grovers-algorithm-pin-finder/blob/main/assets/grover-output.jpg" height="500" width="600">
  </kbd>
</p>

> A simple Qiskit demo that hides a PIN as a bit-string, then uses **Grover's algorithm** to amplify that state and measure it back.

| | |
|---|---|
| **Backend** | Qiskit Aer simulator (`AerSimulator`) |
| **Circuit** | `n` qubits + Hadamards + oracle + diffuser + measure |
| **SDK** | [Qiskit](https://qiskit.org) + [qiskit-aer](https://qiskit.github.io/qiskit-aer/) |
| **Language** | Python |

> Keep `--bits` small (about **3–8**). This is a local simulator demo, not a 200-bit PIN cracker.

---

## Features

- Pick a secret PIN with `--pin` or let the program pick one with `--random`
- Builds a Grover oracle that flips the phase of that PIN's bit-string
- Diffuser inverts amplitudes about the mean (makes the marked PIN more likely)
- Repeats oracle + diffuser about `π/4 * sqrt(N)` times
- Measures many shots and reports the most common guess
- Prints a classical vs Grover comparison (`N/2` guesses vs `O(sqrt(N))` oracle calls)

---

## Project structure
```
grovers-algorithm-pin-finder/
├── grover-pin-finder.py    # Oracle, diffuser, Grover loop, and CLI
└── README.md
```

---

## Quick start

### Prerequisites

- Python 3.8+
- Qiskit + Aer: ```pip install -U qiskit qiskit-aer```


### Run
> Be sure to keep the bits size in the 3-8 bit range for the simulator

```python grover-pin-finder.py --pin 14 --bits 4 --shots 1024```

```python grover-pin-finder.py --random --bits 4 --shots 1024```

```python grover-pin-finder.py -h```

| Flag | Meaning | Example |
|---|---|---|
| `--pin` | Secret PIN as a decimal number | `--pin 14` |
| `--random` | Pick a random PIN in range | `--random` |
| `--bits` | Number of qubits / PIN width | `--bits 4` |
| `--shots` | How many times to measure | `--shots 1024` |
| `-h` | Show help and exit | `-h` |

---

## What each part of the code does

1. **`build_oracle`** — Marks the secret bit-string. `X` maps the target to `|11…1⟩`, `H`–`MCX`–`H` multiplies that state by `-1`, then `X` undoes the mapping.
2. **`build_diffuser`** — Inversion about the mean. Pushes the marked PIN up and the others down.
3. **`build_grover_circuit`** — Hadamards (all PINs at once) → repeat oracle + diffuser → measure.
4. **`optimal_iterations`** — `round((π / 4) * sqrt(N))`. For 4 bits this is **3**.
5. **`main` CLI** — Reads `--pin` / `--random` / `--bits` / `--shots`. No PIN flag → `Provide --pin <number> or use --random.`
6. **Simulate** — `AerSimulator` runs many shots. Most common bit-string is the guess.
7. **Compare** — Classical average is `N / 2` tries. Grover used `iterations` oracle calls.

---

## Circuit setup

```
qc = QuantumCircuit(n_qubits, n_qubits)
qc.h(range(n_qubits))

oracle_gate = build_oracle(n_qubits, target).to_gate()
diffuser_gate = build_diffuser(n_qubits).to_gate()

for _ in range(iterations):
    qc.append(oracle_gate, range(n_qubits))
    qc.append(diffuser_gate, range(n_qubits))

qc.measure(range(n_qubits), range(n_qubits))

sim = AerSimulator()
result = sim.run(transpile(qc, sim), shots=shots).result()
counts = result.get_counts()
```
