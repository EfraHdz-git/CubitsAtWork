# test_enhanced_system.py
import requests
import json
import base64
import matplotlib.pyplot as plt
import io

def test_circuit_generation(text):
    url = "http://localhost:8000/text/generate"
    payload = {"text": text}
    headers = {"Content-Type": "application/json"}
    
    print(f"Sending request for: '{text}'")
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        
        # Print circuit type and explanation
        print(f"\nCircuit Type: {data['circuit_type']}")
        print(f"Number of Qubits: {data['num_qubits']}")
        print(f"\n=== Explanation ===")
        print(f"Title: {data['explanation']['title']}")
        print(f"Summary: {data['explanation']['summary']}")
        
        # Print gates explanation
        print("\nKey Gates:")
        for gate in data['explanation']['gates']:
            print(f"- {gate['gate']}: {gate['explanation']}")
            if gate.get('analogy'):
                print(f"  Analogy: {gate['analogy']}")
        
        # Display applications
        print("\nApplications:")
        for app in data['explanation']['applications']:
            print(f"- {app}")
        
        # Show educational value
        print(f"\nEducational Value: {data['explanation']['educational_value']}")
        
        # Option to display visualizations
        display_viz = input("\nDisplay visualizations? (y/n): ")
        if display_viz.lower() == 'y':
            # Display circuit diagram
            circuit_img = base64.b64decode(data['visualization']['circuit_diagram'])
            circuit_plot = plt.figure(figsize=(10, 6))
            plt.imshow(plt.imread(io.BytesIO(circuit_img)))
            plt.axis('off')
            plt.title("Circuit Diagram")
            plt.show()
            
            # Display Q-sphere if available
            if data['visualization']['q_sphere']:
                qsphere_img = base64.b64decode(data['visualization']['q_sphere'])
                qsphere_plot = plt.figure(figsize=(8, 8))
                plt.imshow(plt.imread(io.BytesIO(qsphere_img)))
                plt.axis('off')
                plt.title("Q-sphere Visualization")
                plt.show()
        
        # Option to display code
        display_code = input("\nDisplay Qiskit code? (y/n): ")
        if display_code.lower() == 'y':
            print("\n=== Qiskit Code ===")
            print(data['exports']['qiskit_code'])
        
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
        test_circuit_generation(test)
        
        if i < len(test_cases) - 1:
            input("\nPress Enter to continue to the next test...")