// src/components/EducationalExplanation.tsx
import { CircuitResponse } from '../services/api';
import '../assets/styles/components/EducationalExplanation.css';
import { useEffect } from 'react';

interface Props {
  circuitData: CircuitResponse | null;
}

function EducationalExplanation({ circuitData }: Props) {
  // Add logging to debug explanation data
  useEffect(() => {
    if (circuitData) {
      console.log("CircuitData received:", circuitData);
      console.log("Explanation structure:", circuitData.explanation);
    }
  }, [circuitData]);

  if (!circuitData) {
    return (
      <div className="card edu-exp-container">
        <h2 className="edu-exp-heading">Summary of Circuit</h2>
        <div className="edu-exp-placeholder">
          Generate a circuit to see summary
        </div>
      </div>
    );
  }

  // If the response has an error field at the top level
  if (circuitData.error) {
    return (
      <div className="card edu-exp-container">
        <h2 className="edu-exp-heading">Explanation Error</h2>
        <div className="edu-exp-error">
          <p>There was a problem generating the circuit:</p>
          <p className="edu-exp-error-message">{circuitData.error}</p>
          <p className="edu-exp-error-help">Please try again or check your configuration.</p>
        </div>
      </div>
    );
  }

  if (!circuitData.explanation) {
    console.warn("No explanation found in circuitData:", circuitData);
    return (
      <div className="card edu-exp-container">
        <h2 className="edu-exp-heading">Summary of Circuit</h2>
        <div className="edu-exp-placeholder">
          No explanation available for this circuit
        </div>
      </div>
    );
  }

  // If the explanation has an error field
  if (circuitData.explanation.error) {
    return (
      <div className="card edu-exp-container">
        <h2 className="edu-exp-heading">Explanation Error</h2>
        <div className="edu-exp-error">
          <p>There was a problem generating the explanation:</p>
          <p className="edu-exp-error-message">{circuitData.explanation.error}</p>
          <p className="edu-exp-error-help">Please try again or check your API configuration.</p>
        </div>
      </div>
    );
  }

  const { explanation } = circuitData;

  // Helper function to format applications into a comma-separated paragraph
  const renderApplications = (applications: string[]) => {
    // For short lists (less than 4 items), display as regular list
    if (applications.length < 4) {
      return (
        <ul className="edu-exp-applications">
          {applications.map((app, index) => (
            <li key={index} className="edu-exp-application">{app}</li>
          ))}
        </ul>
      );
    }
    
    // For longer lists, display as a paragraph with semicolons
    return (
      <p className="edu-exp-applications-paragraph">
        {applications.join('; ')}
      </p>
    );
  };

  return (
    <div className="card edu-exp-container">
      <h2 className="edu-exp-heading">{explanation.title}</h2>
      
      <div className="edu-exp-content">
        {explanation.summary && (
          <div className="edu-exp-summary">
            <p className="edu-exp-text">{explanation.summary}</p>
          </div>
        )}
        
        {explanation.gates && explanation.gates.length > 0 && (
          <div className="edu-exp-section">
            <h3 className="edu-exp-subheading">How It Works</h3>
            
            {/* For short lists of gates (less than 6) */}
            {explanation.gates.length < 6 ? (
              <div className="edu-exp-gates">
                {explanation.gates.map((gate, index) => (
                  <div key={index} className="edu-exp-gate">
                    <h4 className="edu-exp-gate-name">{gate.gate}</h4>
                    <p className="edu-exp-gate-explanation">{gate.explanation}</p>
                    {gate.analogy && (
                      <p className="edu-exp-gate-analogy">
                        <strong>Analogy:</strong> {gate.analogy}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              /* For longer lists of gates (6 or more) */
              <div className="edu-exp-gates">
                {/* Show first 3 gates */}
                {explanation.gates.slice(0, 3).map((gate, index) => (
                  <div key={index} className="edu-exp-gate">
                    <h4 className="edu-exp-gate-name">{gate.gate}</h4>
                    <p className="edu-exp-gate-explanation">{gate.explanation}</p>
                    {gate.analogy && (
                      <p className="edu-exp-gate-analogy">
                        <strong>Analogy:</strong> {gate.analogy}
                      </p>
                    )}
                  </div>
                ))}
                
                {/* Compact representation of remaining gates */}
                <div className="edu-exp-gates-compact">
                  <h4 className="edu-exp-subheading">Additional Gates</h4>
                  <div className="edu-exp-gates-grid">
                    {explanation.gates.slice(3).map((gate, index) => (
                      <div key={index} className="edu-exp-gate-grid-item">{gate.gate}</div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        
        {explanation.applications && explanation.applications.length > 0 && (
          <div className="edu-exp-section">
            <h3 className="edu-exp-subheading">Applications</h3>
            {renderApplications(explanation.applications)}
          </div>
        )}
        
        {explanation.educational_value && (
          <div className="edu-exp-section">
            <h3 className="edu-exp-subheading">Educational Value</h3>
            <p className="edu-exp-text">{explanation.educational_value}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default EducationalExplanation;