# app/core/nlp_processor/intent_parser.py
from enum import Enum
from typing import Dict, List, Optional, Tuple
import re
import math

class CircuitType(str, Enum):
    # Circuit types remain the same
    BELL_STATE = "bell_state"
    GHZ_STATE = "ghz_state"
    W_STATE = "w_state"
    TELEPORTATION = "teleportation"
    SUPERDENSE_CODING = "superdense_coding"
    DEUTSCH_JOZSA = "deutsch_jozsa"
    BERNSTEIN_VAZIRANI = "bernstein_vazirani"
    SIMON = "simon"
    QFT = "qft"
    QPE = "qpe"
    SHOR = "shor"
    GROVERS = "grovers"
    QAOA = "qaoa"
    VQE = "vqe"
    QUANTUM_COUNTING = "quantum_counting"
    QUANTUM_WALK = "quantum_walk"
    HHL = "hhl"
    
    # Special handling
    CUSTOM = "custom"
    UNKNOWN = "unknown"

class CircuitIntent:
    def __init__(self, circuit_type: CircuitType, params: Dict = None):
        self.circuit_type = circuit_type
        self.params = params or {}

class SimpleIntentParser:
    """A rule-based intent parser for quantum circuit requests."""
    
    def __init__(self):
        # Keywords that map to circuit types
        self.circuit_keywords = {
            CircuitType.BELL_STATE: ["bell", "bell state", "entangle", "entangled pair"],
            CircuitType.GHZ_STATE: ["ghz", "greenberger", "horne", "zeilinger", "ghz state"],
            CircuitType.W_STATE: ["w state", "w-state"],
            CircuitType.TELEPORTATION: ["teleport", "teleportation", "transfer", "quantum teleportation"],
            CircuitType.SUPERDENSE_CODING: ["superdense", "dense coding", "superdense coding"],
            CircuitType.DEUTSCH_JOZSA: ["deutsch", "jozsa", "deutsch-jozsa", "deutsch jozsa"],
            CircuitType.BERNSTEIN_VAZIRANI: ["bernstein", "vazirani", "bernstein-vazirani"],
            CircuitType.SIMON: ["simon", "simon's algorithm", "simons algorithm"],
            CircuitType.QFT: ["qft", "fourier", "quantum fourier", "quantum fourier transform"],
            CircuitType.QPE: ["qpe", "phase estimation", "quantum phase estimation"],
            CircuitType.SHOR: ["shor", "shor's", "factoring", "factorization"],
            CircuitType.GROVERS: ["grover", "search", "grovers algorithm", "database search"],
            CircuitType.QAOA: ["qaoa", "quantum approximate optimization", "approximate optimization"],
            CircuitType.VQE: ["vqe", "variational", "eigensolver", "variational quantum eigensolver"],
            CircuitType.QUANTUM_COUNTING: ["quantum counting", "counting algorithm"],
            CircuitType.QUANTUM_WALK: ["quantum walk", "quantum random walk"],
            CircuitType.HHL: ["hhl", "linear system", "linear equations", "harrow hassidim lloyd"]
        }
        
        # Gate pattern matches
        self.gate_patterns = {
            "rx": r"rx\s*\(\s*([^)]+)\s*\)\s*(?:on|to)?\s*qubit\s*(\d+)",
            "ry": r"ry\s*\(\s*([^)]+)\s*\)\s*(?:on|to)?\s*qubit\s*(\d+)",
            "rz": r"rz\s*\(\s*([^)]+)\s*\)\s*(?:on|to)?\s*qubit\s*(\d+)",
            "h": r"h(?:adamard)?\s*(?:gate)?\s*(?:on|to)?\s*qubit\s*(\d+)",
            "x": r"x\s*(?:gate)?\s*(?:on|to)?\s*qubit\s*(\d+)",
            "y": r"y\s*(?:gate)?\s*(?:on|to)?\s*qubit\s*(\d+)",
            "z": r"z\s*(?:gate)?\s*(?:on|to)?\s*qubit\s*(\d+)",
            "cnot": r"(?:cnot|cx|controlled-x|controlled\s*x)\s*(?:from|with)?\s*qubit\s*(\d+)\s*(?:to|and|controlling)?\s*qubit\s*(\d+)",
            "cz": r"(?:cz|controlled-z|controlled\s*z)\s*(?:from|with)?\s*qubit\s*(\d+)\s*(?:to|and|controlling)?\s*qubit\s*(\d+)",
        }
    
    def parse_angle(self, angle_str: str) -> float:
        """Parse angle expressions like pi/2, pi/4, etc."""
        angle_str = angle_str.lower().strip()
        
        # Handle pi expressions
        if 'pi' in angle_str:
            # Replace pi with math.pi
            angle_str = angle_str.replace('pi', str(math.pi))
            
            # Evaluate the expression
            try:
                return eval(angle_str)
            except:
                # Default to 0 if we can't parse it
                return 0.0
        
        # Try to convert to float directly
        try:
            return float(angle_str)
        except:
            # Default to 0 if we can't parse it
            return 0.0
    
    def extract_gates(self, text: str) -> List[str]:
        """Extract gate operations from the text."""
        text = text.lower()
        gates = []
        
        # Search for rotation gates with angles
        for gate_name, pattern in self.gate_patterns.items():
            if gate_name in ["rx", "ry", "rz"]:
                # Handle rotation gates with angles
                matches = re.finditer(pattern, text)
                for match in matches:
                    angle_str, qubit = match.groups()
                    angle = self.parse_angle(angle_str)
                    gates.append(f"{gate_name} {qubit} {angle}")
            elif gate_name in ["cnot", "cz"]:
                # Handle 2-qubit gates
                matches = re.finditer(pattern, text)
                for match in matches:
                    control, target = match.groups()
                    gate_cmd = "cx" if gate_name == "cnot" else gate_name
                    gates.append(f"{gate_cmd} {control} {target}")
            else:
                # Handle single qubit gates
                matches = re.finditer(pattern, text)
                for match in matches:
                    qubit = match.groups()[0]
                    gates.append(f"{gate_name} {qubit}")
        
        return gates
    
    def parse(self, text: str) -> CircuitIntent:
        """Parse a natural language request into a circuit intent."""
        text = text.lower()
        
        # Identify circuit type
        circuit_type = CircuitType.UNKNOWN
        highest_score = 0
        
        for c_type, keywords in self.circuit_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > highest_score:
                highest_score = score
                circuit_type = c_type
        
        # Extract gates for potential custom circuit
        gates = self.extract_gates(text)
        
        # If gates found, consider it a custom circuit
        if gates:
            circuit_type = CircuitType.CUSTOM
        
        # Extract parameters
        params = {}
        
        # Try to extract number of qubits
        qubit_matches = re.findall(r'(\d+)\s*qubit', text)
        if qubit_matches:
            try:
                num_qubits = int(qubit_matches[0])
                # Enforce maximum of 10 qubits
                params["num_qubits"] = min(num_qubits, 10)
            except ValueError:
                pass
        
        # If custom circuit, add gates to params
        if circuit_type == CircuitType.CUSTOM and gates:
            params["custom_gates"] = gates
            params["custom_description"] = "Custom quantum circuit with specified gates"
        
        return CircuitIntent(circuit_type, params)