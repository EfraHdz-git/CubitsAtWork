
# CubitsAtWork

AI-powered quantum circuit generator that transforms natural language, images, and templates into interactive quantum circuits. 
Provides circuit explanations, simulations, and exportable formats to accelerate quantum computing exploration.

## 🚀 Features

- Generate quantum circuits from natural language descriptions
- Convert circuit images to digital quantum circuits
- Transform templates into customizable circuits
- Import circuits from JSON, QASM, Python
- Detailed gate-by-gate explanations
- Circuit visualization and simulation
- Export to Qiskit, QASM, and more

## 🧠 Tech Stack

**Frontend**
- React (UI Framework)
- Vite (Build Tool)
- TypeScript (Type Safety)
- CSS (Styling and Layout)

**Backend**
- FastAPI (Python Framework)
- OpenCV (Image Processing)
- Qiskit (Quantum Circuits)
- Matplotlib (Visualizations)
- IBM Cloud (API Hosting)

**AI & ML**
- OpenAI (Vision and Explanation)
- Future: HuggingFace models, domain-specific LLMs

## 🌐 Live Project

[https://cubitsatwork.efraprojects.com](https://cubitsatwork.efraprojects.com)

## 📦 Installation (Dev)

```bash
git clone https://github.com/EfraHdz-git/CubitsAtWork.git
cd CubitsAtWork
# Backend setup (inside backend folder)
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
pip install -r requirements.txt

# Frontend setup (inside frontend folder)
npm install
npm run dev
```

## ⚡ Environment Variables

You must create a `.env` file in the backend with:

```
OPENAI_API_KEY=your_openai_key_here
```

## 📌 Notes

- This is a PoC project built for rapid experimentation and showcasing AI-assisted quantum circuit generation.
- Designed to lower the barrier to entry for quantum computing while still offering expert-level capabilities.

## 📖 License

MIT License
