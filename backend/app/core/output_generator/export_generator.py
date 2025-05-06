# app/core/output_generator/export_generator.py
from qiskit import QuantumCircuit
import json
import qiskit.qpy as qpy
import io
from datetime import datetime
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

class ExportGenerator:
   """Generates various export formats for quantum circuits with enhanced metadata."""
   
   def generate_qasm(self, circuit: QuantumCircuit, circuit_type: str = "custom", description: str = None) -> str:
       """
       Generate OpenQASM code for the circuit with detailed comments.
       
       Args:
           circuit: The quantum circuit to export
           circuit_type: Type of the circuit (e.g., 'bell_state', 'qft')
           description: Optional description of what the circuit does
           
       Returns:
           str: OpenQASM representation of the circuit with comments
       """
       # Get the base QASM code
       qasm_code = circuit.qasm()
       
       # Add header comments
       header = [
           "// ========================================================================",
           f"// Quantum Circuit: {circuit_type.replace('_', ' ').title()}",
           f"// Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
           f"// Qubits: {circuit.num_qubits}, Classical bits: {circuit.num_clbits}",
       ]
       
       if description:
           header.append("//")
           header.append(f"// Description: {description}")
           
       header.append("// ========================================================================\n")
       
       # Insert header comments after the include statements
       include_end = qasm_code.find(';', qasm_code.find('include')) + 1
       enhanced_qasm = qasm_code[:include_end+1] + '\n' + '\n'.join(header) + qasm_code[include_end+1:]
       
       # Add comments for register definitions
       qreg_index = enhanced_qasm.find('qreg')
       if qreg_index >= 0:
           enhanced_qasm = enhanced_qasm[:qreg_index] + '// Quantum register definition\n' + enhanced_qasm[qreg_index:]
           
       creg_index = enhanced_qasm.find('creg')
       if creg_index >= 0:
           enhanced_qasm = enhanced_qasm[:creg_index] + '// Classical register definition\n' + enhanced_qasm[creg_index:]
       
       # Add operation sections
       # Find the start of gate operations (after register definitions)
       operations_start = max(enhanced_qasm.rfind(';', 0, enhanced_qasm.find('h ') or enhanced_qasm.find('x ') or len(enhanced_qasm)) + 1, 0)
       
       if operations_start > 0:
           operations_comment = "\n// Circuit Operations\n"
           enhanced_qasm = enhanced_qasm[:operations_start] + operations_comment + enhanced_qasm[operations_start:]
       
       # Add a comment before the measurement section if it exists
       measure_index = enhanced_qasm.find('measure')
       if measure_index >= 0:
           enhanced_qasm = enhanced_qasm[:measure_index] + '\n// Measurement Operations\n' + enhanced_qasm[measure_index:]
       
       return enhanced_qasm
   
   def generate_qpy(self, circuit: QuantumCircuit) -> bytes:
       """
       Generate QPY binary format for the circuit.
       
       Returns:
           bytes: QPY binary representation of the circuit
       """
       buffer = io.BytesIO()
       qpy.dump(circuit, buffer)
       return buffer.getvalue()
   
   def generate_json(self, circuit: QuantumCircuit, circuit_type: str = "custom", description: str = None) -> str:
       """
       Generate a comprehensive JSON representation of the circuit with metadata.
       
       Args:
           circuit: The quantum circuit to export
           circuit_type: Type of the circuit (e.g., 'bell_state', 'qft')
           description: Optional description of what the circuit does
           
       Returns:
           str: JSON representation of the circuit with metadata
       """
       # Create a dictionary with metadata
       circuit_dict = {
           "metadata": {
               "circuit_type": circuit_type,
               "name": circuit_type.replace('_', ' ').title(),
               "description": description or f"A {circuit_type.replace('_', ' ')} quantum circuit",
               "generated_on": datetime.now().isoformat(),
               "num_qubits": circuit.num_qubits,
               "num_clbits": circuit.num_clbits,
               "depth": circuit.depth(),
               "size": len(circuit.data)
           },
           "circuit": {
               "registers": {
                   "qregs": [{"name": "q", "size": circuit.num_qubits}],
                   "cregs": [{"name": "c", "size": circuit.num_clbits}]
               },
               "operations": []
           }
       }
       
       # Add each gate operation with detailed information
       for instruction, qargs, cargs in circuit.data:
           gate_info = {
               "name": instruction.name,
               "qubits": [q.index for q in qargs],
               "clbits": [c.index for c in cargs] if cargs else []
           }
           
           # Add any parameters the gate might have
           if hasattr(instruction, 'params') and instruction.params:
               gate_info["parameters"] = [float(param) for param in instruction.params]
           
           # Add gate description
           if instruction.name == "h":
               gate_info["description"] = "Hadamard gate (creates superposition)"
           elif instruction.name == "x":
               gate_info["description"] = "Pauli-X gate (NOT gate)"
           elif instruction.name == "cx":
               gate_info["description"] = "CNOT gate (creates entanglement)"
           elif instruction.name == "measure":
               gate_info["description"] = "Measurement operation"
           
           circuit_dict["circuit"]["operations"].append(gate_info)
       
       return json.dumps(circuit_dict, indent=2)
   
   def generate_ibmq_job(self, circuit: QuantumCircuit, circuit_type: str = "custom", description: str = None) -> str:
       """
       Generate comprehensive IBM Quantum Experience job configuration.
       
       Args:
           circuit: The quantum circuit to export
           circuit_type: Type of the circuit (e.g., 'bell_state', 'qft')  
           description: Optional description of what the circuit does
           
       Returns:
           str: JSON configuration for IBM Q Experience with metadata
       """
       ibmq_config = {
           "metadata": {
               "circuit_type": circuit_type,
               "name": circuit_type.replace('_', ' ').title(),
               "description": description or f"A {circuit_type.replace('_', ' ')} quantum circuit",
               "generated_on": datetime.now().isoformat()
           },
           "backend": {
               "name": "ibmq_qasm_simulator"  # Default to simulator
           },
           "shots": 1024,
           "max_credits": 10,
           "qobj_id": None,
           "circuits": [{
               "name": circuit_type.replace('_', '_'),
               "metadata": {
                   "num_qubits": circuit.num_qubits,
                   "num_clbits": circuit.num_clbits
               },
               "compiled_circuit": {
                   "header": {
                       "clbit_labels": [["c", i] for i in range(circuit.num_clbits)],
                       "creg_sizes": [["c", circuit.num_clbits]],
                       "global_phase": 0,
                       "memory_slots": circuit.num_clbits,
                       "n_qubits": circuit.num_qubits,
                       "qreg_sizes": [["q", circuit.num_qubits]]
                   },
                   "operations": []
               }
           }]
       }
       
       # Add QASM representation
       ibmq_config["circuits"][0]["qasm"] = circuit.qasm()
       
       # Add gates to operations
       for instruction, qargs, cargs in circuit.data:
           operation = {
               "name": instruction.name,
               "qubits": [q.index for q in qargs],
               "memory": [c.index for c in cargs] if cargs else []
           }
           
           # Add parameters if applicable
           if hasattr(instruction, 'params') and instruction.params:
               operation["params"] = [float(param) for param in instruction.params]
               
           ibmq_config["circuits"][0]["compiled_circuit"]["operations"].append(operation)
       
       return json.dumps(ibmq_config, indent=2)
       
   def generate_jupyter_notebook(self, circuit: QuantumCircuit, circuit_type: str = "custom", description: str = None) -> str:
       """
       Generate a Jupyter Notebook containing the quantum circuit code and visualizations.
       
       Args:
           circuit: The quantum circuit to export
           circuit_type: Type of the circuit (e.g., 'bell_state', 'qft')
           description: Optional description of what the circuit does
           
       Returns:
           str: JSON representation of the Jupyter Notebook
       """
       # Create a new notebook
       nb = new_notebook()
       
       # Add title and description
       title = f"# {circuit_type.replace('_', ' ').title()} Quantum Circuit"
       markdown_content = [
           title,
           f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
           "",
           "## Description",
           description or f"This notebook contains a {circuit_type.replace('_', ' ')} quantum circuit implementation.",
           "",
           "## Circuit Properties",
           f"- **Number of qubits:** {circuit.num_qubits}",
           f"- **Number of classical bits:** {circuit.num_clbits}",
           f"- **Circuit depth:** {circuit.depth()}",
           f"- **Gate count:** {len(circuit.data)}",
           "",
           "## Implementation"
       ]
       
       nb.cells.append(new_markdown_cell('\n'.join(markdown_content)))
       
       # Add imports in a code cell
       imports = [
           "# Import necessary libraries",
           "from qiskit import QuantumCircuit, Aer, execute, transpile",
           "from qiskit.visualization import plot_histogram, plot_bloch_multivector"
       ]
       nb.cells.append(new_code_cell('\n'.join(imports)))
       
       # Add circuit creation cell
       circuit_creation = [
           f"# Create the {circuit_type.replace('_', ' ')} circuit",
           f"qc = QuantumCircuit({circuit.num_qubits}, {circuit.num_clbits})"
       ]
       
       # Add gate operations
       for instruction, qargs, cargs in circuit.data:
           gate_name = instruction.name
           qubits = [q.index for q in qargs]
           clbits = [c.index for c in cargs]
           
           # Add comment for the gate
           if gate_name == "h":
               circuit_creation.append(f"# Apply Hadamard gate to qubit {qubits[0]}")
           elif gate_name == "cx" or gate_name == "cnot":
               circuit_creation.append(f"# Apply CNOT gate: control={qubits[0]}, target={qubits[1]}")
           elif gate_name == "measure":
               circuit_creation.append(f"# Measure qubit {qubits[0]} to classical bit {clbits[0]}")
           
           # Add the gate code
           if gate_name == "h":
               circuit_creation.append(f"qc.h({qubits[0]})")
           elif gate_name == "x":
               circuit_creation.append(f"qc.x({qubits[0]})")
           elif gate_name == "y":
               circuit_creation.append(f"qc.y({qubits[0]})")
           elif gate_name == "z":
               circuit_creation.append(f"qc.z({qubits[0]})")
           elif gate_name == "cx" or gate_name == "cnot":
               circuit_creation.append(f"qc.cx({qubits[0]}, {qubits[1]})")
           elif gate_name == "cz":
               circuit_creation.append(f"qc.cz({qubits[0]}, {qubits[1]})")
           elif gate_name.startswith("r") and hasattr(instruction, 'params') and instruction.params:
               angle = instruction.params[0]
               angle_str = f"{angle:.4f}"
               circuit_creation.append(f"qc.{gate_name}({angle_str}, {qubits[0]})")
           elif gate_name == "measure":
               circuit_creation.append(f"qc.measure({qubits[0]}, {clbits[0]})")
           elif gate_name == "barrier":
               qubits_str = ", ".join(map(str, qubits))
               circuit_creation.append(f"qc.barrier({qubits_str})")
           else:
               # Generic format for other gates
               qubits_str = ", ".join(map(str, qubits))
               if hasattr(instruction, 'params') and instruction.params:
                   params_str = ", ".join(f"{p:.4f}" for p in instruction.params)
                   if params_str:
                       circuit_creation.append(f"qc.{gate_name}({params_str}, {qubits_str})")
                   else:
                       circuit_creation.append(f"qc.{gate_name}({qubits_str})")
               else:
                   circuit_creation.append(f"qc.{gate_name}({qubits_str})")
       
       nb.cells.append(new_code_cell('\n'.join(circuit_creation)))
       
       # Add circuit visualization cell
       nb.cells.append(new_markdown_cell("## Circuit Visualization"))
       nb.cells.append(new_code_cell("# Display the circuit\nqc.draw('mpl')"))
       
       # Add simulation cell
       nb.cells.append(new_markdown_cell("## Circuit Simulation"))
       simulation_code = [
           "# Run the circuit on a simulator",
           "simulator = Aer.get_backend('qasm_simulator')",
           "transpiled_circuit = transpile(qc, simulator)",
           "job = execute(transpiled_circuit, simulator, shots=1024)",
           "result = job.result()",
           "counts = result.get_counts()",
           "",
           "# Print the results",
           "print('Measurement results:')",
           "print(counts)"
       ]
       nb.cells.append(new_code_cell('\n'.join(simulation_code)))
       
       # Add results visualization
       nb.cells.append(new_markdown_cell("## Results Visualization"))
       nb.cells.append(new_code_cell("# Plot the results\nplot_histogram(counts)"))
       
       # Add statevector visualization for small circuits
       if circuit.num_qubits <= 2:
           nb.cells.append(new_markdown_cell("## Statevector Visualization"))
           statevector_code = [
               "# Create a copy of the circuit without measurements",
               "qc_no_measure = QuantumCircuit(qc.num_qubits)",
               "for instr, qargs, cargs in qc.data:",
               "    if instr.name != 'measure':",
               "        qc_no_measure.append(instr, qargs, cargs)",
               "",
               "# Simulate the statevector",
               "statevector_simulator = Aer.get_backend('statevector_simulator')",
               "job = execute(qc_no_measure, statevector_simulator)",
               "statevector = job.result().get_statevector()",
               "",
               "# Display the Bloch sphere representation",
               "plot_bloch_multivector(statevector)"
           ]
           nb.cells.append(new_code_cell('\n'.join(statevector_code)))
       
       # Add analysis section for specific circuit types
       if circuit_type in ["bell_state", "ghz_state", "qft", "grovers"]:
           nb.cells.append(new_markdown_cell("## Circuit Analysis"))
           
           analysis_code = ["# Analyze the results"]
           if circuit_type == "bell_state":
               analysis_code.extend([
                   "# For a Bell state, we expect to see |00⟩ and |11⟩ with equal probability",
                   "total_shots = sum(counts.values())",
                   "print(f'|00⟩ probability: {counts.get(\"00\", 0)/total_shots:.2f}')",
                   "print(f'|11⟩ probability: {counts.get(\"11\", 0)/total_shots:.2f}')"
               ])
           elif circuit_type == "qft":
               analysis_code.extend([
                   "# Analyze QFT output",
                   "print('Measurement outcomes:', counts)",
                   "# Sort by frequency",
                   "sorted_counts = dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))",
                   "print('Most frequent outcomes:', list(sorted_counts.keys())[:3])"
               ])
           
           nb.cells.append(new_code_cell('\n'.join(analysis_code)))
       
       # Add a further exploration cell
       nb.cells.append(new_markdown_cell("## Further Exploration"))
       nb.cells.append(new_code_cell("# Your experiments and modifications\n# Try changing parameters or adding gates\n"))
       
       # Convert notebook to JSON
       return nbformat.writes(nb)