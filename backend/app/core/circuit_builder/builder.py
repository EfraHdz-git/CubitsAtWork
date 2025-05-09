from typing import List
import re
import numpy as np
from qiskit import QuantumCircuit
from ..nlp_processor.intent_parser import CircuitType, CircuitIntent
from .openai_circuit_generator import OpenAICircuitGenerator

class CustomCircuitBuilder:

    def __init__(self):
        self.gate_map = {
            "h": self._apply_h,
            "x": self._apply_x,
            "y": self._apply_y,
            "z": self._apply_z,
            "id": self._apply_id,
            "cx": self._apply_cx,
            "cz": self._apply_cz,
            "ccx": self._apply_ccx,
            "rx": self._apply_rx,
            "ry": self._apply_ry,
            "rz": self._apply_rz,
            "u1": self._apply_u1,  # will auto map to rz
            "u2": self._apply_u2,
            "u3": self._apply_u3,
            "s": self._apply_s,
            "t": self._apply_t,
            "measure": self._apply_measure,
            "swap": self._apply_swap,
            "cp": self._apply_cp,
            "reset": self._apply_reset,
            "if": self._apply_conditional,
            "conditional": self._apply_conditional,  # Allow "conditional:" prefix from parser
            "barrier": self._apply_barrier
        }

    def build_circuit(self, num_qubits: int, gate_sequence: List[str]) -> QuantumCircuit:
        circuit = QuantumCircuit(num_qubits, num_qubits)

        for gate_instruction in gate_sequence:
            self._apply_gate(circuit, gate_instruction)

        if not any("measure" in gate for gate in gate_sequence):
            circuit.measure_all()

        return circuit

    def _apply_gate(self, circuit: QuantumCircuit, gate_instruction: str):
        # Handle measurement with arrow notation
        if "->" in gate_instruction:
            parts = gate_instruction.strip().replace("->", " ").split()
            if len(parts) >= 2:
                # Extract the actual qubit and classical bit indices
                if parts[0].lower() == "measure":
                    # Format: "measure 0 0 -> 0"
                    qubit_idx = parts[1]
                    clbit_idx = parts[-1]
                    parts = ["measure", qubit_idx, clbit_idx]
                else:
                    # Format: "0 -> 0" or "q[0] -> c[0]"
                    qubit_part = parts[0]
                    clbit_part = parts[-1]
                    
                    # Handle QASM style format with q[] and c[]
                    qubit_match = re.search(r'q\[(\d+)\]', qubit_part)
                    clbit_match = re.search(r'c\[(\d+)\]', clbit_part)
                    
                    if qubit_match and clbit_match:
                        qubit_idx = qubit_match.group(1)
                        clbit_idx = clbit_match.group(1)
                    else:
                        # Simple numeric format
                        qubit_idx = qubit_part
                        clbit_idx = clbit_part
                    
                    parts = ["measure", qubit_idx, clbit_idx]
            else:
                print(f"Invalid measurement format: {gate_instruction}")
                return
                
        # Handle conditional operations
        elif gate_instruction.startswith("if("):
            parts = gate_instruction.strip().replace(")", "").replace("(", " ").replace("==", " ").replace(",", " ").split()
            parts.insert(0, "if")
        elif gate_instruction.lower().startswith("conditional:"):
            parts = gate_instruction.replace("conditional:", "").strip().split()
            parts.insert(0, "conditional")
            
        # Handle rotation gates with angles in parentheses: rx(pi/3) 0, ry(pi/3) 0, rz(pi/6) 1
        elif any(gate_instruction.startswith(f"{g}(") for g in ["rx", "ry", "rz"]):
            # Extract gate name (rx, ry, rz)
            gate_name = gate_instruction.split("(")[0].strip()
            # Extract angle and target qubit
            remaining = gate_instruction.split("(", 1)[1]
            angle_str = remaining.split(")", 1)[0].strip()
            qubit_part = remaining.split(")", 1)[1].strip() if ")" in remaining else "0"
            
            # Parse qubit index
            qubit = qubit_part.split()[0] if " " in qubit_part else qubit_part
            
            # Parse angle expression - handle various formats
            if "/" in angle_str or "*" in angle_str or "+" in angle_str or "-" in angle_str:
                try:
                    # Replace pi with np.pi for evaluation
                    expression = angle_str.lower().replace("pi", "np.pi")
                    
                    # Safely evaluate the mathematical expression
                    angle = eval(expression)
                    print(f"Successfully evaluated angle expression '{angle_str}' to {angle}")
                except Exception as e:
                    print(f"Error evaluating angle expression '{angle_str}': {str(e)}")
                    angle = 0.0
            elif "pi" in angle_str.lower():
                try:
                    # Handle simple pi constants
                    expression = angle_str.lower().replace("pi", "np.pi")
                    angle = eval(expression)
                except Exception as e:
                    print(f"Error parsing pi angle '{angle_str}': {str(e)}")
                    angle = 0.0
            else:
                try:
                    # Handle plain numeric values
                    angle = float(angle_str)
                except Exception as e:
                    print(f"Error converting angle '{angle_str}' to float: {str(e)}")
                    angle = 0.0
                    
            parts = [gate_name, qubit, str(angle)]
        else:
            parts = gate_instruction.strip().split()

        if not parts:
            return

        gate_name = parts[0].lower()
        gate_function = self.gate_map.get(gate_name)
        if not gate_function:
            print(f"Warning: Unrecognized gate '{gate_name}' in instruction: {gate_instruction}")
            return

        try:
            gate_function(circuit, parts[1:])
        except Exception as e:
            print(f"Error applying gate {gate_name} with args {parts[1:]}: {str(e)}")

    # --- Gate implementations ---

    def _apply_h(self, circuit, args):
        circuit.h(int(args[0]))

    def _apply_x(self, circuit, args):
        circuit.x(int(args[0]))

    def _apply_y(self, circuit, args):
        circuit.y(int(args[0]))

    def _apply_z(self, circuit, args):
        circuit.z(int(args[0]))

    def _apply_id(self, circuit, args):
        circuit.i(int(args[0]))

    def _apply_cx(self, circuit, args):
        circuit.cx(int(args[0]), int(args[1]))

    def _apply_cz(self, circuit, args):
        circuit.cz(int(args[0]), int(args[1]))

    def _apply_ccx(self, circuit, args):
        circuit.ccx(int(args[0]), int(args[1]), int(args[2]))

    def _apply_rx(self, circuit, args):
        try:
            if len(args) >= 2:
                circuit.rx(float(args[1]), int(args[0]))
            else:
                print(f"Insufficient args for rx: {args}")
        except Exception as e:
            print(f"Error applying rx gate: {str(e)}")

    def _apply_ry(self, circuit, args):
        try:
            if len(args) >= 2:
                circuit.ry(float(args[1]), int(args[0]))
            else:
                print(f"Insufficient args for ry: {args}")
        except Exception as e:
            print(f"Error applying ry gate: {str(e)}")

    def _apply_rz(self, circuit, args):
        try:
            if len(args) >= 2:
                circuit.rz(float(args[1]), int(args[0]))
            else:
                print(f"Insufficient args for rz: {args}")
        except Exception as e:
            print(f"Error applying rz gate: {str(e)}")

    def _apply_u1(self, circuit, args):
        # U1 is deprecated -> same as RZ
        try:
            if len(args) >= 2:
                circuit.rz(float(args[1]), int(args[0]))
            else:
                print(f"Insufficient args for u1: {args}")
        except Exception as e:
            print(f"Error applying u1 gate: {str(e)}")

    def _apply_u2(self, circuit, args):
        try:
            if len(args) >= 3:
                circuit.u2(float(args[1]), float(args[2]), int(args[0]))
            else:
                print(f"Insufficient args for u2: {args}")
        except Exception as e:
            print(f"Error applying u2 gate: {str(e)}")

    def _apply_u3(self, circuit, args):
        try:
            if len(args) >= 4:
                circuit.u3(float(args[1]), float(args[2]), float(args[3]), int(args[0]))
            else:
                print(f"Insufficient args for u3: {args}")
        except Exception as e:
            print(f"Error applying u3 gate: {str(e)}")

    def _apply_s(self, circuit, args):
        circuit.s(int(args[0]))

    def _apply_t(self, circuit, args):
        circuit.t(int(args[0]))

    def _apply_measure(self, circuit, args):
        try:
            # Print args for debugging
            print(f"Applying measure with args: {args}")
            if len(args) >= 2:
                qubit_idx = int(args[0])
                clbit_idx = int(args[1])
                circuit.measure(qubit_idx, clbit_idx)
            else:
                print(f"Insufficient args for measure: {args}")
        except Exception as e:
            print(f"Error applying measure gate: {str(e)}")

    def _apply_swap(self, circuit, args):
        circuit.swap(int(args[0]), int(args[1]))

    def _apply_cp(self, circuit, args):
        circuit.cp(float(args[2]), int(args[0]), int(args[1]))

    def _apply_reset(self, circuit, args):
        circuit.reset(int(args[0]))

    def _apply_barrier(self, circuit, args):
        qubits = [int(q) for q in args]
        circuit.barrier(*qubits)

    def _apply_conditional(self, circuit, args):
        """
        Format expected:
        conditional if c 2 1 x 2   OR  if c 2 1 x 2
        Meaning: if classical c[2] == 1, apply X on qubit 2.
        """
        print(f"Applying conditional operation with args: {args}")
        if len(args) >= 4:
            try:
                creg_index = int(args[1])
                condition_value = int(args[2])
                gate = args[3].lower()
                qubit = int(args[4]) if len(args) >= 5 else None

                if qubit is None:
                    return

                # Define the condition register
                condition_register = circuit.cregs[0]
                
                # Handle conditional operations based on gate type
                if gate == "x":
                    # Create the conditional X gate
                    # First apply the gate normally
                    x_gate = circuit.x(qubit)
                    # Then add the condition
                    x_gate.c_if(condition_register, condition_value)
                    
                    # Modify the name of the last instruction to indicate it's conditional
                    if len(circuit.data) > 0:
                        last_instruction = circuit.data[-1]
                        instruction_obj = last_instruction[0]
                        if hasattr(instruction_obj, 'name'):
                            original_name = instruction_obj.name
                            instruction_obj.name = f"{original_name}_if_{condition_value}"
                
                elif gate == "z":
                    z_gate = circuit.z(qubit)
                    z_gate.c_if(condition_register, condition_value)
                    if len(circuit.data) > 0:
                        last_instruction = circuit.data[-1]
                        instruction_obj = last_instruction[0]
                        if hasattr(instruction_obj, 'name'):
                            original_name = instruction_obj.name
                            instruction_obj.name = f"{original_name}_if_{condition_value}"
                
                elif gate == "y":
                    y_gate = circuit.y(qubit)
                    y_gate.c_if(condition_register, condition_value)
                    if len(circuit.data) > 0:
                        last_instruction = circuit.data[-1]
                        instruction_obj = last_instruction[0]
                        if hasattr(instruction_obj, 'name'):
                            original_name = instruction_obj.name
                            instruction_obj.name = f"{original_name}_if_{condition_value}"
                
                elif gate == "h":
                    h_gate = circuit.h(qubit)
                    h_gate.c_if(condition_register, condition_value)
                    if len(circuit.data) > 0:
                        last_instruction = circuit.data[-1]
                        instruction_obj = last_instruction[0]
                        if hasattr(instruction_obj, 'name'):
                            original_name = instruction_obj.name
                            instruction_obj.name = f"{original_name}_if_{condition_value}"
                
                elif gate in ["rx", "ry", "rz"] and len(args) >= 6:
                    angle = float(args[5])
                    if gate == "rx":
                        rx_gate = circuit.rx(angle, qubit)
                        rx_gate.c_if(condition_register, condition_value)
                        if len(circuit.data) > 0:
                            last_instruction = circuit.data[-1]
                            instruction_obj = last_instruction[0]
                            if hasattr(instruction_obj, 'name'):
                                original_name = instruction_obj.name
                                instruction_obj.name = f"{original_name}_if_{condition_value}"
                    
                    elif gate == "ry":
                        ry_gate = circuit.ry(angle, qubit)
                        ry_gate.c_if(condition_register, condition_value)
                        if len(circuit.data) > 0:
                            last_instruction = circuit.data[-1]
                            instruction_obj = last_instruction[0]
                            if hasattr(instruction_obj, 'name'):
                                original_name = instruction_obj.name
                                instruction_obj.name = f"{original_name}_if_{condition_value}"
                    
                    elif gate == "rz":
                        rz_gate = circuit.rz(angle, qubit)
                        rz_gate.c_if(condition_register, condition_value)
                        if len(circuit.data) > 0:
                            last_instruction = circuit.data[-1]
                            instruction_obj = last_instruction[0]
                            if hasattr(instruction_obj, 'name'):
                                original_name = instruction_obj.name
                                instruction_obj.name = f"{original_name}_if_{condition_value}"
                
                else:
                    print(f"Unsupported conditional gate: {gate}")
            
            except Exception as e:
                print(f"Error in conditional gate: {str(e)}")


