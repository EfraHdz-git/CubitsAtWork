// src/components/Layout.tsx
import { useState, useEffect, useRef } from 'react';
import { CircuitResponse } from '../services/api';
import NaturalLanguageInput from './NaturalLanguageInput';
import CircuitVisualization from './CircuitVisualization';
import EducationalExplanation from './EducationalExplanation';
import CodeDisplay from './CodeDisplay';
import SimulationResults from './SimulationResults';
import CircuitSelector from './CircuitSelector';
import CircuitImporter from './CircuitImporter';
import CircuitFileUploader from './CircuitFileUploader';
import TechStackPanel from './TechStackPanel';
import '../assets/styles/components/Layout.css';

interface Props {
  circuitData: CircuitResponse | null;
  setCircuitData: (data: CircuitResponse | null) => void;
}

function Layout({ circuitData, setCircuitData }: Props) {
  const [simulationResults, setSimulationResults] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('text'); // 'text', 'template', 'image', 'file'
  const [error, setError] = useState<string | null>(null);
  const [resetCounter, setResetCounter] = useState(0);
  
  // Loading states for different components
  const [isNaturalLanguageGenerating, setIsNaturalLanguageGenerating] = useState(false);
  const [isTemplateGenerating, setIsTemplateGenerating] = useState(false);
  const [isImageGenerating, setIsImageGenerating] = useState(false);
  const [isFileGenerating, setIsFileGenerating] = useState(false);
  
  // Track if results should be displayed
  const [showResults, setShowResults] = useState(false);
  const pendingDataRef = useRef<CircuitResponse | null>(null);

  // Natural Language Input handlers
  const handleStartNaturalLanguageGeneration = () => {
    setIsNaturalLanguageGenerating(true);
    setShowResults(false);
    setSimulationResults(null);
  };

  const handleNaturalLanguageGenerated = (data: CircuitResponse) => {
    pendingDataRef.current = data;
    
    setTimeout(() => {
      setSimulationResults(null);
      setCircuitData(pendingDataRef.current);
      setError(null);
      setIsNaturalLanguageGenerating(false);
      setShowResults(true);
    }, 500);
  };

  const handleNaturalLanguageGenerationFailed = (errorMessage: string) => {
    setIsNaturalLanguageGenerating(false);
    setError(errorMessage);
  };

  // Template/Circuit Selector handlers
  const handleStartTemplateGeneration = () => {
    setIsTemplateGenerating(true);
    setShowResults(false);
    setSimulationResults(null);
  };

  const handleTemplateGenerated = (data: CircuitResponse) => {
    pendingDataRef.current = data;
    
    setTimeout(() => {
      setSimulationResults(null);
      setCircuitData(pendingDataRef.current);
      setError(null);
      setIsTemplateGenerating(false);
      setShowResults(true);
    }, 500);
  };

  const handleTemplateGenerationFailed = (errorMessage: string) => {
    setIsTemplateGenerating(false);
    setError(errorMessage);
  };

  // Image Importer handlers
  const handleStartImageGeneration = () => {
    setIsImageGenerating(true);
    setShowResults(false);
    setSimulationResults(null);
  };

  const handleImageGenerated = (data: CircuitResponse) => {
    pendingDataRef.current = data;
    
    setTimeout(() => {
      setSimulationResults(null);
      setCircuitData(pendingDataRef.current);
      setError(null);
      setIsImageGenerating(false);
      setShowResults(true);
    }, 500);
  };

  const handleImageGenerationFailed = (errorMessage: string) => {
    setIsImageGenerating(false);
    setError(errorMessage);
  };

  // File Importer handlers
  const handleStartFileGeneration = () => {
    setIsFileGenerating(true);
    setShowResults(false);
    setSimulationResults(null);
  };

  const handleFileGenerated = (data: CircuitResponse) => {
    pendingDataRef.current = data;
    
    setTimeout(() => {
      setSimulationResults(null);
      setCircuitData(pendingDataRef.current);
      setError(null);
      setIsFileGenerating(false);
      setShowResults(true);
    }, 500);
  };

  const handleFileGenerationFailed = (errorMessage: string) => {
    setIsFileGenerating(false);
    setError(errorMessage);
  };

  // Reset circuit data and simulation results
  const handleResetCircuit = () => {
    setCircuitData(null);
    pendingDataRef.current = null;
    setSimulationResults(null);
    setError(null);
    setShowResults(false);
    
    setResetCounter(prev => prev + 1);
    
    setIsNaturalLanguageGenerating(false);
    setIsTemplateGenerating(false);
    setIsImageGenerating(false);
    setIsFileGenerating(false);
    
    const resetEvent = new CustomEvent('resetInputs', { detail: { complete: true } });
    document.dispatchEvent(resetEvent);
  };

  // When switching tabs, ensure simulation results are reset
  useEffect(() => {
    setSimulationResults(null);
    setIsNaturalLanguageGenerating(false);
    setIsTemplateGenerating(false);
    setIsImageGenerating(false);
    setIsFileGenerating(false);
    setError(null);
  }, [activeTab]);

  // Determine if any generation is in progress
  const isGenerating = isNaturalLanguageGenerating || isTemplateGenerating || 
                       isImageGenerating || isFileGenerating;

  return (
    <div className="layout-container">
      {/* Input Section with Tabs Above */}
      <div className="layout-section">
        <div className="layout-header">
          <div className="layout-tabs">
            <button 
              className={`layout-tab ${activeTab === 'text' ? 'active' : ''}`}
              onClick={() => {
                setActiveTab('text');
                handleResetCircuit();
              }}
              disabled={isGenerating}
            >
              Create from Text
            </button>
            <button 
              className={`layout-tab ${activeTab === 'template' ? 'active' : ''}`}
              onClick={() => {
                setActiveTab('template');
                handleResetCircuit();
              }}
              disabled={isGenerating}
            >
              Create from Template
            </button>
            <button 
              className={`layout-tab ${activeTab === 'image' ? 'active' : ''}`}
              onClick={() => {
                setActiveTab('image');
                handleResetCircuit();
              }}
              disabled={isGenerating}
            >
              Create from Image
            </button>
            <button 
              className={`layout-tab ${activeTab === 'file' ? 'active' : ''}`}
              onClick={() => {
                setActiveTab('file');
                handleResetCircuit();
              }}
              disabled={isGenerating}
            >
              Create from File
            </button>
          </div>
        </div>
        
        <div className="layout-content card">
          {error && <div className="error-message">{error}</div>}
          
          {activeTab === 'text' && (
            <NaturalLanguageInput 
              onCircuitGenerated={handleNaturalLanguageGenerated}
              onResetCircuit={handleResetCircuit}
              onStartGeneration={handleStartNaturalLanguageGeneration}
              onGenerationFailed={handleNaturalLanguageGenerationFailed}
              isGenerating={isNaturalLanguageGenerating}
              key={`text-input-${resetCounter}`}
            />
          )}
          
          {activeTab === 'template' && (
            <CircuitSelector 
              onCircuitSelected={handleTemplateGenerated}
              onResetCircuit={handleResetCircuit}
              onStartGeneration={handleStartTemplateGeneration}
              onGenerationFailed={handleTemplateGenerationFailed}
              isGenerating={isTemplateGenerating}
              selectedCircuit={circuitData?.circuit_type}
              key={`template-selector-${resetCounter}`}
            />
          )}
          
          {activeTab === 'image' && (
            <CircuitImporter 
              type="image"
              onCircuitGenerated={handleImageGenerated}
              onResetCircuit={handleResetCircuit}
              onStartGeneration={handleStartImageGeneration}
              onGenerationFailed={handleImageGenerationFailed}
              isGenerating={isImageGenerating}
              key={`image-importer-${resetCounter}`}
            />
          )}
          
          {activeTab === 'file' && (
            <CircuitFileUploader 
              onCircuitGenerated={handleFileGenerated}
              onResetCircuit={handleResetCircuit}
              onStartGeneration={handleStartFileGeneration}
              onGenerationFailed={handleFileGenerationFailed}
              isGenerating={isFileGenerating}
              key={`file-uploader-${resetCounter}`}
            />
          )}
        </div>
      </div>
      
      {circuitData && showResults && !isGenerating && (
        <>
          <div className="layout-section">
            <div className="layout-content">
              <EducationalExplanation circuitData={circuitData} />
            </div>
          </div>
          
          <div className="layout-section">
            <div className="layout-content">
              <CircuitVisualization circuitData={circuitData} />
            </div>
          </div>
          
          <div className="layout-section">
            <div className="layout-content">
              <CodeDisplay circuitData={circuitData} />
            </div>
          </div>
          
          <div className="layout-section">
            <div className="layout-content">
              <SimulationResults 
                circuitData={circuitData}
                results={simulationResults}
                setResults={setSimulationResults}
              />
            </div>
          </div>
        </>
      )}
      
      {/* TechStackPanel at the bottom */}
      <div className="layout-section tech-stack-container">
        <TechStackPanel />
      </div>
    </div>
  );
}

export default Layout;