# app/core/circuit_builder/templates/bernstein_vazirani.py
from qiskit import QuantumCircuit

def create_bernstein_vazirani_circuit(num_qubits=3, secret_string=None):
    """
    Create a Bernstein-Vazirani algorithm circuit.
    
    Args:
        num_qubits (int): Number of qubits (excluding ancilla qubit).
        secret_string (str): Binary string representing the secret (e.g., '101').
                            If None, defaults to alternating 1s and 0s.
        
    Returns:
        QuantumCircuit: A Qiskit circuit implementing the Bernstein-Vazirani algorithm.
    """
    # If no secret string is provided, create one (alternating 1s and 0s)
    if secret_string is None:
        secret_string = ''.join(['1' if i % 2 == 0 else '0' for i in range(num_qubits)])
    
    # Convert to binary and ensure the right length
    secret_string = format(int(secret_string, 2), f'0{num_qubits}b')
    
    # We need n+1 qubits, where the last qubit is the ancilla
    total_qubits = num_qubits + 1
    
    # Create quantum circuit with n+1 qubits and n measurement bits
    qc = QuantumCircuit(total_qubits, num_qubits)
    
    # Initialize the ancilla qubit in state |1⟩
    qc.x(num_qubits)
    
    # Apply Hadamard gates to all qubits
    for qubit in range(total_qubits):
        qc.h(qubit)
    
    qc.barrier()
    
    # Implement the oracle based on the secret string
    for qubit, bit in enumerate(secret_string):
        if bit == '1':
            qc.cx(qubit, num_qubits)
    
    qc.barrier()
    
    # Apply Hadamard gates to the input qubits
    for qubit in range(num_qubits):
        qc.h(qubit)
    
    # Measure the input qubits
    for qubit in range(num_qubits):
        qc.measure(qubit, qubit)
    
    return qc