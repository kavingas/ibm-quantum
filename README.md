# IBM Quantum

Experiments with IBM Quantum hardware using Qiskit. Includes a Hello World circuit notebook and a quantum random lottery number generator.

## Requirements

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager
- IBM Quantum account (free at [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com))

## Setup

1. **Install dependencies**

   ```bash
   uv sync
   ```

2. **Configure credentials**

   Copy `.env.sample` to `.env` and fill in your credentials:

   ```bash
   cp .env.sample .env
   ```

   | Variable   | Where to find it |
   |------------|-----------------|
   | `TOKEN`    | [quantum.cloud.ibm.com](https://quantum.cloud.ibm.com) → top-right menu → API key |
   | `INSTANCE` | [quantum.cloud.ibm.com/instances](https://quantum.cloud.ibm.com/instances) → hover the CRN and copy |

## Lottery number generator

Generates truly random lottery numbers using quantum superposition. Each qubit is placed in an equal superposition of |0⟩ and |1⟩ via a Hadamard gate — measuring it collapses it to 0 or 1 with exactly 50/50 probability, guaranteed by quantum mechanics.

**Format:** 4 sets × (7 primary numbers from 1–35 + 1 bonus from 1–20)

```bash
uv run python lottery.py
```

Example output:

```
╔══════════════════════════════════════╗
║   Quantum Lottery Number Generator   ║
╚══════════════════════════════════════╝

Connecting to IBM Quantum…
Available backends: ['ibm_fez', 'ibm_marrakesh', 'ibm_kingston']

Trying ibm_fez (156 qubits)…
Job ID  : d8lq1jj2d42s73cboli0
Random bits collected: 1050

────────────────────────────────────────────
  Primary numbers (1–35)          Bonus
────────────────────────────────────────────
  Set 1:  3   7   9  12  14  21  27    [ 2]
  Set 2:  2  17  19  20  27  33  34    [14]
  Set 3:  1   2  15  16  17  18  22    [17]
  Set 4:  7   9  15  18  20  22  33    [10]
────────────────────────────────────────────
```

If all hardware backends are unavailable, the script automatically falls back to a local quantum simulator (`FakeManilaV2`).

### How the randomness works

1. A 7-qubit circuit applies a Hadamard gate to each qubit and measures all of them.
2. 150 shots are run → 1,050 random bits.
3. Bits are consumed in chunks using rejection sampling to ensure a perfectly uniform distribution (no modulo bias).

## Hello World notebook

Follows the official IBM Quantum [Hello World guide](https://quantum.cloud.ibm.com/docs/en/guides/hello-world). Demonstrates:

- Bell state preparation
- Transpilation for real hardware
- Running with `EstimatorV2`
- Scaling to a 100-qubit GHZ state

```bash
uv run jupyter notebook hello-world.ipynb
```
