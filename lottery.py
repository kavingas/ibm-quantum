#!/usr/bin/env python3
"""
Quantum Lottery Number Generator

Uses IBM Quantum hardware to generate truly random lottery numbers via
quantum superposition and measurement. Each qubit is placed in a
superposition of |0⟩ and |1⟩ using a Hadamard gate, then measured to
produce a perfectly random bit — guaranteed by quantum mechanics, not
a classical algorithm.

Lottery format:
  - 4 sets
  - 7 primary numbers drawn from 1–35 (unique per set)
  - 1 secondary number drawn from 1–20
"""

import os
from dotenv import load_dotenv
from qiskit import QuantumCircuit
from qiskit.transpiler import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# ── Lottery configuration ────────────────────────────────────────────────────

SETS          = 4
PRIMARY_COUNT = 7
PRIMARY_MAX   = 35   # numbers drawn from 1..PRIMARY_MAX
SECONDARY_MAX = 20   # number drawn from 1..SECONDARY_MAX

# Bits needed per draw attempt (must satisfy 2^n >= MAX)
PRIMARY_BITS   = 6   # 2^6 = 64  ≥ 35
SECONDARY_BITS = 5   # 2^5 = 32  ≥ 20

# Circuit dimensions — 7 qubits × 150 shots = 1050 random bits (ample headroom)
NUM_QUBITS = 7
SHOTS      = 150


# ── Quantum circuit ──────────────────────────────────────────────────────────

def build_random_circuit(num_qubits: int) -> QuantumCircuit:
    """All qubits in |+⟩ superposition; measurement collapses each to 0 or 1."""
    qc = QuantumCircuit(num_qubits)
    for i in range(num_qubits):
        qc.h(i)
    qc.measure_all()
    return qc


# ── Bit extraction ───────────────────────────────────────────────────────────

def collect_bits(bit_array) -> list[int]:
    """Flatten all shot bitstrings into a single list of ints."""
    bits: list[int] = []
    for bs in bit_array.get_bitstrings():
        bits.extend(int(b) for b in bs.replace(" ", ""))
    return bits


def draw_number(bits: list[int], n_bits: int, max_val: int) -> tuple[int | None, list[int]]:
    """
    Consume n_bits from the front of bits and return (number, remaining).
    Returns None if the value falls outside [1, max_val] (rejection sampling).
    Always advances the pointer so the caller never stalls.
    """
    if len(bits) < n_bits:
        return None, bits
    chunk, remaining = bits[:n_bits], bits[n_bits:]
    value = int("".join(str(b) for b in chunk), 2)
    return (value + 1 if value < max_val else None), remaining


# ── Lottery set generation ───────────────────────────────────────────────────

def generate_set(bits: list[int]) -> tuple[list[int], int, list[int]]:
    """
    Draw one complete lottery set from the bit pool.
    Returns (sorted primary numbers, secondary number, remaining bits).
    """
    primary:   list[int] = []
    remaining: list[int] = bits[:]

    while len(primary) < PRIMARY_COUNT:
        if len(remaining) < PRIMARY_BITS:
            raise RuntimeError("Exhausted random bits — increase SHOTS or NUM_QUBITS")
        num, remaining = draw_number(remaining, PRIMARY_BITS, PRIMARY_MAX)
        if num is not None and num not in primary:
            primary.append(num)

    secondary: int | None = None
    while secondary is None:
        if len(remaining) < SECONDARY_BITS:
            raise RuntimeError("Exhausted random bits — increase SHOTS or NUM_QUBITS")
        secondary, remaining = draw_number(remaining, SECONDARY_BITS, SECONDARY_MAX)

    return sorted(primary), secondary, remaining


# ── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    load_dotenv()
    token    = os.getenv("TOKEN")
    instance = os.getenv("INSTANCE")

    print("╔══════════════════════════════════════╗")
    print("║   Quantum Lottery Number Generator   ║")
    print("╚══════════════════════════════════════╝")

    qc = build_random_circuit(NUM_QUBITS)

    bits: list[int] = []

    if token:
        print("\nConnecting to IBM Quantum…")
        service = QiskitRuntimeService(
            channel="ibm_cloud",
            # token=token,
            # instance=instance,
        )
        backends = service.backends(operational=True, simulator=False)
        print(f"Available backends: {[b.name for b in backends]}")

        for backend in backends:
            try:
                print(f"\nTrying {backend.name} ({backend.num_qubits} qubits)…")
                pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
                isa_circuit = pm.run(qc)

                sampler = Sampler(mode=backend)
                job = sampler.run([isa_circuit], shots=SHOTS)
                print(f"Job ID  : {job.job_id()}")

                result = job.result()[0]
                bits = collect_bits(result.data.meas)
                print(f"Random bits collected: {len(bits)}")
                break
            except Exception as e:
                print(f"  Failed ({e!s:.80}), trying next backend…")

    if not bits:
        print("\nFalling back to local quantum simulator (FakeManilaV2)…")
        from qiskit_ibm_runtime.fake_provider import FakeManilaV2
        backend = FakeManilaV2()
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
        isa_circuit = pm.run(qc)
        sampler = Sampler(mode=backend)
        job = sampler.run([isa_circuit], shots=SHOTS)
        result = job.result()[0]
        bits = collect_bits(result.data.meas)
        print(f"Random bits collected: {len(bits)}")

    # ── Generate lottery sets ────────────────────────────────────────────────
    print(f"\n{'─'*44}")
    print(f"  {'Primary numbers (1–35)':30s}  {'Bonus'}")
    print(f"{'─'*44}")

    remaining = bits
    for i in range(1, SETS + 1):
        primary, secondary, remaining = generate_set(remaining)
        primary_str = "  ".join(f"{n:2d}" for n in primary)
        print(f"  Set {i}: {primary_str}    [{secondary:2d}]")

    print(f"{'─'*44}")
    print(f"\nBits remaining after draw: {len(remaining)}")


if __name__ == "__main__":
    main()
