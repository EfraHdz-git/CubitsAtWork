import json
import requests
import base64
import io
import matplotlib.pyplot as plt

def send_text_to_api(text):
    print(f"\n🧪 Testing input: '{text}'")
    try:
        response = requests.post("http://localhost:8000/text/generate", json={"text": text})
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

    data = response.json()
    print(f"✅ Response received - Type: {data['circuit_type']}, Qubits: {data['num_qubits']}")

    print(f"\n📘 {data['explanation']['title']}")
    print(f"{data['explanation']['summary']}")
    print(f"\n🧱 Gates:")
    for g in data['explanation']['gates']:
        print(f" - {g['gate']}: {g['explanation']}")
        if g.get('analogy'):
            print(f"   ↪ Analogy: {g['analogy']}")

    print("\n🎯 Applications:")
    for app in data['explanation']['applications']:
        print(f" - {app}")

    print(f"\n📚 Educational Value: {data['explanation']['educational_value']}")
    return data


def show_visuals(data):
    show = input("\n🎨 Show visualizations? (y/n): ").lower() == 'y'
    if not show:
        return

    def decode_and_plot(title, base64_str):
        if not base64_str:
            return
        img_data = base64.b64decode(base64_str)
        img = plt.imread(io.BytesIO(img_data))
        plt.figure(figsize=(8, 6))
        plt.imshow(img)
        plt.axis('off')
        plt.title(title)
        plt.show()

    decode_and_plot("Circuit Diagram", data['visualization'].get('circuit_diagram'))
    decode_and_plot("Q-sphere", data['visualization'].get('q_sphere'))


def show_code(data):
    show = input("\n💻 Show Qiskit code? (y/n): ").lower() == 'y'
    if show:
        print("\n=== Qiskit Code ===")
        print(data['exports']['qiskit_code'])


if __name__ == "__main__":
    test_inputs = [
        "Create a Bell state circuit",
        "Generate a quantum teleportation circuit",
        "I need a 3-qubit GHZ state",
        "Create a circuit for Grover's algorithm with 3 qubits",
        "Generate a QFT circuit with 4 qubits",
        "Build a circuit for Deutsch-Jozsa algorithm",
        "Create a quantum walk circuit with 3 steps"
    ]

    for i, query in enumerate(test_inputs):
        print(f"\n========= Test {i+1}/{len(test_inputs)} =========")
        result = send_text_to_api(query)
        if result:
            show_visuals(result)
            show_code(result)
        if i < len(test_inputs) - 1:
            input("\n➡ Press Enter for next test...")
