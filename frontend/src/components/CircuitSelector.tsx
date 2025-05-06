// src/components/CircuitSelector.tsx
import { useState, useEffect } from 'react';
import '../assets/styles/components/CircuitSelector.css';

// Set API base URL
const API_BASE_URL = 'http://localhost:8000';

interface CircuitParameter {
  name: string;
  label: string;
  type: string;
  default: any;
  min?: number;
  max?: number;
  options?: Array<{
    value: string;
    label: string;
  }>;
}

interface CircuitType {
  id: string;
  name: string;
  description: string;
  parameters: CircuitParameter[];
  defaultParams: {[key: string]: any};
}

interface Props {
  onCircuitSelected: (data: any) => void;
  onResetCircuit: () => void;
  onStartGeneration: () => void;
  onGenerationFailed: (errorMessage: string) => void;
  isGenerating: boolean;
  selectedCircuit?: string | null | undefined;
}

function CircuitSelector({ 
  onCircuitSelected, 
  onResetCircuit, 
  onStartGeneration,
  onGenerationFailed,
  isGenerating,
  selectedCircuit 
}: Props) {
  // Use mock data for initial render to avoid loading state
  const [circuitTypes, setCircuitTypes] = useState<CircuitType[]>([
    {
      id: 'bell_state',
      name: 'Bell State',
      description: 'Creates a Bell state',
      parameters: [],
      defaultParams: {}
    }
  ]);
  const [selectedType, setSelectedType] = useState<string>('bell_state');
  const [parameters, setParameters] = useState<{[key: string]: any}>({});
  const [loadingTemplates, setLoadingTemplates] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastGeneratedConfig, setLastGeneratedConfig] = useState<string>('');

  // Load templates on component mount
  useEffect(() => {
    fetchCircuitTypes();
  }, []);

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

  const fetchCircuitTypes = async () => {
    try {
      setLoadingTemplates(true);
      
      const response = await fetch(`${API_BASE_URL}/circuits/templates`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch circuit types: ${response.status}`);
      }
      
      const data = await response.json();
      
      if (!Array.isArray(data)) {
        throw new Error("Invalid response format: expected an array");
      }
      
      if (data.length > 0) {
        setCircuitTypes(data);
        
        // Only set default selection if we didn't have a selection yet
        if (!selectedType) {
          setSelectedType(data[0].id);
          setParameters(data[0].defaultParams || {});
        }
      }
    } catch (err) {
      // Don't set error state, just use our default types
    } finally {
      setLoadingTemplates(false);
    }
  };

  // Update selected circuit when prop changes
  useEffect(() => {
    if (selectedCircuit && circuitTypes.length > 0) {
      setSelectedType(selectedCircuit);
      
      // Find the circuit type to get default parameters
      const circuitType = circuitTypes.find(type => type.id === selectedCircuit);
      if (circuitType) {
        setParameters(circuitType.defaultParams || {});
      }
    }
  }, [selectedCircuit, circuitTypes]);
  
  const handleTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newType = e.target.value;
    setSelectedType(newType);
    
    // Update parameters based on selected circuit type
    const circuitType = circuitTypes.find(type => type.id === newType);
    if (circuitType) {
      setParameters(circuitType.defaultParams || {});
    } else {
      setParameters({});
    }
    
    // Reset last generated config since we changed the type
    setLastGeneratedConfig('');
  };
  
  // Handle parameter changes
  const handleParameterChange = (paramName: string, value: any) => {
    setParameters(prev => ({
      ...prev,
      [paramName]: value
    }));
    
    // Reset last generated config since we changed the parameters
    setLastGeneratedConfig('');
  };
  
  // Render the parameter inputs
  const renderParameterInputs = () => {
    if (!selectedType || circuitTypes.length === 0) {
      return null;
    }
    
    const circuitType = circuitTypes.find(type => type.id === selectedType);
    
    if (!circuitType || !circuitType.parameters || circuitType.parameters.length === 0) {
      return <p>This circuit has no configurable parameters.</p>;
    }
    
    return (
      <div className="circuit-selector-params">
        {circuitType.parameters.map((param: CircuitParameter) => (
          <div key={param.name} className="form-group">
            <label className="form-label">{param.label}</label>
            {param.type === 'number' ? (
              <input
                type="number"
                min={param.min}
                max={param.max}
                value={parameters[param.name] || param.default}
                onChange={(e) => handleParameterChange(param.name, parseInt(e.target.value))}
                disabled={isGenerating}
              />
            ) : param.type === 'select' ? (
              <select
                value={parameters[param.name] || param.default}
                onChange={(e) => handleParameterChange(param.name, e.target.value)}
                disabled={isGenerating}
              >
                {param.options?.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            ) : null}
          </div>
        ))}
      </div>
    );
  };

  const handleReset = () => {
    onResetCircuit();
  };
  
  const handleGenerate = async () => {
    if (!selectedType) {
      return;
    }
    
    // Create a config string to track what we're generating
    const configString = `${selectedType}-${JSON.stringify(parameters)}`;
    
    // If already generating this exact config, don't do it again
    if (isGenerating || configString === lastGeneratedConfig) {
      return;
    }
    
    // Signal to parent that generation is starting
    onStartGeneration();
    
    // Set the config we're generating
    setError(null);
    setLastGeneratedConfig(configString);
    
    try {
      // Call the backend API to generate the circuit
      const url = `${API_BASE_URL}/circuits/generate`;
      
      const requestBody = {
        circuit_type: selectedType,
        parameters: parameters
      };
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });
      
      if (!response.ok) {
        let errorMessage = `Failed to generate circuit: ${response.status}`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            errorMessage = errorData.detail;
          }
        } catch (e) {
          // If we can't parse the error JSON, just use the status code
        }
        throw new Error(errorMessage);
      }
      
      // Process the response
      const text = await response.text();
      
      let circuitData;
      try {
        circuitData = JSON.parse(text);
      } catch (parseError) {
        throw new Error("Failed to parse circuit data");
      }
      
      // Update the parent component with the data
      onCircuitSelected(circuitData);
      
    } catch (err) {
      const errorMessage = err instanceof Error 
        ? err.message 
        : 'Failed to generate circuit. Please try again later.';
        
      setError(errorMessage);
      onGenerationFailed(errorMessage);
      setLastGeneratedConfig(''); // Reset to allow retrying
    }
  };
  
  return (
    <div className="circuit-selector-container">
      <p className="circuit-selector-description">
        Select a circuit type and configure parameters to generate a quantum circuit.
      </p>
      
      <div className="circuit-selector-form">
        <div className="form-group">
          <label className="form-label">Circuit Type</label>
          {loadingTemplates ? (
            <div style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
              <select disabled style={{ minWidth: '200px', padding: '8px' }}>
                <option>Loading templates...</option>
              </select>
              <div className="spinner-small"></div>
            </div>
          ) : (
            <select 
              value={selectedType} 
              onChange={handleTypeChange}
              disabled={isGenerating}
              style={{ minWidth: '200px', padding: '8px' }}
            >
              {circuitTypes.map(type => (
                <option key={type.id} value={type.id}>
                  {type.name}
                </option>
              ))}
            </select>
          )}
        </div>
        
        {/* Add parameter inputs */}
        {renderParameterInputs()}
        
        {error && <div className="error-message">{error}</div>}
        
        <div className="circuit-selector-actions">
          {isGenerating ? (
            <div className="circuit-selector-loading">
              <div className="circuit-selector-spinner"></div>
              <span>Generating circuit...</span>
            </div>
          ) : (
            <>
              <button 
                className="secondary circuit-selector-reset-button"
                onClick={handleReset}
                disabled={isGenerating}
              >
                Reset
              </button>
              <button 
                className="primary"
                onClick={handleGenerate}
                disabled={!selectedType || loadingTemplates || lastGeneratedConfig === `${selectedType}-${JSON.stringify(parameters)}`}
              >
                Generate Circuit
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default CircuitSelector;