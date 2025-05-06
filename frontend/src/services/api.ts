// src/services/api.ts

//const API_BASE_URL = 'http://localhost:8000';
const API_BASE_URL = 'https://cubits-api.1v4c6sozyelm.us-south.codeengine.appdomain.cloud';

export interface CircuitGenerationRequest {
  text: string;
}

export interface Gate {
  gate: string;
  explanation: string;
  analogy?: string; // Make analogy optional since it might not always be present
}

export interface CircuitExplanation {
  title: string;
  summary: string;
  gates: Gate[];
  applications: string[];
  educational_value: string;
  error?: string; // Add error field for explanation-level errors
  custom_description?: string; // Add for consistency with backend
}

// New interfaces for enhanced visualizations
export interface CircuitImageMetadata {
  width: number;
  height: number;
  circuit_width?: number;
  circuit_depth?: number;
  qubits?: number;
  cbits?: number;
  folded?: boolean;
  fold_columns?: number;
  type?: string;
}

export interface CircuitImage {
  image: string;
  metadata: CircuitImageMetadata;
}

// Updated visualization interface with support for both formats
export interface CircuitVisualization {
  // Support both legacy format (string) and enhanced format (object)
  circuit_diagram: string | CircuitImage;
  bloch_sphere?: string | CircuitImage | null;
  q_sphere?: string | CircuitImage;
  measurement_histogram?: string | CircuitImage;
}

export interface CircuitExports {
  qiskit_code: string;
  qasm_code: string;
  json_code: string;
  ibmq_config?: string; // Make optional
}

export interface CircuitUploadResponse extends CircuitResponse {
  source_format: string;
  original_content: string;
  cleaned_content?: string;
}

export interface CircuitResponse {
  circuit_type: string;
  num_qubits: number;
  explanation: CircuitExplanation;
  visualization: CircuitVisualization;
  exports: CircuitExports;
  custom_gates?: string[]; // Add for custom circuits
  custom_description?: string; // Add for custom circuits
  error?: string; // Add this for top-level errors
}

// Helper functions for working with enhanced visualizations
export function isEnhancedImage(
  image: string | CircuitImage | null | undefined
): image is CircuitImage {
  return (
    !!image &&
    typeof image === 'object' &&
    'image' in image &&
    'metadata' in image
  );
}

export function getImageSource(
  image: string | CircuitImage | null | undefined
): string {
  if (!image) return '';
  
  if (isEnhancedImage(image)) {
    return image.image;
  }
  
  return image;
}

export function getImageMetadata(
  image: string | CircuitImage | null | undefined
): CircuitImageMetadata | null {
  if (!image || !isEnhancedImage(image)) {
    return null;
  }
  
  return image.metadata;
}

export const ApiService = {
  generateCircuitFromText: async (text: string): Promise<CircuitResponse> => {
    try {
      const response = await fetch(`${API_BASE_URL}/text/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });
      
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      
      // Parse the response and return the data
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error generating circuit:', error);
      throw error;
    }
  },
  
  // Add new method for circuit file uploads
  uploadCircuitFile: async (file: File, description?: string): Promise<CircuitUploadResponse> => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      if (description) {
        formData.append('description', description);
      }
      
      const response = await fetch(`${API_BASE_URL}/upload/circuit`, {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }
      
      // Parse the response and return the data
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error uploading circuit file:', error);
      throw error;
    }
  }
};