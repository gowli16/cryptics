"""
BB84 Quantum Key Distribution - Master Simulation File
Amrita QuantumLeap Bootcamp 2026 | Quantum Cryptography
"""

import numpy as np
import random
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, pauli_error


# ============================================================
# CONFIGURATION
# ============================================================
NUM_BITS = 200
SECURITY_THRESHOLD = 0.11


# ============================================================
# CORE PROTOCOL FUNCTIONS
# ============================================================


def prepare_qubit(bit_value: int, basis: int) -> QuantumCircuit:
    qc = QuantumCircuit(1, 1)
    if bit_value == 1:
        qc.x(0)
    if basis == 1:


        
        qc.h(0)
    return qc

def measure_qubit(circuit: QuantumCircuit, measurement_basis: int, noise_model=None) -> int:
    meas_circuit = circuit.copy()
    if measurement_basis == 1:
        meas_circuit.h(0)
    meas_circuit.measure(0, 0)
    
    simulator = AerSimulator()
    result = simulator.run(meas_circuit, shots=1, memory=True, noise_model=noise_model).result()
    return int(result.get_memory()[0])

def create_depolarizing_noise(p):
    noise_model = NoiseModel()
    error = depolarizing_error(p, 1)
    noise_model.add_all_qubit_quantum_error(error, ['x', 'h'])
    return noise_model

def run_bb84_simulation(num_bits=200, eve_intercept_probability=0.0, noise_model=None):
    alice_bits = np.random.randint(0, 2, num_bits)
    alice_bases = np.random.randint(0, 2, num_bits)
    bob_bases = np.random.randint(0, 2, num_bits)
    
    bob_results = []
    
    for i in range(num_bits):
        # Alice prepares
        qc = prepare_qubit(alice_bits[i], alice_bases[i])
        
        # Eve intercepts
        if random.random() < eve_intercept_probability:
            eve_basis = random.randint(0, 1)
            eve_bit = measure_qubit(qc.copy(), eve_basis, noise_model)
            qc = prepare_qubit(eve_bit, eve_basis)
            
        # Bob measures
        bob_bit = measure_qubit(qc, bob_bases[i], noise_model)
        bob_results.append(bob_bit)
        
    # Sifting
    sifted_alice = []
    sifted_bob = []
    for i in range(num_bits):
        if alice_bases[i] == bob_bases[i]:
            sifted_alice.append(alice_bits[i])
            sifted_bob.append(bob_results[i])
            
    # QBER
    errors = sum(a != b for a, b in zip(sifted_alice, sifted_bob))
    qber = errors / len(sifted_alice) if len(sifted_alice) > 0 else 0
    efficiency = len(sifted_alice) / num_bits if num_bits > 0 else 0
    
    return qber, efficiency, sifted_alice, sifted_bob


# ============================================================
# EXPERIMENT 1: BASELINE (MEMBER 1)
# ============================================================
def run_baseline_experiment():
    print("\n" + "="*50)
    print(" EXPERIMENT 1: BASELINE BB84 (CLEAN CHANNEL)")
    print("="*50)
    
    qber, efficiency, alice_key, bob_key = run_bb84_simulation(num_bits=NUM_BITS)
    
    print(f"Bits Sent:       {NUM_BITS}")
    print(f"Sifted Key Len:  {len(alice_key)}")
    print(f"Efficiency:      {efficiency:.2%}")
    print(f"QBER:            {qber:.4f}")
    
    if qber < SECURITY_THRESHOLD:
        print("[SUCCESS] Channel is Secure. No eavesdropping detected.")
    else:
        print("[ERROR] Channel is compromised.")
    
    # Print sample keys
    print(f"\nAlice's Key (first 10): {alice_key[:10]}")
    print(f"Bob's Key   (first 10): {bob_key[:10]}")


