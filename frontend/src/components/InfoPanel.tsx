import React from 'react';
import '../assets/styles/components/InfoPanel.css';

interface InfoPanelProps {
  showIcon?: boolean;
}

const InfoPanel: React.FC<InfoPanelProps> = ({ showIcon = false }) => (
  <div className="info-panel">
    {showIcon && (
      <div className="info-panel-circle">
        <i className="bi bi-info-circle"></i>
      </div>
    )}
    <h2 className={`info-panel-title ${showIcon ? 'with-icon' : ''}`}>CubitsAtWork</h2>
    
    <div className="info-section">
      <h5><span className="icon">🔍</span> Problem</h5>
      <p>Quantum circuit development has several challenges:</p>
      <ul>
        <li>High barrier to entry for newcomers to quantum computing</li>
        <li>Manual circuit creation is time-consuming and error-prone</li>
        <li>Difficult to visualize and understand complex quantum operations</li>
        <li>Limited accessibility to quantum circuit design tools</li>
      </ul>
    </div>

    <div className="info-section">
      <h5><span className="icon">💡</span> Solution</h5>
      <p>A versatile quantum circuit creation platform that:</p>
      <ul>
        <li>Generates circuits from natural language descriptions</li>
        <li>Converts circuit images to digital quantum circuits</li>
        <li>Transforms templates into customizable circuits</li>
        <li>Imports from various formats (JSON/Python/QASM)</li>
        <li>Provides detailed gate-by-gate explanations</li>
        <li>Simulates circuits with visualization of results</li>
      </ul>
    </div>

    <div className="info-section">
      <h5><span className="icon">📊</span> Benefits</h5>
      <ul>
        <li>Accelerates quantum circuit development workflow</li>
        <li>Makes quantum computing accessible to broader audiences</li>
        <li>Enhances understanding through visual explanations</li>
        <li>Provides exportable code for further development</li>
        <li>Offers immediate simulation feedback</li>
      </ul>
    </div>

    <div className="info-section">
      <h5><span className="icon">🎯</span> Who It's For</h5>
      <div className="badge-container">
        <span className="info-badge">Researchers</span>
        <span className="info-badge">Educators</span>
        <span className="info-badge">Students</span>
        <span className="info-badge">Quantum Developers</span>
        <span className="info-badge">Industry Professionals</span>
      </div>
    </div>
  </div>
);

export default InfoPanel;