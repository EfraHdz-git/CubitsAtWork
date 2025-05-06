# app/core/circuit_builder/templates/teleportation.py (updated)
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

def create_teleportation_circuit():
    """
    Create a quantum teleportation circuit.
    
    Teleports the state of qubit 0 to qubit 2 using entanglement and classical communication.
    """
    # Create quantum registers
    qr = QuantumRegister(3, 'q')
    crz = ClassicalRegister(1, 'crz')
    crx = ClassicalRegister(1, 'crx') 
    
    # Create the circuit
    qc = QuantumCircuit(qr, crz, crx)
    
    # Step 1: Create the bell pair between qubits 1 and 2
    qc.h(qr[1])
    qc.cx(qr[1], qr[2])
    
    # Step 2: Sender operations - entangle qubit 0 (the state to teleport) with qubit 1
    qc.cx(qr[0], qr[1])
    qc.h(qr[0])
    
    # Step 3: Measure qubits 0 and 1
    qc.measure(qr[0], crz[0])
    qc.measure(qr[1], crx[0])
    
    # Step 4: Apply corrections on qubit 2 based on measurement outcomes
    # Corrected conditional syntax
    with qc.if_test((crx, 1)):  # Use with statement for conditional operations
        qc.x(qr[2])
    with qc.if_test((crz, 1)):
        qc.z(qr[2])
    
    return qc