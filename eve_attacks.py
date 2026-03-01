"""
BB84 Quantum Key Distribution Simulation
-----------------------------------------

This implementation models:

1. Alice preparing qubits in Z/X basis
2. Eve performing intercept-resend attack (probabilistic)
3. Quantum channel depolarizing noise
4. Bob measuring qubits
5. QBER calculation
6. Security threshold decision (11%)

Executed using Qiskit Aer simulator.
"""

import numpy as np
import random
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit_aer.noise import NoiseModel, depolarizing_error


# ============================================================
# CONFIGURATION PARAMETERS
# ============================================================

NUM_BITS = 200                 # Number of transmitted qubits
NOISE_PROBABILITY = 0.02       # Depolarizing channel noise
SECURITY_THRESHOLD = 0.11      # BB84 theoretical security limit


# ============================================================
# QUBIT PREPARATION (ALICE)
# ============================================================

def prepare_qubit(bit_value: int, basis: int) -> QuantumCircuit:
    """
    Prepare a single qubit according to BB84 rules.

    basis = 0 → Z basis
    basis = 1 → X basis
    """

    qc = QuantumCircuit(1, 1)

    # Encode classical bit
    if bit_value == 1:
        qc.x(0)

    # Change basis if needed
    if basis == 1:
        qc.h(0)

    return qc


# ============================================================
# QUBIT MEASUREMENT
# ============================================================

def measure_qubit(circuit: QuantumCircuit,
                  measurement_basis: int,
                  noise_model=None) -> int:
    """
    Measure qubit in chosen basis using Aer simulator.
    """

    # Rotate measurement basis if X
    if measurement_basis == 1:
        circuit.h(0)

    circuit.measure(0, 0)

    simulator = Aer.get_backend("aer_simulator")

    result = simulator.run(
        circuit,
        shots=1,
        memory=True,
        noise_model=noise_model
    ).result()

    return int(result.get_memory()[0])


# ============================================================
# QUANTUM CHANNEL NOISE MODEL
# ============================================================

def create_depolarizing_noise_model(noise_probability: float) -> NoiseModel:
    """
    Create depolarizing noise model for 1-qubit gates.
    """

    noise_model = NoiseModel()

    dep_error = depolarizing_error(noise_probability, 1)

    noise_model.add_all_qubit_quantum_error(dep_error, ['x', 'h'])

    return noise_model


# ============================================================
# BB84 PROTOCOL SIMULATION
# ============================================================

def run_bb84(eve_intercept_probability: float,
             noise_probability: float,
             num_bits: int):

    alice_bits = np.random.randint(0, 2, num_bits)
    alice_bases = np.random.randint(0, 2, num_bits)
    bob_bases = np.random.randint(0, 2, num_bits)

    noise_model = None
    if noise_probability > 0:
        noise_model = create_depolarizing_noise_model(noise_probability)

    bob_results = []

    for i in range(num_bits):

        # ---------------------------
        # Step 1: Alice prepares qubit
        # ---------------------------
        qc = prepare_qubit(alice_bits[i], alice_bases[i])

        # ---------------------------
        # Step 2: Eve (Intercept-Resend)
        # ---------------------------
        if random.random() < eve_intercept_probability:
            eve_basis = random.randint(0, 1)
            eve_bit = measure_qubit(qc.copy(), eve_basis, noise_model)

            # Eve re-prepares qubit
            qc = prepare_qubit(eve_bit, eve_basis)

        # ---------------------------
        # Step 3: Bob measures
        # ---------------------------
        bob_bit = measure_qubit(qc, bob_bases[i], noise_model)
        bob_results.append(bob_bit)

    # ---------------------------
    # Basis sifting
    # ---------------------------
    sifted_alice = []
    sifted_bob = []

    for i in range(num_bits):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_results[i])

    # ---------------------------
    # QBER Calculation
    # ---------------------------
    errors = sum(a != b for a, b in zip(sifted_alice, sifted_bob))
    qber = errors / len(sifted_alice) if len(sifted_alice) > 0 else 0

    # Efficiency (key rate)
    efficiency = len(sifted_alice) / num_bits

    return qber, efficiency


# ============================================================
# MAIN ANALYSIS
# ============================================================

if __name__ == "__main__":

    print("\n==============================")
    print(" BB84 Quantum Circuit Analysis")
    print("==============================\n")

    eve_levels = np.linspace(0, 1, 6)
    qber_results = []

    for eve_prob in eve_levels:

        qber, efficiency = run_bb84(
            eve_intercept_probability=eve_prob,
            noise_probability=NOISE_PROBABILITY,
            num_bits=NUM_BITS
        )

        qber_results.append(qber)

        print(f"Eve Interception: {int(eve_prob*100)}%")
        print(f"QBER: {qber:.4f}")
        print(f"Key Efficiency: {efficiency:.4f}")

        if qber > SECURITY_THRESHOLD:
            print("→ Protocol Aborted (Security Compromised)")
            print("⚠ Attack detectable at this interception rate\n")
    else:
            print("→ Secure Key Can Be Generated\n")
    # ============================================================
# Theoretical vs Experimental Validation
# ============================================================

    print("\n--- Theoretical Validation ---")

# Run full interception case
    full_qber, _ = run_bb84(
        eve_intercept_probability=1.0,
        noise_probability=0.0,
        num_bits=NUM_BITS)

    print("Expected QBER under full intercept ≈ 25%")
    print(f"Observed QBER: {full_qber:.4f}")
    # Plot Results
    plt.figure()
    plt.plot(eve_levels * 100, np.array(qber_results) * 100)
    plt.axhline(y=SECURITY_THRESHOLD * 100,
                linestyle='--',
                label="Security Threshold (11%)")

    plt.xlabel("Eve Interception Probability (%)")
    plt.ylabel("QBER (%)")
    plt.title("BB84 Security Analysis (Quantum Circuit Model)")
    plt.legend()
    plt.show()