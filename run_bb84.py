"""
╔══════════════════════════════════════════════════════════════╗
║   BB84 Quantum Key Distribution — Core Implementation        ║
║   Amrita QuantumLeap Bootcamp 2026 | Quantum Cryptography    ║
║   Member 1: BB84 Protocol Core (Encoding, Measurement,       ║
║             Sifting, QBER)                                   ║
╚══════════════════════════════════════════════════════════════╝

BB84 Protocol Overview:
────────────────────────────────────────────────────────────────
Step 1 │ Alice generates n random bits and n random bases
Step 2 │ Alice encodes each bit into a qubit using her basis
Step 3 │ Alice sends qubits to Bob over a quantum channel
Step 4 │ Bob randomly chooses a basis and measures each qubit
Step 5 │ Alice & Bob publicly compare bases (not bits)
Step 6 │ They keep only bits where bases matched → Sifted Key
Step 7 │ They compare a small sample of sifted bits → QBER check
Step 8 │ If QBER < 11%, the key is secure; else abort

Basis Encoding Table:
────────────────────────────────────────────────────────────────
Bit │ Basis (Z=0) │ Basis (X=1)
 0  │    |0⟩      │    |+⟩  = H|0⟩
 1  │    |1⟩      │    |−⟩  = H|1⟩
────────────────────────────────────────────────────────────────
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


# ══════════════════════════════════════════════════════════════
# SECTION 1 — KEY GENERATION (Alice's random inputs)
# ══════════════════════════════════════════════════════════════

def generate_random_bits(n: int) -> list[int]:
    """
    Generate n random classical bits for Alice.
    These are the SECRET bits she wants to share with Bob.

    Args:
        n: Number of bits to generate

    Returns:
        List of 0s and 1s, e.g. [1, 0, 1, 1, 0, ...]

    Example:
        >>> bits = generate_random_bits(8)
        >>> print(bits)  # [1, 0, 0, 1, 1, 0, 1, 0]
    """
    return np.random.randint(0, 2, size=n).tolist()


def generate_random_bases(n: int) -> list[int]:
    """
    Generate n random basis choices.
    0 → Z basis (rectilinear:  |0⟩, |1⟩)
    1 → X basis (diagonal:     |+⟩, |−⟩)

    Both Alice and Bob independently call this function.
    The bases are NOT kept secret (shared publicly during sifting),
    but the bits themselves are never revealed.

    Args:
        n: Number of basis choices to generate

    Returns:
        List of 0s and 1s representing basis choices
    """
    return np.random.randint(0, 2, size=n).tolist()


# ══════════════════════════════════════════════════════════════
# SECTION 2 — ALICE'S ENCODING (Quantum Circuit Construction)
# ══════════════════════════════════════════════════════════════

def encode_single_qubit(bit: int, basis: int) -> QuantumCircuit:
    """
    Encodes ONE classical bit into a qubit using Alice's chosen basis.

    Encoding Rules:
    ┌─────┬───────┬─────────────────────────────────────────────┐
    │ Bit │ Basis │ State  │ Circuit Operations                  │
    ├─────┼───────┼────────┼─────────────────────────────────────┤
    │  0  │   Z   │  |0⟩   │ (none — default |0⟩ state)          │
    │  1  │   Z   │  |1⟩   │ X gate (bit flip)                   │
    │  0  │   X   │  |+⟩   │ H gate (superposition)              │
    │  1  │   X   │  |−⟩   │ X gate then H gate                  │
    └─────┴───────┴────────┴─────────────────────────────────────┘

    Why does this work?
    - In Z basis: |0⟩ and |1⟩ are orthogonal → perfectly distinguishable
    - In X basis: |+⟩ and |−⟩ are also orthogonal → also distinguishable
    - BUT measuring |+⟩ or |−⟩ in Z basis gives random result → security!

    Args:
        bit:   0 or 1 (Alice's secret bit)
        basis: 0 (Z basis) or 1 (X basis)

    Returns:
        QuantumCircuit with 1 qubit, 1 classical bit (not yet measured)
    """
    qc = QuantumCircuit(1, 1)  # 1 qubit, 1 classical bit

    # ── Encode the bit value ──
    if bit == 1:
        qc.x(0)   # X gate: |0⟩ → |1⟩  (Pauli-X = quantum NOT gate)

    # ── Encode the basis ──
    if basis == 1:
        qc.h(0)   # Hadamard: |0⟩ → |+⟩  or  |1⟩ → |−⟩

    # NOTE: No measurement here! The qubit is "in transit" to Bob.
    return qc


def encode_all_qubits(bits: list[int], bases: list[int]) -> list[QuantumCircuit]:
    """
    Encodes ALL of Alice's bits into quantum circuits.
    This is the full quantum channel transmission from Alice.

    Args:
        bits:  Alice's n random secret bits
        bases: Alice's n random basis choices

    Returns:
        List of n QuantumCircuits, each representing one qubit in transit

    Example:
        >>> alice_bits  = [0, 1, 0, 1]
        >>> alice_bases = [0, 0, 1, 1]
        >>> circuits = encode_all_qubits(alice_bits, alice_bases)
        # circuit[0] → |0⟩  (bit=0, Z-basis)
        # circuit[1] → |1⟩  (bit=1, Z-basis)
        # circuit[2] → |+⟩  (bit=0, X-basis)
        # circuit[3] → |−⟩  (bit=1, X-basis)
    """
    if len(bits) != len(bases):
        raise ValueError(f"bits length ({len(bits)}) must equal bases length ({len(bases)})")

    return [encode_single_qubit(bit, basis) for bit, basis in zip(bits, bases)]


# ══════════════════════════════════════════════════════════════
# SECTION 3 — BOB'S MEASUREMENT (Quantum Circuit Execution)
# ══════════════════════════════════════════════════════════════

def measure_single_qubit(circuit: QuantumCircuit, basis: int,
                          simulator: AerSimulator) -> int:
    """
    Bob measures ONE qubit in his randomly chosen basis.

    Measurement Rules:
    ┌───────────────┬──────────────────────────────────────────────┐
    │  Bob's Basis  │  What he does before measuring               │
    ├───────────────┼──────────────────────────────────────────────┤
    │  Z (basis=0)  │  Nothing — measures in computational basis   │
    │  X (basis=1)  │  Applies H gate first, then measures         │
    └───────────────┴──────────────────────────────────────────────┘

    Why apply H before measuring in X basis?
    - |+⟩ = H|0⟩,  so H|+⟩ = |0⟩  → Bob measures 0 ✓
    - |−⟩ = H|1⟩,  so H|−⟩ = |1⟩  → Bob measures 1 ✓
    - Without H, measuring |+⟩ gives 0 or 1 randomly (50/50) ✗

    What happens when bases DON'T match?
    - Alice sent in X basis, Bob measures in Z basis (or vice versa)
    - The result is purely random — 50% chance of error
    - These bits are DISCARDED during sifting

    Args:
        circuit:   Alice's encoded qubit circuit (not yet measured)
        basis:     Bob's measurement basis (0=Z, 1=X)
        simulator: AerSimulator instance (reused for efficiency)

    Returns:
        Measured bit: 0 or 1
    """
    # Copy circuit so we don't mutate Alice's original
    meas_circuit = circuit.copy()

    # ── Rotate to correct measurement basis ──
    if basis == 1:
        meas_circuit.h(0)   # Rotate from X basis to Z before measuring

    # ── Measure qubit → classical bit ──
    meas_circuit.measure(0, 0)

    # ── Run on simulator (1 shot = 1 measurement event) ──
    job = simulator.run(meas_circuit, shots=1)
    counts = job.result().get_counts()

    # counts looks like: {'0': 1} or {'1': 1}
    return int(list(counts.keys())[0])


def measure_all_qubits(circuits: list[QuantumCircuit],
                        bob_bases: list[int]) -> list[int]:
    """
    Bob measures ALL received qubits using his random basis choices.

    Reuses a single AerSimulator instance for performance.

    Args:
        circuits:   List of Alice's encoded qubit circuits
        bob_bases:  Bob's random basis choices (one per qubit)

    Returns:
        List of Bob's measured bits (0s and 1s)
    """
    simulator = AerSimulator()   # One simulator instance, reused for all shots
    return [
        measure_single_qubit(circuit, basis, simulator)
        for circuit, basis in zip(circuits, bob_bases)
    ]


# ══════════════════════════════════════════════════════════════
# SECTION 4 — SIFTING (Basis Reconciliation)
# ══════════════════════════════════════════════════════════════

def sift_keys(alice_bases: list[int], bob_bases: list[int],
              alice_bits: list[int], bob_bits: list[int]) -> tuple[list[int], list[int]]:
    """
    Sifting: Alice and Bob publicly compare their BASIS choices
    (over an authenticated classical channel) and keep ONLY the
    bits where they used the SAME basis.

    Why do we discard mismatched bases?
    - If Alice encoded in X basis but Bob measured in Z basis,
      Bob's result is random (quantum mechanics!) → useless
    - On average, ~50% of bits survive sifting

    Security Note:
    - Only BASES are revealed publicly, never the actual bits
    - An eavesdropper (Eve) gains zero information from basis disclosure

    Args:
        alice_bases: Alice's basis choices (list of 0s and 1s)
        bob_bases:   Bob's basis choices   (list of 0s and 1s)
        alice_bits:  Alice's original bits (kept secret until now)
        bob_bits:    Bob's measured bits

    Returns:
        Tuple of (alice_sifted_key, bob_sifted_key)
        Both lists contain only bits where bases matched.

    Example:
        Alice bits:   [1, 0, 1, 0, 1]
        Alice bases:  [0, 1, 0, 1, 0]
        Bob bases:    [0, 0, 0, 1, 1]   ← compare these
        Bob bits:     [1, 1, 1, 0, 0]
                       ↑        ↑        ← bases match at index 0, 3
        Alice sifted: [1, 0]
        Bob sifted:   [1, 0]   ← should match (no errors, no Eve)
    """
    alice_sifted = []
    bob_sifted   = []

    for i in range(len(alice_bases)):
        if alice_bases[i] == bob_bases[i]:   # Bases match!
            alice_sifted.append(alice_bits[i])
            bob_sifted.append(bob_bits[i])
        # If bases don't match → silently discard this bit

    return alice_sifted, bob_sifted


def sifting_efficiency(original_n: int, sifted_n: int) -> float:
    """
    Returns the fraction of bits that survived sifting.
    Theoretically ~50% (bases match half the time on average).

    Args:
        original_n: Total bits sent by Alice
        sifted_n:   Bits remaining after sifting

    Returns:
        Float between 0 and 1 (expect ~0.50)
    """
    return sifted_n / original_n if original_n > 0 else 0.0


# ══════════════════════════════════════════════════════════════
# SECTION 5 — QBER (Security Check)
# ══════════════════════════════════════════════════════════════

def calculate_qber(alice_key: list[int], bob_key: list[int],
                   sample_fraction: float = 1.0) -> float:
    """
    Calculates the Quantum Bit Error Rate (QBER).

    QBER = (number of mismatched bits) / (total compared bits)

    In practice, Alice and Bob reveal a SAMPLE of their sifted key
    publicly to estimate QBER, then discard those revealed bits.
    Here we default to comparing all bits (fine for simulation).

    Security Thresholds:
    ┌───────────────┬────────────────────────────────────────────┐
    │  QBER Value   │  Interpretation                            │
    ├───────────────┼────────────────────────────────────────────┤
    │  ~0%          │  Ideal channel, no Eve, no noise           │
    │  ~25%         │  Eve doing intercept-resend attack         │
    │  0–11%        │  Secure (errors correctable via QEC)       │
    │  > 11%        │  ABORT — channel compromised or too noisy  │
    └───────────────┴────────────────────────────────────────────┘

    The 11% threshold comes from information-theoretic analysis:
    above this rate, Eve could have gained more info than Alice
    and Bob can reconcile via privacy amplification.

    Args:
        alice_key:       Alice's sifted key bits
        bob_key:         Bob's sifted key bits
        sample_fraction: Fraction of sifted key to use for QBER estimation
                         (default=1.0 uses all bits — fine for simulation)

    Returns:
        Float QBER between 0.0 and 1.0
    """
    if not alice_key or not bob_key:
        raise ValueError("Cannot calculate QBER: empty key provided")
    if len(alice_key) != len(bob_key):
        raise ValueError(f"Key length mismatch: Alice={len(alice_key)}, Bob={len(bob_key)}")

    # Optionally use only a sample (as in real QKD)
    sample_size = max(1, int(len(alice_key) * sample_fraction))
    alice_sample = alice_key[:sample_size]
    bob_sample   = bob_key[:sample_size]

    errors = sum(a != b for a, b in zip(alice_sample, bob_sample))
    return errors / sample_size


def is_channel_secure(qber: float, threshold: float = 0.11) -> bool:
    """
    Returns True if QBER is below the security threshold.

    Args:
        qber:      Calculated QBER value
        threshold: Security cutoff (default 11% per BB84 theory)

    Returns:
        True if secure, False if channel should be abandoned
    """
    return qber < threshold


# ══════════════════════════════════════════════════════════════
# SECTION 6 — CIRCUIT VISUALIZATION (For presentation/report)
# ══════════════════════════════════════════════════════════════

def print_circuit_table():
    """
    Prints all 4 possible BB84 encoding circuits as text diagrams.
    Useful for understanding and for your report.
    """
    cases = [
        (0, 0, "|0⟩  (Z basis, bit=0)"),
        (1, 0, "|1⟩  (Z basis, bit=1)"),
        (0, 1, "|+⟩  (X basis, bit=0)"),
        (1, 1, "|−⟩  (X basis, bit=1)"),
    ]

    print("\n" + "═"*55)
    print("  BB84 Encoding Circuits — All 4 Possible States")
    print("═"*55)
    for bit, basis, label in cases:
        try:
            qc = encode_single_qubit(bit, basis)
            print(f"\n  ► {label}")
            print(qc.draw('text'))
        except Exception:
            pass

    print("═"*55)


def draw_circuit_to_file(bit: int, basis: int, filename: str):
    """
    Saves a single BB84 encoding circuit as a PNG image.
    Useful for your report and presentation slides.

    Args:
        bit:      0 or 1
        basis:    0 (Z) or 1 (X)
        filename: Output PNG path e.g. 'circuit_bit1_xbasis.png'
    """
    qc = encode_single_qubit(bit, basis)

    # Add a measurement so the full circuit is visible
    qc_with_meas = qc.copy()
    qc_with_meas.barrier()
    qc_with_meas.measure(0, 0)

    fig = qc_with_meas.draw('mpl')
    fig.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"  Circuit saved to: {filename}")


# ══════════════════════════════════════════════════════════════
# SECTION 7 — FULL PROTOCOL RUNNER
# ══════════════════════════════════════════════════════════════

def run_bb84_core(n_bits: int = 200, verbose: bool = True) -> dict:
    """
    Runs the complete BB84 core protocol from start to finish.
    This is the CLEAN version (no Eve, no noise) — the baseline.

    Other team members (Member 2: Eve, Member 3: Noise) will
    import encode_all_qubits() and measure_all_qubits() and
    inject their modifications between these two steps.

    Args:
        n_bits:  Number of qubits Alice sends
        verbose: Print step-by-step summary

    Returns:
        Dictionary with full protocol results
    """
    if verbose:
        print("\n" + "═"*55)
        print(f"  BB84 Core Protocol | n = {n_bits} bits")
        print("═"*55)

    # ── Step 1: Alice generates random bits and bases ──
    alice_bits  = generate_random_bits(n_bits)
    alice_bases = generate_random_bases(n_bits)
    bob_bases   = generate_random_bases(n_bits)

    if verbose:
        print(f"\n[Step 1] Alice's bits  (first 10): {alice_bits[:10]}")
        print(f"         Alice's bases (first 10): {alice_bases[:10]}")
        print(f"         Bob's bases   (first 10): {bob_bases[:10]}")

    # ── Step 2: Alice encodes qubits ──
    circuits = encode_all_qubits(alice_bits, alice_bases)

    if verbose:
        print(f"\n[Step 2] Alice encoded {n_bits} qubits into quantum circuits")
        # print circuit logic is fine if we remove the draw console
        # skipping print for console compatibility

    # ── Step 3: Bob measures qubits ──
    # (In a real system, qubits travel through a quantum channel here)
    bob_bits = measure_all_qubits(circuits, bob_bases)

    if verbose:
        print(f"\n[Step 3] Bob measured all qubits")
        print(f"         Bob's bits    (first 10): {bob_bits[:10]}")

    # ── Step 4: Sifting — compare bases publicly ──
    alice_key, bob_key = sift_keys(alice_bases, bob_bases, alice_bits, bob_bits)
    efficiency = sifting_efficiency(n_bits, len(alice_key))

    if verbose:
        print(f"\n[Step 4] Sifting complete")
        print(f"         Original bits:  {n_bits}")
        print(f"         Sifted key len: {len(alice_key)} ({efficiency:.1%} survived)")
        print(f"         Alice key (first 10): {alice_key[:10]}")
        print(f"         Bob key   (first 10): {bob_key[:10]}")

    # ── Step 5: QBER check ──
    qber   = calculate_qber(alice_key, bob_key)
    secure = is_channel_secure(qber)

    if verbose:
        print(f"\n[Step 5] QBER = {qber:.4f} ({qber*100:.2f}%)")
        if secure:
            print(f"         [SUCCESS] Channel is SECURE (QBER < 11%)")
            print(f"         [SUCCESS] Shared secret key established!")
        else:
            print(f"         [ERROR] Channel is COMPROMISED (QBER >= 11%)")
            print(f"         [ERROR] Aborting key exchange!")
        print("\n" + "═"*55)

    return {
        "n_bits":          n_bits,
        "alice_bits":      alice_bits,
        "alice_bases":     alice_bases,
        "bob_bases":       bob_bases,
        "bob_bits":        bob_bits,
        "alice_key":       alice_key,
        "bob_key":         bob_key,
        "sifted_length":   len(alice_key),
        "sifting_efficiency": efficiency,
        "qber":            qber,
        "secure":          secure,
    }


# ══════════════════════════════════════════════════════════════
# SECTION 8 — SELF TEST
# ══════════════════════════════════════════════════════════════

def run_self_tests():
    """
    Unit tests to verify all functions work correctly.
    Run this first to make sure your environment is set up.
    """
    print("\n" + "═"*55)
    print("  Running Self-Tests...")
    print("═"*55)

    # Test 1: Encoding
    qc = encode_single_qubit(0, 0)
    assert qc.num_qubits == 1, "Should have 1 qubit"
    print("  [SUCCESS] Test 1 Passed: encode_single_qubit (|0>)")

    qc = encode_single_qubit(1, 1)
    ops = [instr.operation.name for instr in qc.data]
    assert 'x' in ops and 'h' in ops, "bit=1, basis=1 should have X and H gates"
    print("  [SUCCESS] Test 2 Passed: encode_single_qubit (|-n> = XH|0>)")

    # Test 3: Sifting logic
    a_bases = [0, 1, 0, 1, 0]
    b_bases = [0, 0, 0, 1, 1]
    a_bits  = [1, 0, 1, 0, 1]
    b_bits  = [1, 1, 1, 0, 0]
    ak, bk  = sift_keys(a_bases, b_bases, a_bits, b_bits)
    assert ak == [1, 1, 0], f"Alice sifted key wrong: {ak}"
    assert bk == [1, 1, 0], f"Bob sifted key wrong: {bk}"
    print("  [SUCCESS] Test 3 Passed: sift_keys (correct basis matching)")

    # Test 4: QBER = 0 for identical keys
    key = [1, 0, 1, 0, 1, 1, 0]
    q   = calculate_qber(key, key)
    assert q == 0.0, f"QBER of identical keys should be 0, got {q}"
    print("  [SUCCESS] Test 4 Passed: QBER = 0 for identical keys")

    # Test 5: QBER = 1 for flipped keys
    key_a = [1, 1, 1, 1]
    key_b = [0, 0, 0, 0]
    q     = calculate_qber(key_a, key_b)
    assert q == 1.0, f"QBER of fully flipped keys should be 1.0, got {q}"
    print("  [SUCCESS] Test 5 Passed: QBER = 1.0 for completely flipped keys")

    # Test 6: Security threshold
    assert is_channel_secure(0.05)  == True,  "QBER 5%  should be secure"
    assert is_channel_secure(0.11)  == False, "QBER 11% should be insecure"
    assert is_channel_secure(0.25)  == False, "QBER 25% (Eve) should be insecure"
    print("  [SUCCESS] Test 6 Passed: Security threshold logic")

    print("\n  All tests passed! Environment is ready.")
    print("═"*55)


# ══════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════

if _name_ == "_main_":
    # Run self-tests first
    run_self_tests()

    # Print all 4 encoding circuits (ignoring unicode draw errors)
    print_circuit_table()

    # Run the full BB84 protocol
    results = run_bb84_core(n_bits=200, verbose=True)

    # ── Summary for quick verification ──
    print("\n  ── Quick Summary ──")
    print(f"  Bits sent:       {results['n_bits']}")
    print(f"  Sifted key len:  {results['sifted_length']}")
    print(f"  Sifting eff.:    {results['sifting_efficiency']:.1%}")
    print(f"  QBER:            {results['qber']:.4f}")
    print(f"  Secure:          {'YES [SUCCESS]' if results['secure'] else 'NO [ERROR]'}")

    # ── Show first 20 bits of final key ──
    print(f"\n  Alice's key: {results['alice_key'][:20]}")
    print(f"  Bob's key:   {results['bob_key'][:20]}")
    match = results['alice_key'][:20] == results['bob_key'][:20]
    print(f"  Keys match:  {'[SUCCESS] YES' if match else '[ERROR] NO'}")