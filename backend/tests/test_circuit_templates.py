from qiskit import Aer, execute
from app.core.nlp_processor.intent_parser import CircuitIntent, CircuitType
from app.core.circuit_builder.builder import CircuitBuilder

def simulate_statevector(circuit):
    simulator = Aer.get_backend("statevector_simulator")
    result = execute(circuit, simulator).result()
    return result.get_statevector()

def run_tests():
    builder = CircuitBuilder()

    test_cases = [
        ("Bell State", CircuitType.BELL_STATE, {"num_qubits": 2}),
        ("GHZ State", CircuitType.GHZ_STATE, {"num_qubits": 3}),
        ("W State", CircuitType.W_STATE, {"num_qubits": 3}),
        ("Quantum Teleportation", CircuitType.TELEPORTATION, {}),
        ("Superdense Coding", CircuitType.SUPERDENSE_CODING, {"message": "10"}),
        ("Deutsch-Jozsa", CircuitType.DEUTSCH_JOZSA, {"num_qubits": 3, "oracle_type": "balanced"}),
        ("Bernstein-Vazirani", CircuitType.BERNSTEIN_VAZIRANI, {"num_qubits": 4, "secret_string": "101"}),
        ("Simon's Algorithm", CircuitType.SIMON, {"num_qubits": 4, "secret_string": "110"}),
        ("Quantum Fourier Transform", CircuitType.QFT, {"num_qubits": 3}),
        ("Quantum Phase Estimation", CircuitType.QPE, {"num_qubits": 4, "precision_qubits": 3}),
        ("Shor's Algorithm", CircuitType.SHOR, {"number_to_factor": 15}),
        ("Grover's Algorithm", CircuitType.GROVERS, {"num_qubits": 3, "marked_state": "101"}),
        ("QAOA", CircuitType.QAOA, {"num_qubits": 3, "depth": 1}),
        ("VQE", CircuitType.VQE, {"num_qubits": 2}),
        ("Quantum Counting", CircuitType.QUANTUM_COUNTING, {"num_qubits": 4, "counting_qubits": 2}),
        ("Quantum Walk", CircuitType.QUANTUM_WALK, {"num_qubits": 3, "steps": 2}),
        ("HHL", CircuitType.HHL, {"num_qubits": 4}),
        ("Custom Bell", CircuitType.CUSTOM, {"num_qubits": 2, "custom_gates": ["h 0", "cx 0 1"]}),
        ("Custom Hadamards", CircuitType.CUSTOM, {"num_qubits": 3, "custom_gates": ["h 0", "h 1", "h 2"]}),
        ("Custom Rotations", CircuitType.CUSTOM, {"num_qubits": 3, "custom_gates": ["rx 0 1.57", "ry 1 0.78", "rz 2 3.14"]}),
        ("Complex Custom Circuit", CircuitType.CUSTOM, {
            "num_qubits": 3,
            "custom_gates": [
                "h 0", "h 1", "h 2", "cx 0 1", "cx 1 2",
                "rz 0 0.5", "rz 1 0.5", "rz 2 0.5",
                "cx 1 2", "cx 0 1", "h 0", "h 1", "h 2"
            ]
        }),
        ("Custom with Measurements", CircuitType.CUSTOM, {
            "num_qubits": 2,
            "custom_gates": ["h 0", "cx 0 1", "measure 0 0", "measure 1 1"]
        }),
    ]

    for i, (name, ctype, params) in enumerate(test_cases):
        print(f"\n🧪 Test {i + 1}/{len(test_cases)}: {name}")
        try:
            intent = CircuitIntent(ctype, params)
            circuit = builder.build_circuit(intent)

            print(f"✔ Created circuit with {circuit.num_qubits} qubits and {len(circuit.data)} instructions")

            if "measure" in str(circuit):
                print("📏 Measurement included")

            # Optional simulations for specific tests
            if name == "Bell State":
                state = simulate_statevector(circuit)
                print(f"🔬 Bell amplitudes: |00⟩ = {abs(state[0])**2:.2f}, |11⟩ = {abs(state[3])**2:.2f}")
            elif name == "GHZ State":
                state = simulate_statevector(circuit)
                print(f"🔬 GHZ amplitudes: |000⟩ = {abs(state[0])**2:.2f}, |111⟩ = {abs(state[7])**2:.2f}")
            elif name == "Custom Hadamards":
                state = simulate_statevector(circuit)
                probs = [abs(amp) ** 2 for amp in state]
                print(f"🌀 Superposition state probabilities ≈ {[round(p, 3) for p in probs]}")

        except Exception as e:
            print(f"❌ Test '{name}' failed: {str(e)}")

if __name__ == "__main__":
    run_tests()
