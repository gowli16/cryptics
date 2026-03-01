# ============================================================
# SIMULATOR BACKEND MODULE
# Centralized Qiskit Aer Simulator for BB84 Project
# ============================================================

from qiskit_aer import AerSimulator

# Create ONE global simulator instance
_simulator = AerSimulator()


def run_circuit(circuit, shots=1, noise_model=None, memory=True):
    """
    Executes a quantum circuit using the global AerSimulator.

    Parameters:
        circuit      : QuantumCircuit object
        shots        : Number of executions (default=1)
        noise_model  : Optional Qiskit NoiseModel
        memory       : Whether to return individual shot results

    Returns:
        result.get_memory()  -> list of measurement outcomes
        OR
        result.get_counts()  -> dictionary of counts (if memory=False)
    """

    job = _simulator.run(
        circuit,
        shots=shots,
        noise_model=noise_model,
        memory=memory
    )

    result = job.result()

    if memory:
        return result.get_memory()
    else:
        return result.get_counts()