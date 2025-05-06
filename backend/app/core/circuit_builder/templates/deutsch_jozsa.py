# app/core/circuit_builder/templates/deutsch_jozsa.py
from qiskit import QuantumCircuit

def create_deutsch_jozsa_circuit(num_qubits=3, oracle_type='balanced'):
    """
    Create a Deutsch-Jozsa algorithm circuit.
    
    Args:
        num_qubits (int): Number of qubits (excluding ancilla qubit).
        oracle_type (str): Type of oracle - 'constant' or 'balanced'.
        
    Returns:
        QuantumCircuit: A Qiskit circuit implementing the Deutsch-Jozsa algorithm.
    """
    # We need n+1 qubits, where the last qubit is the ancilla
    total_qubits = num_qubits + 1
    
    # Create quantum circuit with n+1 qubits and n measurement bits
    qc = QuantumCircuit(total_qubits, num_qubits)
    
    # Initialize the ancilla qubit in state |1⟩
    qc.x(num_qubits)
    
    # Apply Hadamard to all qubits
    for qubit in range(total_qubits):
        qc.h(qubit)
    
    qc.barrier()
    
    # Implement the oracle
    if oracle_type == 'constant':
        # For constant function, do nothing (constant 0)
        # Or apply X to ancilla (constant 1)
        pass
    else:  # 'balanced'
        # For balanced function, create a balanced oracle
        # Here's a simple balanced oracle: CNOT gates from each input qubit to the ancilla
        for qubit in range(num_qubits):
            qc.cx(qubit, num_qubits)
    
    qc.barrier()
    
    # Apply Hadamard to input qubits
    for qubit in range(num_qubits):
        qc.h(qubit)
    
    # Measure the input qubits
    for qubit in range(num_qubits):
        qc.measure(qubit, qubit)
    
    return qc