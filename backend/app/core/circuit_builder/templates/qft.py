# app/core/circuit_builder/templates/qft.py
from qiskit import QuantumCircuit
import numpy as np

def create_qft_circuit(num_qubits=3):
    """
    Create a Quantum Fourier Transform circuit.
    
    Args:
        num_qubits (int): Number of qubits for the QFT.
        
    Returns:
        QuantumCircuit: A Qiskit circuit implementing the QFT.
    """
    qc = QuantumCircuit(num_qubits)
    
    # Implement QFT
    for i in range(num_qubits):
        qc.h(i)
        for j in range(i+1, num_qubits):
            # Add controlled phase rotations
            # The phase angle is 2π/2^(j-i+1)
            qc.cp(2*np.pi/2**(j-i+1), j, i)
    
    # Swap qubits (optional - to match standard QFT definition)
    for i in range(num_qubits//2):
        qc.swap(i, num_qubits-i-1)
    
    # Add measurements (optional)
    qc.measure_all()
    
    return qc