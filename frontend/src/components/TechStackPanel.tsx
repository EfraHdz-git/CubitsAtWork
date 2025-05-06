import React, { useState } from 'react';
import '../assets/styles/components/TechStackPanel.css';

const TechStackPanel: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  const togglePanel = () => {
    setIsExpanded(!isExpanded);
  };
  
  return (
    <div className="tech-stack-panel">
      <button 
        className={`tech-stack-toggle ${isExpanded ? 'expanded' : ''}`} 
        onClick={togglePanel}
      >
        <i className="bi bi-code-square"></i>
        <span>Tech Stack</span>
        <i className={`bi ${isExpanded ? 'bi-chevron-up' : 'bi-chevron-down'}`}></i>
      </button>

      {isExpanded && (
        <div className="tech-stack-content">
          <h5 className="tech-stack-heading">Current Implementation</h5>
          <div className="tech-grid">
            <div className="tech-column">
              <h6 className="tech-category">Frontend</h6>
              <ul className="tech-list">
                <li><span className="tech-badge react">React</span> UI framework</li>
                <li><span className="tech-badge vite">Vite</span> Build tool</li>
                <li><span className="tech-badge ts">TypeScript</span> Type safety</li>
                <li><span className="tech-badge css">CSS</span> Styling & layout</li>
              </ul>
            </div>
            <div className="tech-column">
              <h6 className="tech-category">Backend</h6>
              <ul className="tech-list">
                <li><span className="tech-badge fastapi">FastAPI</span> Python framework</li>
                <li><span className="tech-badge python">Python</span> Server-side logic</li>
                <li><span className="tech-badge opencv">OpenCV</span> Image processing</li>
                <li><span className="tech-badge rest">REST API</span> Client-server comm</li>
              </ul>
            </div>
            <div className="tech-column">
              <h6 className="tech-category">Quantum & AI</h6>
              <ul className="tech-list">
                <li><span className="tech-badge qiskit">Qiskit</span> Quantum circuits</li>
                <li><span className="tech-badge qasm">QASM</span> Circuit interchange</li>
                <li><span className="tech-badge openai">OpenAI</span> Vision & explanation</li>
                <li><span className="tech-badge matplotlib">Matplotlib</span> Visualizations</li>
              </ul>
            </div>
          </div>

          <hr className="tech-divider" />

          <h5 className="tech-stack-heading">Future Enhancements</h5>
          <div className="tech-grid">
            <div className="tech-column">
              <h6 className="tech-category">Real Quantum Access</h6>
              <ul className="tech-list">
                <li><span className="tech-badge ibmq">IBM Quantum</span> Real device execution</li>
                <li><span className="tech-badge cloud">Cloud QPU</span> Hosted quantum solutions</li>
                <li><span className="tech-badge qcloud">Quantum Cloud</span> Multi-provider access</li>
              </ul>
            </div>
            <div className="tech-column">
              <h6 className="tech-category">Advanced AI & ML</h6>
              <ul className="tech-list">
                <li><span className="tech-badge ml">ML Models</span> Circuit optimization</li>
                <li><span className="tech-badge huggingface">HuggingFace</span> Specialized models</li>
                <li><span className="tech-badge finetune">Fine-tuned</span> Domain-specific LLMs</li>
              </ul>
            </div>
            <div className="tech-column">
              <h6 className="tech-category">Integration & Features</h6>
              <ul className="tech-list">
                <li><span className="tech-badge realtime">Real-time</span> Collaborative editing</li>
                <li><span className="tech-badge vr">VR/AR</span> 3D circuit visualization</li>
                <li><span className="tech-badge blockchain">Blockchain</span> Result certification</li>
              </ul>
            </div>
          </div>

          <div className="tech-footer">
            <p>CubitsAtWork transforms quantum circuit development through AI-powered tools and intuitive interfaces.</p>
            <p>Designed as a PoC to lower the barrier to entry for quantum computing while providing powerful tools for experts.</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default TechStackPanel;