// src/components/CodeDisplay.tsx
import { useState, useEffect, useRef } from 'react';
import { CircuitResponse } from '../services/api';
import '../assets/styles/components/CodeDisplay.css';

interface Props {
  circuitData: CircuitResponse | null;
}

function CodeDisplay({ circuitData }: Props) {
  const [format, setFormat] = useState('qiskit');
  const [code, setCode] = useState('');
  const [editableCode, setEditableCode] = useState('');
  const [copied, setCopied] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const API_BASE_URL = 'http://localhost:8000';

  useEffect(() => {
    if (!circuitData || !circuitData.exports) return;
    
    // Select the code based on the chosen format
    let selectedCode = '';
    switch (format) {
      case 'qiskit':
        selectedCode = circuitData.exports.qiskit_code || '# No Qiskit code available';
        break;
      case 'qasm':
        selectedCode = circuitData.exports.qasm_code || '// No QASM code available';
        break;
      case 'json':
        selectedCode = circuitData.exports.json_code || '{}';
        break;
      default:
        selectedCode = '';
    }
    
    setCode(selectedCode);
    setEditableCode(selectedCode);
    setIsEditing(false);
  }, [circuitData, format]);

  useEffect(() => {
    if (isEditing && textareaRef.current) {
      textareaRef.current.focus();
    }
  }, [isEditing]);

  const handleCopy = () => {
    const textToCopy = isEditing ? editableCode : code;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    // Special handling for Jupyter Notebook format
    if (format === 'jupyter') {
      const circuitId = circuitData?.circuit_type || 'custom';
      const apiUrl = `${API_BASE_URL}/exports/jupyter?circuit_type=${encodeURIComponent(circuitData?.circuit_type || 'custom')}&num_qubits=${circuitData?.num_qubits || 2}`;
      
      const a = document.createElement('a');
      a.href = apiUrl;
      a.download = `quantum_circuit_${circuitId}.ipynb`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      return;
    }
    
    // Normal handling for other formats
    const textToDownload = isEditing ? editableCode : code;
    const blob = new Blob([textToDownload], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    let extension = '.txt';
    if (format === 'qiskit') extension = '.py';
    if (format === 'qasm') extension = '.qasm';
    if (format === 'json') extension = '.json';
    a.download = `quantum_circuit_${format}${extension}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const toggleEditMode = () => {
    if (isEditing) {
      setCode(editableCode);
    }
    setIsEditing(!isEditing);
  };

  const handleCodeChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setEditableCode(e.target.value);
  };

  if (!circuitData) {
    return (
      <div className="card code-display-container">
        <h2 className="code-display-heading">Generated Code</h2>
        <div className="code-display-placeholder">
          Generate a circuit to see code
        </div>
      </div>
    );
  }

  return (
    <div className="card code-display-container">
      <div className="code-display-header">
        <h2 className="code-display-heading">Generated Code</h2>
        <div className="code-display-controls">
          <select 
            className="code-display-select"
            value={format} 
            onChange={(e) => setFormat(e.target.value)}
            disabled={isEditing}
          >
            <option value="qiskit">Qiskit</option>
            <option value="qasm">QASM</option>
            <option value="json">JSON</option>
            <option value="jupyter">Jupyter Notebook</option>
          </select>
          <button 
            className={`secondary ${isEditing ? 'active' : ''}`} 
            onClick={toggleEditMode}
            disabled={!code || format === 'jupyter'}
          >
            {isEditing ? "Save" : "Edit"}
          </button>
          <button 
            className="primary" 
            onClick={handleCopy} 
            disabled={!code || format === 'jupyter'}
          >
            {copied ? "Copied!" : "Copy"}
          </button>
          <button 
            className="primary" 
            onClick={handleDownload} 
            disabled={!circuitData}
          >
            Download
          </button>
        </div>
      </div>
      
      {format === 'jupyter' ? (
        <div className="jupyter-note-container">
          <div className="jupyter-info">
            <h3>Jupyter Notebook Export</h3>
            <p>
              This will download a Jupyter Notebook (.ipynb) file containing the complete circuit implementation, 
              visualization code, and simulation code.
            </p>
            <p>
              You can open this notebook in:
            </p>
            <ul>
              <li>Local Jupyter installation</li>
              <li>Google Colab</li>
              <li>IBM Quantum Lab</li>
              <li>Any other Jupyter-compatible environment</li>
            </ul>
            <p className="jupyter-note">
              Click the <strong>Download</strong> button to get the notebook file.
            </p>
          </div>
        </div>
      ) : isEditing ? (
        <textarea
          ref={textareaRef}
          className="code-display-textarea"
          value={editableCode}
          onChange={handleCodeChange}
          spellCheck="false"
        />
      ) : (
        <pre className="code-display-pre code-block">
          <code className="code-display-code">
            {code || '# Generate a circuit to see code'}
          </code>
        </pre>
      )}
    </div>
  );
}

export default CodeDisplay;