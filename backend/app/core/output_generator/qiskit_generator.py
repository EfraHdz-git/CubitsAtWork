# app/core/output_generator/qiskit_generator.py
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
import re
from datetime import datetime

class QiskitGenerator:
    """Generates professional, directly executable Qiskit code from a quantum circuit."""
    
    def generate_code(self, circuit: QuantumCircuit, circuit_type: str = "custom", description: str = None) -> str:
        """
        Generate well-commented, executable Python code that creates the given circuit.
        
        Args:
            circuit: The quantum circuit to generate code for
            circuit_type: The type of circuit (e.g., 'bell_state', 'qft', etc.)
            description: Optional description of what the circuit does
            
        Returns:
            str: Directly executable Python code with proper comments
        """
        circuit_code = []
        
        # Add header with metadata
        circuit_code.append("# " + "=" * 80)
        circuit_code.append(f"# Quantum Circuit: {circuit_type.replace('_', ' ').title()}")
        circuit_code.append(f"# Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        circuit_code.append(f"# Qubits: {circuit.num_qubits}, Classical bits: {circuit.num_clbits}")
        
        if description:
            circuit_code.append("# ")
            circuit_code.append(f"# Description: {description}")
        
        circuit_code.append("# " + "=" * 80 + "\n")
        
        # Only include imports that are actually used
        circuit_code.append("# Required imports")
        circuit_code.append("from qiskit import QuantumCircuit")
        
        # Determine which imports are needed based on the code we'll generate
        needs_aer = True  # We'll include simulation code
        needs_visualization = True  # We'll include visualization code
        
        # Add just the imports that will be used
        if needs_aer:
            circuit_code.append("from qiskit import transpile, execute")
            circuit_code.append("# Import Aer from qiskit_aer package")
            circuit_code.append("from qiskit_aer import Aer")
        if needs_visualization:
            circuit_code.append("from qiskit.visualization import plot_histogram")
            if circuit.num_qubits <= 2:
                circuit_code.append("from qiskit.visualization import plot_bloch_multivector")
        
        # Add a function definition to make the code more structured and reusable
        circuit_code.append("\n\ndef create_circuit():")
        circuit_code.append(f"    \"\"\"" + (description or f"Creates a {circuit_type.replace('_', ' ')} quantum circuit") + "\"\"\"")
        circuit_code.append(f"    # Initialize quantum circuit with {circuit.num_qubits} qubits and {circuit.num_clbits} classical bits")
        circuit_code.append(f"    qc = QuantumCircuit({circuit.num_qubits}, {circuit.num_clbits})")
        
        # Organize gates by sections
        initialization_gates = []
        core_algorithm_gates = []
        measurement_gates = []
        
        # Generate gate code with appropriate comments
        for i, (instruction, qargs, cargs) in enumerate(circuit.data):
            # Get the name of the gate
            gate_name = instruction.name
            # Fixed: use enumeration instead of direct index property
            qubits = [i for i, _ in enumerate(qargs)]
            clbits = [i for i, _ in enumerate(cargs)]
            
            # Add code with comments - indented for the function
            gate_code = self._generate_gate_code(gate_name, qubits, clbits, instruction, indent=4)
            
            # Categorize gates
            if gate_name == "measure":
                measurement_gates.append(gate_code)
            elif i < len(circuit.data) // 3:  # Simple heuristic for initialization
                initialization_gates.append(gate_code)
            else:
                core_algorithm_gates.append(gate_code)
        
        # Add sections with appropriate comments
        if initialization_gates:
            circuit_code.append("\n    # Initialization")
            circuit_code.extend(initialization_gates)
        
        if core_algorithm_gates:
            circuit_name = circuit_type.replace('_', ' ').title()
            circuit_code.append(f"\n    # {circuit_name} Algorithm Core Operations")
            circuit_code.extend(core_algorithm_gates)
        
        if measurement_gates:
            circuit_code.append("\n    # Measurement Operations")
            circuit_code.extend(measurement_gates)
        elif len(circuit.data) > 0:  # Add measurement if none exist and there are gates
            circuit_code.append("\n    # Add measurements to all qubits")
            circuit_code.append("    qc.measure_all()")
        
        # Return the circuit from the function
        circuit_code.append("\n    return qc")
        
        # Add a function to simulate the circuit
        circuit_code.append("\n\ndef simulate_circuit(qc):")
        circuit_code.append("    \"\"\"Simulates the given quantum circuit and returns the results.\"\"\"")
        circuit_code.append("    # Get a simulator backend")
        circuit_code.append("    simulator = Aer.get_backend('qasm_simulator')")
        circuit_code.append("    # Transpile circuit for the simulator")
        circuit_code.append("    transpiled_circuit = transpile(qc, simulator)")
        circuit_code.append("    # Execute the circuit on the simulator with 1024 shots")
        circuit_code.append("    job = execute(transpiled_circuit, simulator, shots=1024)")
        circuit_code.append("    # Get the results")
        circuit_code.append("    result = job.result()")
        circuit_code.append("    counts = result.get_counts()")
        circuit_code.append("    return counts")

        # Add a function to analyze the results based on circuit type
        if circuit_type in ["bell_state", "ghz_state", "qft", "grovers"]:
            circuit_code.append("\n\ndef analyze_results(counts):")
            circuit_code.append("    \"\"\"Analyzes the simulation results based on the circuit type.\"\"\"")
            
            if circuit_type == "bell_state":
                circuit_code.append("    # Bell State Analysis")
                circuit_code.append("    # Check for entanglement - should see mostly |00⟩ and |11⟩ states")
                circuit_code.append("    print('Counts:', counts)")
                circuit_code.append("    # Calculate probabilities")
                circuit_code.append("    total_shots = sum(counts.values())")
                circuit_code.append("    print(f'|00⟩ probability: {counts.get(\"00\", 0)/total_shots:.2f}')")
                circuit_code.append("    print(f'|11⟩ probability: {counts.get(\"11\", 0)/total_shots:.2f}')")
            
            elif circuit_type == "qft":
                circuit_code.append("    # QFT Analysis")
                circuit_code.append("    print('Measurement outcomes:', counts)")
                circuit_code.append("    # Sort by frequency")
                circuit_code.append("    sorted_counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))")
                circuit_code.append("    print('Most frequent outcomes:', list(sorted_counts.keys())[:3])")
        
        # Add a main function that demonstrates how to use the code
        circuit_code.append("\n\ndef main():")
        circuit_code.append("    \"\"\"Main function to create, simulate and analyze the circuit.\"\"\"")
        circuit_code.append("    # Create the quantum circuit")
        circuit_code.append("    qc = create_circuit()")
        circuit_code.append("    ")
        circuit_code.append("    # Display circuit (uncomment to display)")
        circuit_code.append("    # print(qc)")
        circuit_code.append("    ")
        circuit_code.append("    # Simulate the circuit")
        circuit_code.append("    counts = simulate_circuit(qc)")
        circuit_code.append("    ")
        
        # Add analysis call if it exists
        if circuit_type in ["bell_state", "ghz_state", "qft", "grovers"]:
            circuit_code.append("    # Analyze the results")
            circuit_code.append("    analyze_results(counts)")
            circuit_code.append("    ")
        else:
            circuit_code.append("    # Print the results")
            circuit_code.append("    print('Measurement results:', counts)")
            circuit_code.append("    ")
        
        circuit_code.append("    # Plot the results")
        circuit_code.append("    histogram = plot_histogram(counts)")
        circuit_code.append("    # histogram.savefig('results.png')  # Uncomment to save the histogram")
        
        # Add execution guard to make the code properly importable
        circuit_code.append("\n\n# This ensures the code runs when executed directly")
        circuit_code.append("if __name__ == \"__main__\":")
        circuit_code.append("    main()")
        
        return "\n".join(circuit_code)
    
    def _generate_gate_code(self, gate_name, qubits, clbits, instruction, indent=0) -> str:
        """Generate code for a specific gate with appropriate comments."""
        indent_str = " " * indent
        gate_comment = ""
        gate_code = ""
        
        # Special handling for common gates with detailed comments
        if gate_name == "h":
            gate_comment = f"{indent_str}# Apply Hadamard gate to qubit {qubits[0]} (creates superposition)"
            gate_code = f"{indent_str}qc.h({qubits[0]})"
        elif gate_name == "x":
            gate_comment = f"{indent_str}# Apply X gate (NOT gate) to qubit {qubits[0]} (flips the qubit)"
            gate_code = f"{indent_str}qc.x({qubits[0]})"
        elif gate_name == "y":
            gate_comment = f"{indent_str}# Apply Y gate to qubit {qubits[0]}"
            gate_code = f"{indent_str}qc.y({qubits[0]})"
        elif gate_name == "z":
            gate_comment = f"{indent_str}# Apply Z gate to qubit {qubits[0]} (phase flip)"
            gate_code = f"{indent_str}qc.z({qubits[0]})"
        elif gate_name == "cx" or gate_name == "cnot":
            gate_comment = f"{indent_str}# Apply CNOT gate: control={qubits[0]}, target={qubits[1]} (entangles qubits)"
            gate_code = f"{indent_str}qc.cx({qubits[0]}, {qubits[1]})"
        elif gate_name == "cz":
            gate_comment = f"{indent_str}# Apply CZ gate: control={qubits[0]}, target={qubits[1]}"
            gate_code = f"{indent_str}qc.cz({qubits[0]}, {qubits[1]})"
        elif gate_name.startswith("r") and hasattr(instruction, 'params') and instruction.params:
            angle = instruction.params[0]
            angle_str = f"{angle:.4f}"
            gate_comment = f"{indent_str}# Apply {gate_name.upper()} rotation by {angle_str} radians to qubit {qubits[0]}"
            gate_code = f"{indent_str}qc.{gate_name}({angle_str}, {qubits[0]})"
        elif gate_name == "measure":
            gate_comment = f"{indent_str}# Measure qubit {qubits[0]} and store result in classical bit {clbits[0]}"
            gate_code = f"{indent_str}qc.measure({qubits[0]}, {clbits[0]})"
        elif gate_name == "barrier":
            qubits_str = ", ".join(map(str, qubits))
            gate_comment = f"{indent_str}# Add a barrier to prevent optimization across this point"
            gate_code = f"{indent_str}qc.barrier({qubits_str})"
        else:
            # Generic format for other gates
            qubits_str = ", ".join(map(str, qubits))
            # Add params if available
            if hasattr(instruction, 'params') and instruction.params:
                params_str = ", ".join(f"{p:.4f}" for p in instruction.params)
                if params_str:
                    gate_comment = f"{indent_str}# Apply {gate_name} gate with parameters [{params_str}] to qubits {qubits}"
                    gate_code = f"{indent_str}qc.{gate_name}({params_str}, {qubits_str})"
                else:
                    gate_comment = f"{indent_str}# Apply {gate_name} gate to qubits {qubits}"
                    gate_code = f"{indent_str}qc.{gate_name}({qubits_str})"
            else:
                gate_comment = f"{indent_str}# Apply {gate_name} gate to qubits {qubits}"
                gate_code = f"{indent_str}qc.{gate_name}({qubits_str})"
                
        return f"{gate_comment}\n{gate_code}"