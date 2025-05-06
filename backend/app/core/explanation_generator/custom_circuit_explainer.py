# app/core/explanation_generator/custom_circuit_explainer.py
from typing import Dict, List, Any, Optional
import os
import json
from qiskit import QuantumCircuit
from ..nlp_processor.intent_parser import CircuitIntent, CircuitType
from openai import OpenAI

class CustomCircuitExplainer:
    """Generates educational explanations specifically for custom quantum circuits."""
    
    def __init__(self, api_key=None):
        # Use provided API key or environment variable
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        # Initialize the OpenAI client if API key is available
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
            print(f"OpenAI API key found and loaded for CustomCircuitExplainer")
        else:
            self.client = None
            print("Warning: No OpenAI API key found. Cannot generate custom circuit explanations.")
    
    def explain_circuit(self, intent: CircuitIntent) -> Dict[str, Any]:
        """Generate a detailed explanation for a custom quantum circuit using OpenAI."""
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
            # Get relevant data from intent
            gates = intent.params.get("custom_gates", [])
            num_qubits = intent.params.get("num_qubits", 2)
            description = intent.params.get("custom_description", "Custom quantum circuit")
            
            # Format gates for better readability in the prompt
            human_readable_gates = [self._format_gate_for_human(gate) for gate in gates]
            
            # Prepare the prompt for OpenAI with explicit JSON instructions
            system_prompt = """
            You are a quantum computing professor teaching a class on quantum circuits. Your task is to explain quantum circuits in detail.
            
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
                // repeat for each gate
              ],
              "applications": [
                "application 1",
                "application 2",
                // 3-5 practical applications
              ],
              "educational_value": "The educational importance of this circuit (1 paragraph)"
            }
            
            Ensure that your response is properly formatted as valid JSON with no additional text before or after the JSON object.
            """
            
            user_prompt = f"""
            Please explain this custom quantum circuit:
            
            Number of qubits: {num_qubits}
            Circuit description: {description}
            Gate sequence:
            {', '.join(human_readable_gates)}
            
            Remember: Your response must be ONLY a JSON object with the fields: title, summary, gates (array), applications (array), and educational_value.
            """
            
            # Call OpenAI API
            print("Calling OpenAI API for custom circuit explanation...")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},  # Specifically request JSON response
                temperature=0.7
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
                
                return json.loads(content)
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON explanation: {e}")
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
            return {
                "title": "Explanation Generation Error",
                "summary": "There was a problem generating the explanation.",
                "gates": [],
                "applications": [],
                "educational_value": "",
                "error": f"Error: {str(e)}"
            }
            
    def _format_gate_for_human(self, gate_str: str) -> str:
        """Convert gate string from internal format to human-readable format."""
        # Implementation remains the same
        parts = gate_str.strip().split()
        gate_type = parts[0].lower()
        
        # Gate formatting logic remains the same...
        # Return the formatted gate string
        return gate_str