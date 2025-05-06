import os
import json
import math
import re
from typing import Dict, Any, Optional, List
from .intent_parser import CircuitIntent, CircuitType
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class OpenAICircuitParser:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required.")
        self.client = OpenAI(api_key=self.api_key)

    def parse_angle(self, angle_expression: str) -> float:
        angle_expression = angle_expression.lower().replace('π', 'math.pi').replace('pi', 'math.pi')
        try:
            return eval(angle_expression)
        except Exception as e:
            print(f"Error parsing angle '{angle_expression}': {str(e)}")
            match = re.search(r'([\d.]+)', angle_expression)
            return float(match.group(1)) if match else 0.0

    def normalize_gate_instructions(self, gates: List[str]) -> List[str]:
        normalized_gates = []
        for gate in gates:
            # Debug log
            print(f"Normalizing gate instruction: '{gate}'")
            
            # Skip empty or None gates
            if not gate:
                continue
                
            # Handle measurement with arrow
            if "->" in gate:
                parts = gate.replace("->", " ").split()
                if len(parts) == 2:
                    normalized_gates.append(f"measure {parts[0]} {parts[1]}")
                elif len(parts) == 3 and parts[0].lower() == "measure":
                    normalized_gates.append(f"measure {parts[1]} {parts[2]}")
                else:
                    normalized_gates.append(gate)
            
            # Handle conditionals
            elif gate.startswith("if("):
                match = re.match(r"if\s*\(c\[(\d+)\]==(\d+)\)\s*(\w+)\s*(\d+)", gate)
                if match:
                    normalized_gates.append(f"if c {match.group(1)} {match.group(2)} {match.group(3)} {match.group(4)}")
                else:
                    normalized_gates.append(gate)
            
            # Handle rotation gates with parentheses like rx(pi/3) 0
            elif any(gate.startswith(f"{g}(") for g in ["rx", "ry", "rz"]):
                # Keep the format as is - the CustomCircuitBuilder will handle it
                normalized_gates.append(gate)
                print(f"Kept rotation gate with parentheses: '{gate}'")
            
            # Handle rotation gates with separate angle params like rx 0 1.5708
            elif any(gate.startswith(prefix) for prefix in ["rx ", "ry ", "rz ", "u1 ", "u2 ", "u3 "]):
                parts = gate.split()
                if len(parts) >= 3:
                    # Try to parse and normalize the angle value
                    try:
                        angle = self.parse_angle(" ".join(parts[2:]))
                        normalized_gates.append(f"{parts[0]} {parts[1]} {angle}")
                        print(f"Normalized rotation gate with separate angle: '{parts[0]} {parts[1]} {angle}'")
                    except Exception as e:
                        print(f"Error normalizing angle in gate '{gate}': {str(e)}")
                        normalized_gates.append(gate)
                else:
                    normalized_gates.append(gate)
            else:
                normalized_gates.append(gate)
        
        return normalized_gates

    def parse(self, text: str) -> CircuitIntent:
        system_prompt = """
You are a quantum computing expert assistant. Analyze user requests for circuits and extract:

- Circuit type (bell_state, ghz_state, teleportation, grovers, custom, etc)
- Number of qubits (default 2-10)
- Parameters (if any)
- Gate sequence (custom circuits)

Gate formats to use:
- Simple gates: "h 0"
- Rotation gates: "rx(pi/3) 0", "ry(pi/3) 0", "rz(pi/6) 1"
- Parametric gates: "u1 0 0.5", "u2 0 0.5 1.2", "u3 0 0.5 1.2 0.7"
- Two-qubit gates: "cx 0 1", "cz 0 1", "cp 0 1 0.5", "swap 0 1"
- Multi control gates: "ccx 0 1 2"
- Measurement: "measure 0 -> 0"
- Reset: "reset 0"
- Barrier: "barrier 0 1 2"
- Conditional: "if(c[2]==1) x 2"

IMPORTANT:
YOU MUST RETURN EVERY SINGLE GATE OPERATION IN AN ARRAY. EACH GATE MUST BE A SEPARATE STRING ELEMENT.
DO NOT GROUP GATES BY TYPE OR CATEGORY.
OUTPUT EACH OPERATION IN ORDER AS A SEPARATE STRING IN THE ARRAY, WITH GATE TYPE + QUBITS.

IMPORTANT: YOUR RESPONSE MUST BE IN VALID JSON FORMAT with this structure:
{
  "circuit_type": "custom",
  "num_qubits": 5,
  "params": {},
  "custom_gates": ["h 0", "cx 0 1", ...],
  "custom_description": "Description of the circuit"
}
"""
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        content = response.choices[0].message.content
        parsed = json.loads(content)

        circuit_type_str = parsed.get("circuit_type", "unknown").upper()
        try:
            circuit_type = CircuitType[circuit_type_str]
        except KeyError:
            circuit_type = CircuitType.CUSTOM if circuit_type_str.lower() == "custom" else CircuitType.UNKNOWN

        params = {
            "num_qubits": min(parsed.get("num_qubits", 2), 10),
            **parsed.get("params", {})
        }

        if circuit_type == CircuitType.CUSTOM:
            params["custom_description"] = parsed.get("custom_description", "Custom quantum circuit")
            raw_gates = parsed.get("custom_gates", [])
            
            # Handle if custom_gates is a dictionary
            if isinstance(raw_gates, dict):
                print("WARNING: custom_gates is a dictionary, flattening to list")
                flattened_gates = []
                for gate_type, gates in raw_gates.items():
                    if isinstance(gates, list):
                        flattened_gates.extend(gates)
                    else:
                        print(f"Warning: Unexpected format for {gate_type}: {gates}")
                        if isinstance(gates, str):
                            flattened_gates.append(gates)
                raw_gates = flattened_gates
            
            # Debug log the raw gates before normalization
            print(f"Raw gates from parser: {raw_gates}")
            
            normalized_gates = self.normalize_gate_instructions(raw_gates)
            params["custom_gates"] = normalized_gates
            
            # Debug log the normalized gates
            print(f"Normalized gates: {normalized_gates}")

        return CircuitIntent(circuit_type, params)

    def parse_circuit_file(self, file_content: str, file_format: str, description: Optional[str] = None) -> tuple:
        if file_format == 'qasm':
            system_prompt = """
You are a quantum computing expert. Analyze and clean OpenQASM. Extract:

- cleaned_qasm
- num_qubits
- description
- gates (as a flat array of individual gate operations)

Gate formats to use:
- Simple gates: "h 0"
- Rotation gates: "rx(pi/3) 0", "ry(pi/3) 0", "rz(pi/6) 1"  (KEEP pi/x notation)
- Two-qubit gates: "cx 0 1", "cz 0 1"
- Multi control gates: "ccx 0 1 2"
- Measurement: "measure 0 -> 0"
- Reset: "reset 0"
- Barrier: "barrier 0 1 2"
- Conditional: "if(c[2]==1) x 2"

IMPORTANT:
YOU MUST RETURN EVERY SINGLE GATE OPERATION AS INDIVIDUAL STRINGS IN THE GATES ARRAY.
DO NOT GROUP GATES BY TYPE OR CATEGORY. THE GATES MUST BE A FLAT ARRAY OF STRINGS.
OUTPUT EACH OPERATION IN ORDER, WITH GATE TYPE + QUBITS.
FOR ROTATION GATES, PRESERVE THE EXACT ANGLE NOTATION (pi/3, pi/6, etc.)

IMPORTANT: YOUR RESPONSE MUST BE IN THIS VALID JSON FORMAT:
{
  "cleaned_qasm": "OPENQASM 2.0; qreg q[5]; creg c[5]; ...",
  "num_qubits": 5,
  "description": "Circuit description",
  "gates": ["h 0", "ry(pi/3) 0", "cx 0 1", ...]
}
"""
        elif file_format == 'qiskit':
            system_prompt = """
You are a quantum computing expert. Analyze and clean Qiskit Python code. Extract:

- cleaned_code
- num_qubits
- description
- gates (as a flat array of individual gate operations)

Gate formats to use:
- Simple gates: "h 0"
- Rotation gates: "rx(pi/3) 0", "ry(pi/3) 0", "rz(pi/6) 1"  (KEEP pi/x notation)
- Two-qubit gates: "cx 0 1", "cz 0 1"
- Multi control gates: "ccx 0 1 2"
- Measurement: "measure 0 -> 0"
- Reset: "reset 0"
- Barrier: "barrier 0 1 2"
- Conditional: "if(c[2]==1) x 2"

IMPORTANT:
YOU MUST RETURN EVERY SINGLE GATE OPERATION AS INDIVIDUAL STRINGS IN THE GATES ARRAY.
DO NOT GROUP GATES BY TYPE OR CATEGORY. THE GATES MUST BE A FLAT ARRAY OF STRINGS.
OUTPUT EACH OPERATION IN ORDER, WITH GATE TYPE + QUBITS.
FOR ROTATION GATES, PRESERVE THE EXACT ANGLE NOTATION (pi/3, pi/6, etc.)

IMPORTANT: YOUR RESPONSE MUST BE IN THIS VALID JSON FORMAT:
{
  "cleaned_code": "from qiskit import QuantumCircuit...",
  "num_qubits": 5,
  "description": "Circuit description",
  "gates": ["h 0", "ry(pi/3) 0", "cx 0 1", ...]
}
"""
        elif file_format == 'json':
            system_prompt = """
You are a quantum computing expert. Analyze and clean JSON circuit. Extract:

- cleaned_json
- num_qubits
- description
- gates (as a flat array of individual gate operations)

Gate formats to use:
- Simple gates: "h 0"
- Rotation gates: "rx(pi/3) 0", "ry(pi/3) 0", "rz(pi/6) 1"  (KEEP pi/x notation)
- Two-qubit gates: "cx 0 1", "cz 0 1"
- Multi control gates: "ccx 0 1 2"
- Measurement: "measure 0 -> 0"
- Reset: "reset 0"
- Barrier: "barrier 0 1 2"
- Conditional: "if(c[2]==1) x 2"

IMPORTANT:
YOU MUST RETURN EVERY SINGLE GATE OPERATION AS INDIVIDUAL STRINGS IN THE GATES ARRAY.
DO NOT GROUP GATES BY TYPE OR CATEGORY. THE GATES MUST BE A FLAT ARRAY OF STRINGS.
OUTPUT EACH OPERATION IN ORDER, WITH GATE TYPE + QUBITS.
FOR ROTATION GATES, PRESERVE THE EXACT ANGLE NOTATION (pi/3, pi/6, etc.)

IMPORTANT: YOUR RESPONSE MUST BE IN THIS VALID JSON FORMAT:
{
  "cleaned_json": "{...}",
  "num_qubits": 5,
  "description": "Circuit description", 
  "gates": ["h 0", "ry(pi/3) 0", "cx 0 1", ...]
}
"""
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

        if description:
            system_prompt += f"\nUser Description: {description}"

        # Try up to 3 times with increasingly explicit instructions
        max_attempts = 3
        for attempt in range(max_attempts):
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": file_content}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            # Check if gates is a dictionary or not in the expected format
            raw_gates = parsed.get("gates", [])
            
            if isinstance(raw_gates, list) and len(raw_gates) > 0 and isinstance(raw_gates[0], str):
                # Success! We have a list of strings
                break
            
            if attempt < max_attempts - 1:
                # If gates is a dictionary, make the prompt more explicit for the next attempt
                if isinstance(raw_gates, dict):
                    print(f"Attempt {attempt+1}: Gates returned as a dictionary, retrying with more explicit instructions")
                    system_prompt += """
CRITICAL CORRECTION NEEDED:
DO NOT RETURN GATES AS A DICTIONARY OR OBJECT. The "gates" field MUST be a flat array of strings.
WRONG: "gates": {"single_qubit_gates": ["h 0"], "two_qubit_gates": ["cx 0 1"]}
CORRECT: "gates": ["h 0", "cx 0 1", "measure 0 -> 0"]
"""
                else:
                    print(f"Attempt {attempt+1}: Gates not in expected format: {raw_gates}, retrying")
                    system_prompt += """
CRITICAL CORRECTION NEEDED:
The "gates" field MUST be a flat array of individual gate operation strings in the exact order they appear in the circuit.
Each gate must be a separate string in the array.
"""

        if file_format == 'qasm':
            cleaned_content = parsed.get("cleaned_qasm", "")
        elif file_format == 'qiskit':
            cleaned_content = parsed.get("cleaned_code", "")
        elif file_format == 'json':
            cleaned_content = parsed.get("cleaned_json", "")

        # Final handling of gates - ensure we always have a flat list of strings
        raw_gates = parsed.get("gates", [])
        
        # If gates is a dictionary, flatten it
        if isinstance(raw_gates, dict):
            print("WARNING: Gates is still a dictionary after multiple attempts, flattening manually")
            flattened_gates = []
            for gate_type, gates in raw_gates.items():
                if isinstance(gates, list):
                    flattened_gates.extend(gates)
                else:
                    print(f"Warning: Unexpected gate format for {gate_type}: {gates}")
                    if isinstance(gates, str):
                        flattened_gates.append(gates)
            raw_gates = flattened_gates
        
        # Ensure all gates are strings
        string_gates = []
        for gate in raw_gates:
            if isinstance(gate, str):
                string_gates.append(gate)
            else:
                print(f"Warning: Non-string gate encountered: {gate}, skipping")
        
        print(f"Parsed {len(string_gates)} gates from {file_format} file: {string_gates}")
        
        normalized_gates = self.normalize_gate_instructions(string_gates)
        
        metadata = {
            "num_qubits": parsed.get("num_qubits", 2),
            "description": parsed.get("description", f"Imported {file_format.upper()} circuit"),
            "gates": normalized_gates
        }

        return cleaned_content, metadata