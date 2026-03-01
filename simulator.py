from qiskit_aer import AerSimulator

# Create one global simulator
simulator = AerSimulator()

def run_circuit(circuit, shots=1, noise_model=None):
    result = simulator.run(
        circuit,
        shots=shots,
        memory=True,
        noise_model=noise_model
    ).result()
    
    return result.get_memory()