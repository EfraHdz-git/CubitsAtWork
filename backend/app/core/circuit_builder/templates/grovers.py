# app/core/circuit_builder/templates/grovers.py
from qiskit import QuantumCircuit
import numpy as np

def create_grovers_circuit(num_qubits=3, marked_state=None):
    """
    Create a Grover's algorithm circuit.
    
    Args:
        num_qubits (int): Number of qubits.
        marked_state (str): Binary string representing the marked state (e.g., '101').
                           If None, defaults to all 1s.
                           
    Returns:
        QuantumCircuit: A Qiskit circuit implementing Grover's algorithm.
    """
    # If no marked state is provided, default to all 1s
    if marked_state is None:
        marked_state = '1' * num_qubits
    
    # Convert to binary and ensure the right length
    marked_state = format(int(marked_state, 2), f'0{num_qubits}b')
    
    # Calculate the optimal number of iterations
    iterations = int(np.floor(np.pi/4 * np.sqrt(2**num_qubits)))
    
    # Create a circuit with num_qubits qubits
    qc = QuantumCircuit(num_qubits, num_qubits)
    
    # Initialize: Apply Hadamard to all qubits
    qc.h(range(num_qubits))
    
    # Perform Grover iterations
    for _ in range(iterations):
        # Phase Oracle: Mark the target state
        # We'll use a multi-controlled Z gate for this
        # For simplicity, we'll just add a barrier and comment
        qc.barrier()
        # In a real implementation, you would implement the oracle based on the marked state
        # Here we'll use a simple placeholder for illustration
        for qubit, bit in enumerate(marked_state):
            if bit == '0':
                qc.x(qubit)
        
        # Apply a multi-controlled Z gate (simplified representation)
        if num_qubits > 2:
            qc.h(num_qubits-1)
            qc.mct(list(range(num_qubits-1)), num_qubits-1)
            qc.h(num_qubits-1)
        else:
            qc.cz(0, 1)
        
        for qubit, bit in enumerate(marked_state):
            if bit == '0':
                qc.x(qubit)
        
        qc.barrier()
        
        # Diffusion operator
        qc.h(range(num_qubits))
        qc.x(range(num_qubits))
        
        # Apply multi-controlled Z
        if num_qubits > 2:
            qc.h(num_qubits-1)
            qc.mct(list(range(num_qubits-1)), num_qubits-1)
            qc.h(num_qubits-1)
        else:
            qc.cz(0, 1)
        
        qc.x(range(num_qubits))
        qc.h(range(num_qubits))
        
        qc.barrier()
    
    # Measure all qubits
    qc.measure(range(num_qubits), range(num_qubits))
    
    return qc