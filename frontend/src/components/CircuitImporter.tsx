// src/components/CircuitImporter.tsx
import { useState, useEffect, useRef } from 'react';
import { ApiService } from '../services/api';
import '../assets/styles/components/CircuitImporter.css';

interface Props {
  type: 'image' | 'file';
  onCircuitGenerated: (data: any) => void;
  onResetCircuit: () => void;
  onStartGeneration?: () => void;
  onGenerationFailed?: (errorMessage: string) => void;
  isGenerating?: boolean;
}

function CircuitImporter({ 
  type, 
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
      // Validate file type for images
      if (type === 'image' && !selectedFile.type.startsWith('image/')) {
        setError('Please upload an image file');
        return;
      }
      
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };
  
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      
      // Validate file type
      if (type === 'image' && !droppedFile.type.startsWith('image/')) {
        setError('Please upload an image file');
        return;
      }
      
      if (type === 'file' && !['application/json', 'text/plain', 'text/x-python', 'application/octet-stream'].includes(droppedFile.type)) {
        setError('Please upload a supported file format (.qasm, .py, .json, .txt)');
        return;
      }
      
      setFile(droppedFile);
      setError(null);
    }
  };

  const handleReset = () => {
    resetFileInput();
    onResetCircuit();
  };

  const handleSubmit = async () => {
    if (!file) {
      setError(`Please select a ${type === 'image' ? 'circuit image' : 'circuit file'} first`);
      return;
    }
    
    // Signal to parent that generation is starting
    onStartGeneration();
    setError(null);
    
    try {
      let circuitData;
      
      if (type === 'image') {
        // Use the ApiService to upload the circuit image
        circuitData = await ApiService.uploadCircuitImage(file);
      } else {
        // Use the ApiService to upload the circuit file
        circuitData = await ApiService.uploadCircuitFile(file);
      }
      
      // Update the parent with the new circuit
      onCircuitGenerated(circuitData);
      
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred';
      setError(errorMessage);
      
      // Notify parent that generation failed
      onGenerationFailed(errorMessage);
    }
  };

  // Helper function to render file preview
  const renderFilePreview = () => {
    if (!file) return null;

    if (type === 'image' && file.type.startsWith('image/')) {
      return (
        <div className="circuit-importer-file-preview">
          <img 
            src={URL.createObjectURL(file)} 
            alt="Circuit preview" 
            className="circuit-importer-image-preview" 
          />
          <p className="circuit-importer-filename">{file.name}</p>
          <p className="circuit-importer-filesize">{(file.size / 1024).toFixed(2)} KB</p>
          {!isGenerating && (
            <button 
              className="circuit-importer-remove-file" 
              onClick={resetFileInput}
              title="Remove file"
            >
              ×
            </button>
          )}
        </div>
      );
    } else {
      return (
        <div className="circuit-importer-file-info">
          <p className="circuit-importer-filename">{file.name}</p>
          <p className="circuit-importer-filesize">{(file.size / 1024).toFixed(2)} KB</p>
          {!isGenerating && (
            <button 
              className="circuit-importer-remove-file" 
              onClick={resetFileInput}
              title="Remove file"
            >
              ×
            </button>
          )}
        </div>
      );
    }
  };

  return (
    <div className="circuit-importer-container">
      <p className="circuit-importer-description">
        {type === 'image' 
          ? 'Upload an image of a quantum circuit diagram to generate the corresponding circuit.' 
          : 'Upload a QASM, Qiskit, or JSON file to import a quantum circuit.'}
      </p>
      
      <div 
        className="circuit-importer-upload-area"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {!file ? (
          <p className="circuit-importer-drop-text">
            Drag and drop your {type === 'image' ? 'image' : 'file'} here or 
            <input
              ref={fileInputRef}
              type="file"
              id="circuit-file"
              className="circuit-importer-file-input"
              accept={type === 'image' ? 'image/*' : '.qasm,.py,.json,.txt'}
              onChange={handleFileChange}
            />
            <label htmlFor="circuit-file" className="circuit-importer-file-label">
              browse
            </label>
          </p>
        ) : (
          renderFilePreview()
        )}
      </div>
      
      {error && (
        <div className="circuit-importer-error">
          <p>{error}</p>
          <p className="circuit-importer-error-help">
            {type === 'image' 
              ? 'Try using a clearer image or a simpler circuit diagram.'
              : 'Make sure your file is in a supported format.'}
          </p>
        </div>
      )}
      
      <div className="circuit-importer-button-container">
        {isGenerating ? (
          <div className="circuit-importer-loading">
            <div className="circuit-importer-spinner"></div>
            <span>Generating circuit...</span>
          </div>
        ) : (
          <>
            <button 
              className="secondary circuit-importer-reset-button"
              onClick={handleReset}
              disabled={isGenerating}
            >
              Reset
            </button>
            <button 
              className="primary circuit-importer-button"
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

export default CircuitImporter;