class CircuitBuilder:

    def __init__(self, api_key=None):
        self.custom_builder = CustomCircuitBuilder()
        self.openai_generator = OpenAICircuitGenerator(api_key)
        self.MAX_QUBITS = 50

    def build_circuit(self, intent: CircuitIntent) -> QuantumCircuit:
        circuit_type = intent.circuit_type
        params = intent.params
        num_qubits = params.get("num_qubits", None)

        if num_qubits is not None:
            num_qubits = min(num_qubits, self.MAX_QUBITS)

        if circuit_type == CircuitType.CUSTOM:
            custom_gates = params.get("custom_gates", ["h 0", "cx 0 1"])
            
            # Debug log the gates being processed
            print(f"Building circuit with {len(custom_gates)} gates: {custom_gates}")

            if num_qubits is None:
                highest_qubit = -1
                for gate_str in custom_gates:
                    parts = gate_str.strip().split()
                    for part in parts[1:]:
                        try:
                            qubit = int(part)
                            highest_qubit = max(highest_qubit, qubit)
                        except ValueError:
                            pass

                num_qubits = max(2, highest_qubit + 1)
                num_qubits = min(num_qubits, self.MAX_QUBITS)

            return self.custom_builder.build_circuit(num_qubits, custom_gates)

        if num_qubits is None:
            num_qubits = self.openai_generator._get_default_qubit_count(circuit_type)
            num_qubits = min(num_qubits, self.MAX_QUBITS)

        params["num_qubits"] = num_qubits
        gate_sequence = self.openai_generator.generate_circuit_gates(circuit_type, params)

        return self.custom_builder.build_circuit(num_qubits, gate_sequence)