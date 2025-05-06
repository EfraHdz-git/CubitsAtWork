# app/core/circuit_builder/templates/bell_state.py
from qiskit import QuantumCircuit

def create_bell_state(num_qubits=2):
    """
    Create a Bell state circuit.
    Default is using 2 qubits to create |Φ+⟩ = (|00⟩ + |11⟩)/√2
    """
    # Basic error checking
    if num_qubits < 2:
        raise ValueError("Bell state requires at least 2 qubits")
    
    # Create a quantum circuit with 2 qubits and 2 classical bits
    qc = QuantumCircuit(num_qubits, num_qubits)
    
    # Apply Hadamard to the first qubit
    qc.h(0)
    
    # Apply CNOT with control on the first qubit and target on the second
    qc.cx(0, 1)
    
    # Measure qubits
    for i in range(num_qubits):
        qc.measure(i, i)
    
    return qc