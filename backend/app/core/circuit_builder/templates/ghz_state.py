# app/core/circuit_builder/templates/ghz_state.py
from qiskit import QuantumCircuit

def create_ghz_state(num_qubits=3):
    """
    Create a GHZ state circuit: |GHZ⟩ = (|00...0⟩ + |11...1⟩)/√2
    Default is creating a 3-qubit GHZ state
    """
    if num_qubits < 3:
        raise ValueError("GHZ state typically requires at least 3 qubits")
    
    qc = QuantumCircuit(num_qubits, num_qubits)
    
    # Apply Hadamard to the first qubit
    qc.h(0)
    
    # Apply CNOT gates to entangle all qubits
    for i in range(num_qubits-1):
        qc.cx(i, i+1)
    
    # Measure qubits
    for i in range(num_qubits):
        qc.measure(i, i)
    
    return qc