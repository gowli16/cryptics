"""
Member 3: Quantum Channel Noise Modeling & Visualization
----------------------------------------------------------

This module analyzes how different quantum noise models
affect BB84 protocol security and efficiency.

Noise types implemented:
1. Depolarizing noise
2. Bit-flip noise
3. Phase-flip noise

Outputs:
- QBER vs Noise Probability
- Key Efficiency vs Noise
- Security threshold visualization
"""

import numpy as np
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit
from qiskit_aer import Aer
from qiskit_aer.noise import NoiseModel
from qiskit_aer.noise.errors import depolarizing_error, pauli_error


# ============================================================
# CONFIGURATION
# ============================================================

NUM_BITS = 200
SECURITY_THRESHOLD = 0.11


# ============================================================
# NOISE MODELS
# ============================================================

def create_depolarizing_noise(p):
    """
    Depolarizing noise:
    Qubit randomly replaced with mixed state.
    """
    noise_model = NoiseModel()
    error = depolarizing_error(p, 1)
    noise_model.add_all_qubit_quantum_error(error, ['x', 'h'])
    return noise_model


def create_bitflip_noise(p):
    """
    Bit-flip noise:
    |0> ↔ |1>
    """
    noise_model = NoiseModel()
    error = pauli_error([('X', p), ('I', 1 - p)])
    noise_model.add_all_qubit_quantum_error(error, ['x', 'h'])
    return noise_model


def create_phaseflip_noise(p):
    """
    Phase-flip noise:
    Adds phase error.
    """
    noise_model = NoiseModel()
    error = pauli_error([('Z', p), ('I', 1 - p)])
    noise_model.add_all_qubit_quantum_error(error, ['x', 'h'])
    return noise_model


# ============================================================
# BASIC BB84 (Noise Only)
# ============================================================

def prepare_qubit(bit, basis):
    qc = QuantumCircuit(1, 1)

    if bit == 1:
        qc.x(0)

    if basis == 1:
        qc.h(0)

    return qc


def measure_qubit(qc, basis, noise_model):
    if basis == 1:
        qc.h(0)

    qc.measure(0, 0)

    simulator = Aer.get_backend("aer_simulator")

    result = simulator.run(
        qc,
        shots=1,
        memory=True,
        noise_model=noise_model
    ).result()

    return int(result.get_memory()[0])


def run_noise_analysis(noise_model):

    alice_bits = np.random.randint(0, 2, NUM_BITS)
    alice_bases = np.random.randint(0, 2, NUM_BITS)
    bob_bases = np.random.randint(0, 2, NUM_BITS)

    bob_results = []

    for i in range(NUM_BITS):
        qc = prepare_qubit(alice_bits[i], alice_bases[i])
        bob_bit = measure_qubit(qc, bob_bases[i], noise_model)
        bob_results.append(bob_bit)

    # Sifting
    sifted_alice = []
    sifted_bob = []

    for i in range(NUM_BITS):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_results[i])

    errors = sum(a != b for a, b in zip(sifted_alice, sifted_bob))
    qber = errors / len(sifted_alice) if len(sifted_alice) > 0 else 0
    efficiency = len(sifted_alice) / NUM_BITS

    return qber, efficiency


# ============================================================
# VISUALIZATION
# ============================================================

if __name__ == "__main__":

    noise_levels = np.linspace(0, 0.2, 6)

    qber_depol = []
    qber_bitflip = []
    qber_phaseflip = []

    efficiency_values = []

    print("\n=== Noise Impact Analysis ===\n")

    for p in noise_levels:

        depol_model = create_depolarizing_noise(p)
        qber, efficiency = run_noise_analysis(depol_model)

        qber_depol.append(qber)
        efficiency_values.append(efficiency)

        print(f"Noise Probability: {p:.2f}")
        print(f"QBER: {qber:.4f}")
        print(f"Efficiency: {efficiency:.4f}")

        if qber > SECURITY_THRESHOLD:
            print("→ Security threshold exceeded\n")
        else:
            print("→ Secure region\n")

    # Plot QBER vs Noise
    plt.figure()
    plt.plot(noise_levels * 100, np.array(qber_depol) * 100)
    plt.axhline(y=SECURITY_THRESHOLD * 100,
                linestyle='--',
                label="Security Threshold (11%)")
    plt.xlabel("Noise Probability (%)")
    plt.ylabel("QBER (%)")
    plt.title("QBER vs Depolarizing Noise")
    plt.legend()
    plt.show()

    # Plot Efficiency vs Noise
    plt.figure()
    plt.plot(noise_levels * 100, efficiency_values)
    plt.xlabel("Noise Probability (%)")
    plt.ylabel("Key Efficiency")
    plt.title("Key Efficiency vs Noise")
    plt.show()
    # ============================================================
# QBER vs Eve under Different Noise Levels
# ============================================================

print("\n=== Combined Analysis: QBER vs Eve under Different Noise Levels ===\n")

eve_levels = np.linspace(0, 1, 6)
noise_scenarios = [0.0, 0.02, 0.05]  # 0%, 2%, 5%

plt.figure()

for noise in noise_scenarios:

    qber_values = []

    for eve_prob in eve_levels:
        qber, _ = run_bb84(
            eve_intercept_probability=eve_prob,
            noise_probability=noise,
            num_bits=NUM_BITS
        )
        qber_values.append(qber)

    plt.plot(
        eve_levels * 100,
        np.array(qber_values) * 100,
        label=f"Noise = {int(noise*100)}%"
    )

plt.axhline(
    y=SECURITY_THRESHOLD * 100,
    linestyle='--',
    label="Security Threshold (11%)"
)

plt.xlabel("Eve Interception Probability (%)")
plt.ylabel("QBER (%)")
plt.title("QBER vs Eve under Different Noise Levels")
plt.legend()
plt.show()