# ============================================================
# EXPERIMENT 2: EVE'S ATTACK (MEMBER 2)
# ============================================================
def run_eve_experiment():
    print("\n" + "="*50)
    print(" EXPERIMENT 2: INTERCEPT-RESEND ATTACK")
    print("="*50)
    
    eve_levels = np.linspace(0, 1, 6)
    qber_results = []
    
    for eve_prob in eve_levels:
        qber, eff, _, _ = run_bb84_simulation(num_bits=NUM_BITS, eve_intercept_probability=eve_prob)
        qber_results.append(qber)
        
        print(f"Eve Interception: {int(eve_prob*100)}% | QBER: {qber:.4f}")
        
    # Plotting
    plt.figure()
    plt.plot(eve_levels * 100, np.array(qber_results) * 100, marker='o', color='purple')
    plt.axhline(y=SECURITY_THRESHOLD * 100, linestyle='--', color='red', label="Security Threshold (11%)")
    plt.xlabel("Eve Interception Probability (%)")
    plt.ylabel("QBER (%)")
    plt.title("Exp 2: QBER vs. Eavesdropper Presence")
    plt.legend()
    plt.grid(True, alpha=0.3)
    print("\n--> [SYSTEM] Graph displayed. Close the graph window to continue to Experiment 3...")
    plt.show()


# ============================================================
# EXPERIMENT 3: CHANNEL NOISE (MEMBER 3)
# ============================================================
def run_noise_experiment():
    print("\n" + "="*50)
    print(" EXPERIMENT 3: DEPOLARIZING NOISE CHANNEL")
    print("="*50)
    
    noise_levels = np.linspace(0, 0.2, 6)
    qber_results = []
    
    for noise_prob in noise_levels:
        noise_model = create_depolarizing_noise(noise_prob)
        qber, eff, _, _ = run_bb84_simulation(num_bits=NUM_BITS, noise_model=noise_model)
        qber_results.append(qber)
        
        print(f"Noise Level: {int(noise_prob*100)}% | QBER: {qber:.4f}")
        
    # Plotting
    plt.figure()
    plt.plot(noise_levels * 100, np.array(qber_results) * 100, marker='s', color='#3498db')
    plt.axhline(y=SECURITY_THRESHOLD * 100, linestyle='--', color='red', label="Security Threshold (11%)")
    plt.xlabel("Depolarizing Noise Probability (%)")
    plt.ylabel("QBER (%)")
    plt.title("Exp 3: QBER vs. Quantum Channel Noise")
    plt.legend()
    plt.grid(True, alpha=0.3)
    print("\n--> [SYSTEM] Graph displayed. Close the graph window to continue to Experiment 4...")
    plt.show()


# ============================================================
# EXPERIMENT 4: COMBINED
# ============================================================
def run_combined_experiment():
    print("\n" + "="*50)
    print(" EXPERIMENT 4: COMBINED EVE & NOISE ANALYSIS")
    print("="*50)
    
    eve_levels = np.linspace(0, 1, 6)
    noise_scenarios = [0.0, 0.02, 0.05]
    
    plt.figure()
    for noise in noise_scenarios:
        noise_model = create_depolarizing_noise(noise) if noise > 0 else None
        qber_values = []
        for eve_prob in eve_levels:
            qber, _, _, _ = run_bb84_simulation(num_bits=NUM_BITS, eve_intercept_probability=eve_prob, noise_model=noise_model)
            qber_values.append(qber)
        plt.plot(eve_levels * 100, np.array(qber_values) * 100, marker='o', label=f"Natural Noise = {int(noise*100)}%")
        
    plt.axhline(y=SECURITY_THRESHOLD * 100, linestyle='--', color='red', label="Security Threshold (11%)")
    plt.xlabel("Eve Interception Probability (%)")
    plt.ylabel("QBER (%)")
    plt.title("Exp 4: QBER vs Eve under Natural Channel Noise")
    plt.legend()
    plt.grid(True, alpha=0.3)
    print("\n--> [SYSTEM] Graph displayed. Close the graph window to complete the run.")
    plt.show()


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("  AMRITA QUANTUMLEAP BOOTCAMP 2026")
    print("  TEAM BB84 SIMULATION SUITE - MASTER EXECUTOR")
    print("#"*60)
    
    run_baseline_experiment()
    run_eve_experiment()
    run_noise_experiment()
    run_combined_experiment()
    
    print("\n[SUCCESS] All experiments completed successfully. Great job team!")
