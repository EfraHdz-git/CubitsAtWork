# Modified app/core/explanation_generator/circuit_explainer.py
from typing import Dict, List, Any, Optional
import os
from ..nlp_processor.intent_parser import CircuitType, CircuitIntent
from qiskit import QuantumCircuit
from openai import OpenAI
import json

class CircuitExplainer:
    """Generates educational explanations for quantum circuits."""
    
    def __init__(self, api_key=None):
        # Use provided API key or environment variable
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        # Initialize OpenAI client if API key is available
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            print(f"OpenAI API key found and loaded for CircuitExplainer")
        else:
            self.client = None
            print("Warning: No OpenAI API key found. Cannot generate circuit explanations.")
    
    def generate_explanation(self, intent: CircuitIntent, circuit: QuantumCircuit) -> Dict[str, Any]:
        """Generate an explanation for a quantum circuit using OpenAI."""
        # Check if OpenAI client is available
        if not self.client:
            return {
                "title": "API Configuration Error",
                "summary": "OpenAI API key is not configured. Please check your environment variables or provide a key.",
                "gates": [],
                "applications": [],
                "educational_value": "",
                "error": "OpenAI API key not found"
            }
        
        try:
            # Prepare circuit information for the prompt
            # Changed to avoid using qubit.index
            circuit_details = {
                "type": intent.circuit_type.value,
                "num_qubits": circuit.num_qubits,
                "operations": [
                    {"name": instruction.name, "qubits": [i for i, _ in enumerate(qargs)]}
                    for instruction, qargs, _ in circuit.data
                ]
            }
            
            # Define the system prompt for OpenAI
            system_prompt = """
            You are a quantum computing professor creating educational content.
            Generate an explanation for a quantum circuit that is:
            1. Educational and suitable for students
            2. Clear in explaining each gate's purpose
            3. Rich with analogies to help understanding
            4. Includes practical applications
            
            IMPORTANT: You must respond ONLY with a valid JSON object containing the following fields:
            {
              "title": "A descriptive title for the circuit",
              "summary": "A brief overview of what the circuit does (1-2 paragraphs)",
              "gates": [
                {
                  "gate": "name of gate operation",
                  "explanation": "detailed explanation of the gate's quantum effect",
                  "analogy": "intuitive analogy to help understand the gate"
                },
                // repeat for each gate or gate pattern
              ],
              "applications": [
                "application 1",
                "application 2",
                // 3-5 practical applications
              ],
              "educational_value": "The educational importance of this circuit (1 paragraph)"
            }
            
            Ensure that your response is properly formatted as valid JSON with no additional text.
            """
            
            user_prompt = f"""
            Please explain this quantum circuit of type {intent.circuit_type.value}:
            
            Number of qubits: {circuit.num_qubits}
            Gate operations: {circuit_details['operations']}
            
            Provide an explanation tailored for students learning quantum computing. Be educational, clear, and include helpful analogies.
            """
            
            # Call OpenAI API
            print(f"Calling OpenAI API for {intent.circuit_type.value} circuit explanation...")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},  # Request JSON format
                temperature=0.7  # Some creativity for analogies
            )
            
            # Extract and parse the response
            content = response.choices[0].message.content
            print(f"Received explanation from OpenAI, content length: {len(content)}")
            
            try:
                # Clean up response if needed
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
                
                # Parse JSON
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON explanation: {e}")
                # Return error information
                return {
                    "title": "JSON Parsing Error",
                    "summary": "There was a problem parsing the explanation from OpenAI.",
                    "gates": [],
                    "applications": [],
                    "educational_value": "",
                    "error": f"JSON parsing error: {str(e)}"
                }
                
        except Exception as e:
            print(f"Error in OpenAI explanation generation: {str(e)}")
            # Return error information
            return {
                "title": "Explanation Generation Error",
                "summary": "There was a problem generating the explanation.",
                "gates": [],
                "applications": [],
                "educational_value": "",
                "error": f"Error: {str(e)}"
            }