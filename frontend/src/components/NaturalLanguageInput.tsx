// src/components/NaturalLanguageInput.tsx
import { useState, useEffect } from 'react';
import { ApiService, CircuitResponse } from '../services/api';
import '../assets/styles/components/NaturalLanguageInput.css';

interface Props {
  onCircuitGenerated: (data: CircuitResponse) => void;
  onResetCircuit: () => void;
  onStartGeneration: () => void;
  onGenerationFailed: (errorMessage: string) => void;
  isGenerating: boolean;
}

function NaturalLanguageInput({ 
  onCircuitGenerated, 
  onResetCircuit, 
  onStartGeneration, 
  onGenerationFailed,
  isGenerating 
}: Props) {
  const [input, setInput] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Listen for reset events
  useEffect(() => {
    const handleReset = () => {
      setError(null);
    };

    document.addEventListener('resetInputs', handleReset);
    return () => {
      document.removeEventListener('resetInputs', handleReset);
    };
  }, []);

  const handleSubmit = async () => {
    if (!input.trim()) {
      setError('Please enter a circuit description');
      return;
    }
    
    // Signal to parent that generation is starting
    onStartGeneration();
    setError(null);
    
    try {
      console.log('Starting API call...');
      // Make the API call
      const circuitData = await ApiService.generateCircuitFromText(input);
      
      console.log('API call successful, updating data...');
      // Update parent with the new data
      onCircuitGenerated(circuitData);
    } catch (error) {
      console.error('Error generating circuit:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to generate circuit. Please try again.';
      setError(errorMessage);
      onGenerationFailed(errorMessage);
    }
  };

  const handleReset = () => {
    onResetCircuit();
  };

  return (
    <div className="nl-input-container">
      <p className="nl-input-description">
        Describe a quantum circuit in your own words, and we'll generate it for you.
      </p>
      
      <textarea
        className="nl-input-textarea"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="E.g., Create a Bell state circuit with 2 qubits"
        rows={4}
        disabled={isGenerating}
      />
      
      {error && <p className="nl-input-error">{error}</p>}
      
      <div className="nl-input-button-container">
        {isGenerating ? (
          <div className="nl-input-loading">
            <div className="nl-input-spinner"></div>
            <span>Generating circuit...</span>
          </div>
        ) : (
          <>
            <button 
              className="secondary nl-input-reset-button"
              onClick={handleReset}
              disabled={isGenerating}
            >
              Reset
            </button>
            <button 
              className="primary nl-input-button"
              onClick={handleSubmit}
              disabled={!input.trim() || isGenerating}
            >
              Generate Circuit
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default NaturalLanguageInput;