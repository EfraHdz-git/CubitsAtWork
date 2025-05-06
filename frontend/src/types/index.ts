// src/types/index.ts
export interface CircuitData {
    id?: string;
    name?: string;
    type?: string;
    qubits?: number;
    gates?: number;
    description?: string;
    qasmCode?: string;
    qiskitCode?: string;
    jsonRepresentation?: any;
    visualizationUrl?: string;
    blochSphereData?: any;
    blochSphereUrl?: string;
    qSphereData?: any;
    qSphereUrl?: string;
    explanation?: {
      description?: string;
      purpose?: string;
      applications?: string;
      workings?: string;
    };
  }