# test_simple.py
import requests
import json

def test_circuit_generation(text):
    url = "http://localhost:8000/text/generate"
    payload = {"text": text}
    headers = {"Content-Type": "application/json"}
    
    print(f"Sending request for: '{text}'")
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        # Print circuit type
        print(f"\nCircuit Type: {data['circuit_type']}")
        print(f"Number of Qubits: {data['num_qubits']}")
        
        # Print explanation if available
        if data.get('explanation') and data['explanation'].get('summary'):
            print(f"\nExplanation: {data['explanation']['summary'][:200]}...")
        
        # Check if visualization was successful
        if data.get('visualization') and data['visualization'].get('circuit_diagram'):
            print("\nCircuit diagram generated successfully.")
        else:
            print("\nNo circuit diagram available.")
        
        # Check if code generation was successful
        if data.get('exports') and data['exports'].get('qiskit_code'):
            print("\nQiskit code generated successfully.")
            
            # Print a snippet of the code
            code_snippet = data['exports']['qiskit_code'].split('\n')
            print("\nCode snippet:")
            print('\n'.join(code_snippet[:5]) + "\n...")
        else:
            print("\nNo Qiskit code available.")
            
        return data
    else:
        print(f"Error: {response.text}")
        return None

if __name__ == "__main__":
    test_cases = [
        "Create a Bell state circuit",
        "Generate a quantum teleportation circuit",
        "I need a 3-qubit GHZ state",
        "Create a circuit for Grover's algorithm with 3 qubits",
        "Generate a QFT circuit with 4 qubits"
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\n===== Test Case {i+1}/{len(test_cases)} =====")
        result = test_circuit_generation(test)
        
        if i < len(test_cases) - 1:
            input("\nPress Enter to continue to the next test...")