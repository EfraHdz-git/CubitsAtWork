# app/api/models/response_models.py
from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class GateExplanation(BaseModel):
    gate: str
    explanation: str
    analogy: Optional[str] = None

class CircuitExplanation(BaseModel):
    title: str
    summary: str
    gates: List[GateExplanation]
    applications: List[str]
    educational_value: str
    error: Optional[str] = None
    # For custom circuits
    custom_description: Optional[str] = None

class CircuitVisualization(BaseModel):
    circuit_diagram: str  # Base64 encoded PNG
    bloch_sphere: Optional[str] = None  # Base64 encoded PNG
    q_sphere: Optional[str] = None  # Base64 encoded PNG
    measurement_histogram: Optional[str] = None  # Base64 encoded PNG

class CircuitExports(BaseModel):
    qiskit_code: str
    qasm_code: str
    json_code: str
    ibmq_config: Optional[str] = None

class CustomGateSequence(BaseModel):
    gates: List[str]
    description: Optional[str] = None

class CircuitResponse(BaseModel):
    circuit_type: str
    num_qubits: int
    explanation: CircuitExplanation
    visualization: CircuitVisualization
    exports: CircuitExports
    # For custom circuits
    custom_gates: Optional[List[str]] = None
    custom_description: Optional[str] = None
    error: Optional[str] = None