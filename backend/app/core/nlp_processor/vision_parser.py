# app/core/nlp_processor/vision_parser.py
import os
import json
import base64
from typing import Optional, Dict, Any, List
import re
import math
import traceback
from openai import OpenAI
from .intent_parser import CircuitIntent, CircuitType
from .openai_parser import OpenAICircuitParser
from dotenv import load_dotenv
from fastapi import HTTPException

# Load environment variables
load_dotenv()

class VisionCircuitParser:
    """Uses OpenAI Vision to parse circuit diagrams from images."""
    
    def __init__(self, api_key=None, model="gpt-4o"):
        # Use provided API key or environment variable
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.model = model
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass as parameter.")
        
        # Initialize the OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Create OpenAI parser for reusing gate normalization logic
        self.openai_parser = OpenAICircuitParser(api_key=self.api_key)
    
    async def parse_image(self, image_data: bytes, content_type: str) -> CircuitIntent:
        """Parse a circuit diagram image into a CircuitIntent."""
        print(f"\n==== Vision Parser Request ====")
        print(f"Processing image of type: {content_type}")
        print(f"Using model: {self.model}")
        
        # Encode the image as base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Define the system prompt to instruct the model - enhanced to better align with OpenAI parser
        system_prompt = """
        You are a quantum computing expert specialized in interpreting circuit diagrams and quantum computing notations. 
        Analyze the uploaded image and extract a quantum circuit description.
        
        When analyzing the image, pay special attention to:
        - The number of qubit lines (horizontal lines)
        - Quantum gates shown on the circuit (H, X, Y, Z, CNOT, CZ, T, S, Rx, Ry, Rz, etc.)
        - Control lines connecting gates (vertical lines with control points)
        - Measurement operations (if present)
        - Any special notations or symbols specific to quantum circuits
        
        COMMON QUANTUM CIRCUIT ELEMENTS:
        - H: Hadamard gate (usually a box with 'H')
        - X, Y, Z: Pauli gates
        - Rx, Ry, Rz: Rotation gates (often shown as boxes with curved arrows)
        - CNOT: Controlled-NOT gate (vertical line with a control point and target)
        - CZ: Controlled-Z gate
        - SWAP: Swap gate
        - T, S: Phase gates
        
        The image might contain one of these standard circuits:
        - bell_state: Bell state or entangled pair
        - ghz_state: GHZ state (multi-qubit entanglement)
        - w_state: W state (another type of entangled state)
        - teleportation: Quantum teleportation circuit
        - superdense_coding: Superdense coding protocol
        - deutsch_jozsa: Deutsch-Jozsa algorithm
        - bernstein_vazirani: Bernstein-Vazirani algorithm
        - simon: Simon's algorithm
        - qft: Quantum Fourier Transform (sequence of H gates followed by controlled rotation gates)
        - qpe: Quantum Phase Estimation
        - shor: Shor's algorithm (factorization)
        - grovers: Grover's search algorithm
        - custom: For any other circuit that doesn't match the above
        
        Extract the precise gate sequence. Format gate operations as follows:
        - Hadamard: "h 0" for Hadamard on qubit 0
        - CNOT: "cx 0 1" for CNOT with qubit 0 controlling qubit 1
        - Controlled-Phase: "cp(pi/2) 0 1" for π/2 phase gate with qubit 0 controlling qubit 1
        - Rotation gates: "rx(pi/2) 0" for RX(π/2) on qubit 0
        - Measurement: "measure 0 -> 0" to measure qubit 0 to classical bit 0
        
        For rotation gates, KEEP THE ORIGINAL MATHEMATICAL EXPRESSIONS:
        - Use expressions like "rx(pi/2) 0" instead of converting to decimal values
        - Use "ry(pi/4) 1" for RY(π/4) on qubit 1
        - Use "rz(pi/8) 2" for RZ(π/8) on qubit 2
        - For arbitrary angles, use the pi notation when possible: "rx(3*pi/4) 0"
        
        CRITICAL: You MUST provide a detailed 'custom_description' that explains:
        - What the circuit aims to accomplish
        - The purpose or function of the main gate sequences
        - The expected quantum state or measurement outcomes
        - Any notable quantum phenomena involved (entanglement, superposition, interference, etc.)
        
        Example descriptions:
        - "Bell state preparation circuit that creates quantum entanglement between two qubits using a Hadamard gate followed by CNOT"
        - "Quantum teleportation protocol that transfers the state of qubit 0 to qubit 2 using entanglement and classical communication"
        - "Phase estimation circuit that determines eigenvalues of a unitary operator using quantum Fourier transform"
        
        YOUR RESPONSE MUST BE A VALID JSON OBJECT with these fields:
        - circuit_type: The identified circuit type (one of the above options)
        - num_qubits: Number of qubits (integer, maximum 10)
        - custom_description: Detailed description of what the circuit does (MANDATORY)
        - custom_gates: Array of gate operations in sequence with precise formatting
        
        IMPORTANT: "custom_gates" must be a flat array of strings, NOT grouped by type.
        CORRECT FORMAT: "custom_gates": ["h 0", "cx 0 1", "measure 0 -> 0"]
        INCORRECT FORMAT: "custom_gates": {"h_gates": ["h 0"], "cx_gates": ["cx 0 1"]}
        
        If you see a multi-qubit circuit with sophisticated structure, be sure to identify all qubits and operations accurately.
        """
        
        try:
            print("Calling OpenAI Vision API...")
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model=self.model,  # Current model with vision capabilities
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user", 
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{content_type};base64,{base64_image}"
                                }
                            },
                            {
                                "type": "text",
                                "text": "Analyze this quantum circuit diagram and extract all details. Return a valid JSON object with circuit_type, num_qubits, custom_description, and custom_gates as a flat array of strings. Make sure to include a detailed custom_description explaining what the circuit does."
                            }
                        ]
                    }
                ],
                max_tokens=2000  # Increased for more detailed analysis
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            print(f"Vision API response content: {content}")
            
            # Try to extract JSON from the response (up to 3 attempts with increasingly explicit error messages)
            attempts = 0
            max_attempts = 3
            
            while attempts < max_attempts:
                try:
                    # Try to find JSON in the response
                    json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                        print(f"Extracted JSON from code block: {json_str}")
                    else:
                        # Look for a JSON object directly
                        json_match = re.search(r'(\{[\s\S]*?\})', content, re.DOTALL)
                        if json_match:
                            json_str = json_match.group(1)
                            print(f"Extracted JSON from text: {json_str}")
                        else:
                            print("No JSON format found in response, cannot process")
                            raise HTTPException(status_code=422, detail="Failed to extract circuit data from image. The AI could not identify a valid quantum circuit.")
                    
                    # Clean up the string to help with parsing
                    json_str = json_str.strip()
                    if not json_str.startswith('{'): 
                        print(f"JSON string doesn't start with '{{': {json_str[:20]}")
                        raise HTTPException(status_code=422, detail="Invalid JSON format in AI response. Could not process the circuit image.")
                    
                    parsed_data = json.loads(json_str)
                    print(f"Parsed JSON data: {json.dumps(parsed_data, indent=2)}")
                    
                    # Extract circuit type
                    circuit_type_str = parsed_data.get("circuit_type", "custom").upper()
                    try:
                        circuit_type = CircuitType[circuit_type_str]
                    except KeyError:
                        print(f"Unknown circuit type: {circuit_type_str}, defaulting to CUSTOM")
                        circuit_type = CircuitType.CUSTOM
                    
                    # Extract parameters
                    num_qubits = min(parsed_data.get("num_qubits", 2), 10)  # Limit to 10 qubits max
                    
                    # Prepare parameters
                    params = {
                        "num_qubits": num_qubits
                    }
                    
                    # Extract gate sequence and description
                    if "custom_gates" not in parsed_data or not parsed_data["custom_gates"]:
                        raise HTTPException(status_code=422, detail="No gate sequence found in the circuit image analysis. Please try with a clearer image.")
                    
                    # Get custom description from the response or generate one if missing
                    custom_description = ""
                    if "custom_description" not in parsed_data or not parsed_data["custom_description"] or parsed_data["custom_description"].strip() in ["", "Custom quantum circuit", "Custom quantum circuit from image"]:
                        print("Missing or generic description detected, generating a better one...")
                        # Generate a description based on the gate sequence
                        raw_gates = parsed_data.get("custom_gates", [])
                        gate_description = ""
                        
                        if isinstance(raw_gates, list):
                            gate_description = "\n".join([str(gate) for gate in raw_gates if gate])
                        elif isinstance(raw_gates, dict):
                            gate_description = "\n".join([f"{k}: {v}" for k, v in raw_gates.items()])
                        
                        # Make a follow-up API call to generate a better description
                        description_response = self.client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a quantum computing expert. Based on the gate sequence, provide a detailed explanation of what this quantum circuit does, its purpose, and any quantum phenomena it demonstrates."},
                                {"role": "user", "content": f"This is a quantum circuit with {num_qubits} qubits and the following gate sequence:\n{gate_description}\n\nProvide a detailed explanation of what this circuit does in 2-4 sentences."}
                            ],
                            max_tokens=200
                        )
                        custom_description = description_response.choices[0].message.content.strip()
                        print(f"Generated description: {custom_description}")
                    else:
                        custom_description = parsed_data["custom_description"]
                        print(f"Using provided description: {custom_description}")
                    
                    params["custom_description"] = custom_description
                    
                    # Process gates
                    raw_gates = parsed_data.get("custom_gates", [])
                    
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
                    
                    # Ensure all gates are strings
                    string_gates = []
                    for gate in raw_gates:
                        if isinstance(gate, str):
                            string_gates.append(gate)
                        else:
                            print(f"Warning: Non-string gate encountered: {gate}, skipping")
                    
                    print(f"Raw gates from Vision: {string_gates}")
                    
                    # Use the same gate normalization logic as the text parser
                    normalized_gates = self.openai_parser.normalize_gate_instructions(string_gates)
                    params["custom_gates"] = normalized_gates
                    
                    # Generate explanation structure for the EducationalExplanation component
                    # Use OpenAI to generate detailed gate explanations directly as an enriched JSON
                    print("Generating quantum circuit explanation...")
                    
                    # Build the prompt for generating explanations
                    circuit_title = f"Quantum Circuit Analysis: {circuit_type_str.capitalize()}"
                    if circuit_type == CircuitType.CUSTOM:
                        circuit_title = "Quantum Circuit Analysis: Custom Circuit"
                    
                    explanation_prompt = f"""
                    You are a quantum computing educator. Create an educational explanation for a quantum circuit with the following properties:
                    
                    CIRCUIT DESCRIPTION:
                    {custom_description}
                    
                    GATE SEQUENCE:
                    {' '.join(normalized_gates)}
                    
                    NUMBER OF QUBITS: {num_qubits}
                    
                    FORMAT YOUR RESPONSE AS A JSON OBJECT with these fields:
                    1. title - A concise title for this quantum circuit
                    2. summary - Explanation of what this circuit does (can reuse the description)
                    3. gates - Array of objects with these properties:
                       - gate: The gate name and parameters (e.g., "h 0", "cx 0 1")
                       - explanation: How this gate functions in the circuit (1-2 sentences)
                       - analogy: A simple analogy to aid understanding (optional)
                    4. applications - Array of 3-5 potential applications for this type of circuit
                    5. educational_value - How studying this circuit helps understand quantum computing
                    
                    LIMIT the gates array to the 4-5 most important gates in the circuit.
                    
                    Write the JSON in a clear, educational tone suitable for beginners learning quantum computing.
                    """
                    
                    # Call OpenAI to generate the explanation
                    explanation_response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": explanation_prompt},
                            {"role": "user", "content": "Generate a detailed educational explanation for this quantum circuit."}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.7,
                        max_tokens=1000
                    )
                    
                    # Extract and parse the explanation
                    explanation_content = explanation_response.choices[0].message.content
                    print(f"Generated explanation: {explanation_content[:200]}...")
                    
                    try:
                        explanation_data = json.loads(explanation_content)
                        
                        # CRITICAL FIX: Set the "explanation" field explicitly at the top level
                        # This ensures it will be seen by the API response handler
                        print("Setting explanation directly as a top-level attribute")
                        
                        # Make sure to include all fields the frontend expects
                        final_explanation = {
                            "title": explanation_data.get("title", circuit_title),
                            "summary": explanation_data.get("summary", custom_description),
                            "gates": explanation_data.get("gates", []),
                            "applications": explanation_data.get("applications", [
                                "Quantum computing education", 
                                "Quantum algorithm implementation", 
                                "Quantum information processing"
                            ]),
                            "educational_value": explanation_data.get("educational_value", 
                                "Understanding quantum circuit principles and gate operations.")
                        }
                        
                        # Directly attach the explanation to both places it might be used
                        params["explanation"] = final_explanation
                        
                        print(f"Final explanation structure for API: {json.dumps(final_explanation, indent=2)}")
                    except json.JSONDecodeError as e:
                        print(f"Error parsing explanation JSON: {e}")
                        # Create a minimal explanation structure as fallback
                        params["explanation"] = {
                            "title": circuit_title,
                            "summary": custom_description,
                            "gates": [],
                            "applications": ["Quantum computation", "Quantum algorithms", "Quantum information processing"],
                            "educational_value": "Understanding quantum circuit principles and gate operations."
                        }
                    
                    # Add any additional parameters for predefined circuits
                    if "params" in parsed_data:
                        params.update(parsed_data["params"])
                    
                    # Add debugging information
                    print("==== Vision Parser Results ====")
                    print(f"Circuit type: {circuit_type}")
                    print(f"Num qubits: {num_qubits}")
                    print(f"Custom description: {params.get('custom_description', 'No description')}")
                    print(f"Custom gates: {params.get('custom_gates', [])}")
                    print(f"Explanation structure: {bool(params.get('explanation'))}")
                    print("================================")
                    
                    result = CircuitIntent(circuit_type, params)
                    
                    # CRITICAL FIX: Ensure the explanation is stored as direct instance attribute
                    # This ensures it will persist through any transformations 
                    if "explanation" in params:
                        setattr(result, "explanation", params["explanation"])
                        print(f"IMPORTANT: Added explanation as direct attribute to CircuitIntent result!")
                    
                    return result
                    
                except json.JSONDecodeError as e:
                    attempts += 1
                    print(f"Attempt {attempts}: Failed to parse JSON: {e}")
                    
                    if attempts >= max_attempts:
                        print(f"Failed to parse JSON from Vision API response after {max_attempts} attempts: {e}")
                        print(f"Response content: {content[:500]}...")  # Print first 500 chars for debugging
                        raise HTTPException(status_code=422, detail="Could not understand the quantum circuit in the image. Please try with a clearer image.")
                    
                    # Try again with a different approach
                    json_str = content.strip()
                    # Remove any non-JSON content before the first { and after the last }
                    start_idx = json_str.find('{')
                    end_idx = json_str.rfind('}')
                    if start_idx != -1 and end_idx != -1:
                        json_str = json_str[start_idx:end_idx + 1]
                        print(f"Cleaned JSON string, attempt {attempts+1}: {json_str[:100]}...")
                
        except HTTPException as he:
            # Re-raise HTTP exceptions directly
            raise he
        except Exception as e:
            error_details = traceback.format_exc()
            print(f"Exception during Vision API call: {str(e)}\n{error_details}")
            raise HTTPException(status_code=500, detail=f"Error processing circuit image: {str(e)}")