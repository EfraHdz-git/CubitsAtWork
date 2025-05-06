# app/core/circuit_builder/openai_circuit_generator.py
from typing import Dict, Any, List, Optional
import os
import json
from qiskit import QuantumCircuit
from openai import OpenAI
from ..nlp_processor.intent_parser import CircuitType

class OpenAICircuitGenerator:
    """Generates quantum circuit structures using OpenAI."""
    
    def __init__(self, api_key=None):
        # Use provided API key or environment variable
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        # Initialize OpenAI client if API key is available
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    def generate_circuit_gates(self, circuit_type: CircuitType, params: Dict[str, Any]) -> List[str]:
        """Generate a gate sequence for a circuit using OpenAI."""
        if not self.client:
            # Fallback to basic implementations if no API key
            return self._get_fallback_circuit_gates(circuit_type, params)
        
        try:
            # Extract parameters
            num_qubits = params.get("num_qubits", self._get_default_qubit_count(circuit_type))
            
            # Create a prompt for OpenAI
            system_prompt = """
            You are a quantum computing expert. Your task is to generate a sequence of quantum gates that 
            implements a specific quantum algorithm or circuit.
            
            The gates should be in the format expected by Qiskit:
            - Simple gates: "h 0" for Hadamard on qubit 0
            - Rotation gates: "rx 0 1.5708" for RX(π/2) on qubit 0
            - Two-qubit gates: "cx 0 1" for CNOT with qubit 0 controlling qubit 1
            
            Use only the following gates:
            - Single-qubit gates: h, x, y, z, s, t, rx, ry, rz
            - Two-qubit gates: cx (CNOT), cz, swap
            - Three-qubit gates: ccx (Toffoli)
            - Measurement: measure
            
            YOUR RESPONSE MUST BE A VALID JSON ARRAY containing ONLY the gate instructions in sequence.
            For example: ["h 0", "cx 0 1", "measure 0", "measure 1"]
            
            Ensure the circuit is valid and properly implements the requested algorithm.
            Do not include explanations, just return the JSON array of gate instructions.
            """
            
            # Create the user prompt based on the circuit type and parameters
            user_prompt = self._create_circuit_prompt(circuit_type, params)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},  # Ensure JSON response
                temperature=0.2  # Low temperature for consistent outputs
            )
            
            # Extract and parse the response
            content = response.choices[0].message.content
            
            try:
                # Clean up response if needed
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                # Parse JSON - handle both array and object responses
                parsed = json.loads(content)
                
                # Handle case where OpenAI returns an object with a gates key
                if isinstance(parsed, dict) and "gates" in parsed:
                    gate_sequence = parsed["gates"]
                # Handle case where OpenAI returns just the array
                elif isinstance(parsed, list):
                    gate_sequence = parsed
                else:
                    raise ValueError("Unexpected response format")
                
                return gate_sequence
                
            except json.JSONDecodeError as e:
                return self._get_fallback_circuit_gates(circuit_type, params)
                
        except Exception as e:
            return self._get_fallback_circuit_gates(circuit_type, params)
    
    def _create_circuit_prompt(self, circuit_type: CircuitType, params: Dict[str, Any]) -> str:
        """Create a prompt for OpenAI based on circuit type and parameters."""
        num_qubits = params.get("num_qubits", self._get_default_qubit_count(circuit_type))
        
        # Base details for all prompts
        base_details = f"""
        Circuit type: {circuit_type.value}
        Number of qubits: {num_qubits}
        
        Generate a sequence of Qiskit gate instructions that implements this circuit.
        """
        
        # Add circuit-specific details
        if circuit_type == CircuitType.BELL_STATE:
            return base_details + """
            Create a Bell state (maximally entangled state) between two qubits.
            The final state should be (|00⟩ + |11⟩)/√2.
            """
        
        elif circuit_type == CircuitType.GHZ_STATE:
            return base_details + f"""
            Create a GHZ state among {num_qubits} qubits.
            The final state should be (|{"0" * num_qubits}⟩ + |{"1" * num_qubits}⟩)/√2.
            """
        
        elif circuit_type == CircuitType.W_STATE:
            return base_details + f"""
            Create a W state among {num_qubits} qubits.
            The W state is an equal superposition of all states with exactly one qubit in state |1⟩.
            For example, for 3 qubits: (|100⟩ + |010⟩ + |001⟩)/√3.
            """
        
        elif circuit_type == CircuitType.TELEPORTATION:
            return base_details + """
            Implement a quantum teleportation circuit.
            The circuit should:
            1. Prepare a state to teleport on qubit 0
            2. Create entanglement between qubits 1 and 2
            3. Perform Bell measurement on qubits 0 and 1
            4. Apply conditional corrections on qubit 2
            """
        
        elif circuit_type == CircuitType.SUPERDENSE_CODING:
            return base_details + """
            Implement a superdense coding protocol.
            The circuit should:
            1. Create an entangled pair (Bell state)
            2. Encode two classical bits by applying operations on one qubit
            3. Measure both qubits to decode the classical information
            """
        
        elif circuit_type == CircuitType.DEUTSCH_JOZSA:
            oracle_type = params.get("oracle_type", "balanced")
            return base_details + f"""
            Implement the Deutsch-Jozsa algorithm with a {oracle_type} oracle function.
            The circuit should:
            1. Initialize all qubits
            2. Apply Hadamard gates
            3. Apply the oracle (assume it's {oracle_type})
            4. Apply Hadamard gates again
            5. Measure all qubits except the ancilla
            """
        
        elif circuit_type == CircuitType.BERNSTEIN_VAZIRANI:
            secret = params.get("secret_string", "101")
            if not secret:
                secret = "101"  # Default secret string
            return base_details + f"""
            Implement the Bernstein-Vazirani algorithm to find the secret string "{secret}".
            The circuit should:
            1. Initialize the qubits
            2. Apply Hadamard gates
            3. Implement an oracle that encodes the secret string "{secret}"
            4. Apply Hadamard gates again
            5. Measure all qubits except the ancilla
            """
        
        elif circuit_type == CircuitType.SIMON:
            return base_details + """
            Implement Simon's algorithm.
            The circuit should:
            1. Initialize all qubits
            2. Apply Hadamard gates to the first register
            3. Apply the oracle (representing a function with a hidden period)
            4. Apply Hadamard gates to the first register again
            5. Measure the first register
            """
        
        elif circuit_type == CircuitType.QFT:
            return base_details + f"""
            Implement the Quantum Fourier Transform on {num_qubits} qubits.
            The circuit should apply the appropriate sequence of Hadamard gates and controlled phase rotations.
            """
        
        elif circuit_type == CircuitType.QPE:
            return base_details + """
            Implement Quantum Phase Estimation.
            The circuit should:
            1. Initialize register qubits in superposition
            2. Apply controlled unitary operations
            3. Apply inverse QFT to the register
            4. Measure the register
            """
        
        elif circuit_type == CircuitType.SHOR:
            return base_details + """
            Implement a simplified version of Shor's algorithm.
            The circuit should demonstrate the key components:
            1. QFT and inverse QFT
            2. Modular exponentiation
            Focus on implementing the quantum part of Shor's algorithm.
            """
        
        elif circuit_type == CircuitType.GROVERS:
            marked_state = params.get("marked_state", "101")
            if not marked_state:
                marked_state = "101"  # Default marked state
            return base_details + f"""
            Implement Grover's search algorithm to find the marked state "{marked_state}".
            The circuit should:
            1. Initialize all qubits in superposition
            2. Apply the oracle that marks the state "{marked_state}"
            3. Apply the diffusion operator
            4. Repeat oracle and diffusion as appropriate
            5. Measure all qubits
            """
        
        elif circuit_type == CircuitType.QAOA:
            return base_details + """
            Implement a basic Quantum Approximate Optimization Algorithm (QAOA) circuit.
            The circuit should:
            1. Prepare the initial state
            2. Apply alternating problem and mixer unitaries
            3. Measure all qubits
            
            Use basic gates to approximate the QAOA operations.
            """
        
        elif circuit_type == CircuitType.VQE:
            return base_details + """
            Implement a basic Variational Quantum Eigensolver (VQE) ansatz circuit.
            The circuit should:
            1. Initialize qubits
            2. Apply parameterized gates (use specific values for rotations)
            3. Implement a simple molecule Hamiltonian simulation
            4. Prepare for measurement
            
            Use basic gates to represent a VQE circuit.
            """
        
        elif circuit_type == CircuitType.QUANTUM_COUNTING:
            return base_details + """
            Implement a Quantum Counting algorithm, which combines QPE with Grover's algorithm.
            The circuit should:
            1. Initialize QPE register and work register
            2. Apply Hadamard gates to all qubits
            3. Apply controlled Grover operators 
            4. Apply inverse QFT to the counting register
            5. Measure the counting register
            """
        
        elif circuit_type == CircuitType.QUANTUM_WALK:
            return base_details + """
            Implement a simple Quantum Walk circuit.
            The circuit should:
            1. Initialize the position and coin registers
            2. Apply the coin operator (Hadamard) to the coin register
            3. Apply the shift operator based on the coin state
            4. Repeat coin and shift operations several times
            5. Measure all qubits
            """
        
        elif circuit_type == CircuitType.HHL:
            return base_details + """
            Implement a simplified version of the HHL algorithm for solving linear systems.
            The circuit should demonstrate the key components:
            1. QPE to determine eigenvalues
            2. Controlled rotations
            3. Inverse QPE
            
            Focus on implementing the core quantum operations of the HHL algorithm.
            """
        
        else:
            return base_details + """
            Generate a general quantum circuit that demonstrates quantum superposition and entanglement.
            """
    
    def _get_default_qubit_count(self, circuit_type: CircuitType) -> int:
        """Get the default number of qubits for a given circuit type."""
        default_qubits = {
            CircuitType.BELL_STATE: 2,
            CircuitType.GHZ_STATE: 3,
            CircuitType.W_STATE: 3,
            CircuitType.TELEPORTATION: 3,
            CircuitType.SUPERDENSE_CODING: 2,
            CircuitType.DEUTSCH_JOZSA: 3,
            CircuitType.BERNSTEIN_VAZIRANI: 4,
            CircuitType.SIMON: 6,
            CircuitType.QFT: 3,
            CircuitType.QPE: 5,
            CircuitType.SHOR: 6,
            CircuitType.GROVERS: 3,
            CircuitType.QAOA: 4,
            CircuitType.VQE: 4,
            CircuitType.QUANTUM_COUNTING: 5,
            CircuitType.QUANTUM_WALK: 4,
            CircuitType.HHL: 5
        }
        return default_qubits.get(circuit_type, 3)
    
    def _get_fallback_circuit_gates(self, circuit_type: CircuitType, params: Dict[str, Any]) -> List[str]:
        """Provide fallback gate sequences when OpenAI is unavailable."""
        num_qubits = params.get("num_qubits", self._get_default_qubit_count(circuit_type))
        
        # Basic fallback circuits
        if circuit_type == CircuitType.BELL_STATE:
            return ["h 0", "cx 0 1"]
        
        elif circuit_type == CircuitType.GHZ_STATE:
            gates = ["h 0"]
            for i in range(num_qubits - 1):
                gates.append(f"cx {i} {i+1}")
            return gates
        
        elif circuit_type == CircuitType.TELEPORTATION:
            return ["h 1", "cx 1 2", "cx 0 1", "h 0", "measure 0", "measure 1", "cx 1 2", "cz 0 2"]
        
        elif circuit_type == CircuitType.QFT:
            # Simple 3-qubit QFT
            return ["h 0", "cp 0 1 1.5708", "cp 0 2 0.7854", "h 1", "cp 1 2 1.5708", "h 2", "swap 0 2"]
        
        # For other circuit types, return a basic circuit that at least creates entanglement
        gates = ["h 0"]
        for i in range(min(3, num_qubits) - 1):
            gates.append(f"cx {i} {i+1}")
        return gates