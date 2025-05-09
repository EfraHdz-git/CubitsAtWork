// src/components/CircuitFileUploader.tsx
import { useState, useEffect, useRef } from 'react';
import { ApiService } from '../services/api';
import '../assets/styles/components/CircuitFileUploader.css';

interface Props {
  onCircuitGenerated: (data: any) => void;
  onResetCircuit: () => void;
  onStartGeneration?: () => void;
  onGenerationFailed?: (errorMessage: string) => void;
  isGenerating?: boolean;
}

function CircuitFileUploader({ 
  onCircuitGenerated, 
  onResetCircuit,
  onStartGeneration = () => {},
  onGenerationFailed = () => {},
  isGenerating = false
}: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Listen for reset events
  useEffect(() => {
    const handleReset = () => {
      if (!isGenerating) {
        setError(null);
      }
    };
    
    document.addEventListener('resetInputs', handleReset);
    
    return () => {
      document.removeEventListener('resetInputs', handleReset);
    };
  }, [isGenerating]);

  // Helper function to reset the file input and state
  const resetFileInput = () => {
    if (!isGenerating) {
      setFile(null);
      setError(null);
      
      // Reset the file input element
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0] || null;
    
    if (selectedFile) {
      // Check file extension
      const fileName = selectedFile.name.toLowerCase();
      if (!fileName.endsWith('.qasm') && !fileName.endsWith('.py') && !fileName.endsWith('.json')) {
        setError('Please upload a supported quantum circuit file (.qasm, .py, or .json)');
        return;
      }
      
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleReset = () => {
    resetFileInput();
    onResetCircuit();
  };

  const handleSubmit = async () => {
    if (!file) {
      setError('Please select a circuit file first');
      return;
    }
    
    // Signal to parent that generation is starting
    onStartGeneration();
    setError(null);
    
    try {
      // Use the ApiService to upload the circuit file
      const circuitData = await ApiService.uploadCircuitFile(file);
      
      // Update the parent with the new circuit
      onCircuitGenerated(circuitData);
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred';
      setError(errorMessage);
      
      // Notify parent that generation failed
      onGenerationFailed(errorMessage);
    }
  };

  return (
    <div className="circuit-file-uploader-container">
      <p className="circuit-file-uploader-description">
        Upload a quantum circuit file to import and visualize it.
      </p>
      
      <div className="circuit-file-uploader-form">
        <div className="circuit-file-uploader-input-group">
          <label htmlFor="circuit-file" className="circuit-file-uploader-label">
            Select File:
          </label>
          <div className="circuit-file-uploader-input-wrapper">
            <input
              ref={fileInputRef}
              type="file"
              id="circuit-file"
              className="circuit-file-uploader-input"
              accept=".qasm,.py,.json"
              onChange={handleFileChange}
              disabled={isGenerating}
            />
          </div>
        </div>
        
        <div className="circuit-file-uploader-file-types">
          <p>Supported formats: <span className="formats-inline">.qasm, .py, .json</span></p>
        </div>
      </div>
      
      {error && (
        <div className="circuit-file-uploader-error">
          <p>{error}</p>
          <p className="circuit-file-uploader-error-help">
            Make sure your file is in a supported format (.qasm, .py, or .json).
          </p>
        </div>
      )}
      
      {file && (
        <div className="circuit-file-uploader-selected-file">
          <h4>Selected File:</h4>
          <p className="circuit-file-uploader-filename">{file.name} ({(file.size / 1024).toFixed(2)} KB)</p>
        </div>
      )}
      
      <div className="circuit-file-uploader-button-container">
        {isGenerating ? (
          <div className="circuit-file-uploader-loading">
            <div className="circuit-file-uploader-spinner"></div>
            <span>Generating circuit...</span>
          </div>
        ) : (
          <>
            <button 
              className="secondary circuit-file-uploader-reset-button"
              onClick={handleReset}
              disabled={isGenerating}
            >
              Reset
            </button>
            <button 
              className="primary circuit-file-uploader-button"
              disabled={!file || isGenerating}
              onClick={handleSubmit}
            >
              Generate Circuit
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default CircuitFileUploader;