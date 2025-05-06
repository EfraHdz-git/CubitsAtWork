# app/api/routes/circuit_upload.py
import traceback
import os
import tempfile
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel

from ..models.response_models import CircuitResponse, CircuitExplanation, CircuitVisualization, CircuitExports, GateExplanation
from ...core.nlp_processor.intent_parser import CircuitType, CircuitIntent
from ...core.nlp_processor.openai_parser import OpenAICircuitParser
from ...core.circuit_builder.builder import CircuitBuilder
from ...core.output_generator.qiskit_generator import QiskitGenerator
from ...core.output_generator.visualizer import CircuitVisualizer
from ...core.output_generator.export_generator import ExportGenerator
from ...core.explanation_generator.circuit_explainer import CircuitExplainer
from ...core.explanation_generator.custom_circuit_explainer import CustomCircuitExplainer

# Define request models
class CircuitUploadResponse(CircuitResponse):
    """Response model for circuit uploads, extending the base CircuitResponse."""
    source_format: str
    original_content: str
    cleaned_content: Optional[str] = None

router = APIRouter(
    prefix="/upload",
    tags=["circuit-upload"],
    responses={404: {"description": "Not found"}},
)

# Define allowed file extensions
ALLOWED_EXTENSIONS = {
    '.qasm': 'qasm',    # OpenQASM files
    '.py': 'qiskit',    # Qiskit Python files
    '.json': 'json'     # JSON circuit descriptions
}

@router.post("/circuit", response_model=CircuitUploadResponse)
async def upload_circuit_file(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None)
):
    """
    Upload and process a quantum circuit file.
    Supported formats:
    - OpenQASM (.qasm)
    - Qiskit Python files (.py)
    - JSON circuit descriptions (.json)
    """
    try:
        print(f"Processing uploaded circuit file: {file.filename}")
        
        # Validate file extension
        _, file_extension = os.path.splitext(file.filename)
        file_extension = file_extension.lower()
        
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format: {file_extension}. Supported formats are: {', '.join(ALLOWED_EXTENSIONS.keys())}"
            )
        
        # Read file content
        file_content = await file.read()
        file_content_str = file_content.decode('utf-8')
        
        # Determine the file format
        file_format = ALLOWED_EXTENSIONS[file_extension]
        
        # Use OpenAI to analyze and clean the circuit
        openai_parser = OpenAICircuitParser(os.environ.get("OPENAI_API_KEY"))
        
        # Process the circuit based on its format
        try:
            print(f"Parsing {file_format} circuit file with OpenAI")
            cleaned_content, circuit_metadata = openai_parser.parse_circuit_file(
                file_content_str, 
                file_format, 
                description
            )
            
            # Create a CircuitIntent from the cleaned circuit
            intent_params = {
                "num_qubits": circuit_metadata.get("num_qubits", 2),
                "custom_description": circuit_metadata.get("description", f"Imported {file_format.upper()} circuit"),
                "custom_gates": circuit_metadata.get("gates", []),
                "source_format": file_format,
                "original_content": file_content_str,
                "cleaned_content": cleaned_content
            }
            
            # Create the circuit intent
            intent = CircuitIntent(CircuitType.CUSTOM, intent_params)
            
        except Exception as e:
            print(f"Error parsing circuit file: {str(e)}")
            raise HTTPException(status_code=422, detail=f"Failed to parse circuit file: {str(e)}")
        
        print(f"Intent created: {intent.circuit_type} with params: {intent.params}")
        
        # Build the circuit
        circuit_builder = CircuitBuilder()
        circuit = circuit_builder.build_circuit(intent)
        
        # Initialize response objects with default values
        explanation = CircuitExplanation(
            title=f"Imported {file_format.upper()} Circuit",
            summary=circuit_metadata.get("description", f"Imported {file_format.upper()} quantum circuit"),
            gates=[],
            applications=[],
            educational_value="Understanding quantum computing circuits and implementations."
        )
        
        visualization = CircuitVisualization(
            circuit_diagram="",
            bloch_sphere=None,
            q_sphere=None,
            measurement_histogram=None
        )
        
        exports = CircuitExports(
            qiskit_code="",
            qasm_code="",
            json_code="",
            ibmq_config=None
        )
        
        # Generate enhanced explanation for the imported circuit
        try:
            print("Generating explanation for imported circuit")
            custom_explainer = CustomCircuitExplainer()
            explanation_dict = custom_explainer.explain_circuit(intent)
            
            # Convert explanation dict to model format
            explanation = CircuitExplanation(
                title=explanation_dict.get("title", f"Imported {file_format.upper()} Circuit"),
                summary=explanation_dict.get("summary", circuit_metadata.get("description", f"Imported {file_format.upper()} quantum circuit")),
                gates=[GateExplanation(
                    gate=g.get("gate", ""),
                    explanation=g.get("explanation", ""),
                    analogy=g.get("analogy", "")
                ) for g in explanation_dict.get("gates", [])],
                applications=explanation_dict.get("applications", ["Custom quantum algorithm implementation", "Quantum circuit experimentation"]),
                educational_value=explanation_dict.get("educational_value", "Understanding imported quantum circuit behavior and gate operations."),
                custom_description=circuit_metadata.get("description", "")
            )
            print("Successfully generated explanation")
        except Exception as e:
            print(f"Error generating circuit explanation: {str(e)}")
            # Fallback to simpler explanation
            explanation = CircuitExplanation(
                title=f"Imported {file_format.upper()} Circuit",
                summary=circuit_metadata.get("description", f"Imported {file_format.upper()} quantum circuit"),
                gates=[GateExplanation(
                    gate=gate,
                    explanation=f"Applied {gate.split()[0]} operation",
                    analogy=None
                ) for gate in intent.params.get("custom_gates", [])],
                applications=["Imported quantum circuit implementation"],
                educational_value="Understanding quantum circuit behavior from external sources."
            )
        
        # Generate visualizations
        try:
            visualizer = CircuitVisualizer()
            circuit_image = visualizer.generate_circuit_image(circuit)
            visualization.circuit_diagram = circuit_image
            
            try:
                statevector_viz = visualizer.generate_statevector_visualization(circuit)
                visualization.bloch_sphere = statevector_viz.get("bloch_sphere")
                visualization.q_sphere = statevector_viz.get("q_sphere")
            except Exception as e:
                print(f"Error generating statevector visualization: {str(e)}")
            
            try:
                measurement_histogram = visualizer.generate_measurement_histogram(circuit)
                visualization.measurement_histogram = measurement_histogram
            except Exception as e:
                print(f"Error generating measurement histogram: {str(e)}")
                
        except Exception as e:
            print(f"Error generating visualizations: {str(e)}")
        
        # Generate export formats
        try:
            export_generator = ExportGenerator()
            qiskit_generator = QiskitGenerator()
            
            exports.qiskit_code = qiskit_generator.generate_code(circuit)
            
            try:
                exports.qasm_code = export_generator.generate_qasm(circuit)
            except Exception as e:
                print(f"Error generating QASM: {str(e)}")
                exports.qasm_code = "# Error generating QASM code"
            
            try:
                exports.json_code = export_generator.generate_json(circuit)
            except Exception as e:
                print(f"Error generating JSON: {str(e)}")
                exports.json_code = "{\"error\": \"Error generating JSON code\"}"
            
            try:
                exports.ibmq_config = export_generator.generate_ibmq_job(circuit)
            except Exception as e:
                print(f"Error generating IBMQ config: {str(e)}")
                
        except Exception as e:
            print(f"Error generating exports: {str(e)}")
            exports.qiskit_code = f"# Error generating Qiskit code: {str(e)}"
        
        # Prepare the complete response
        response = CircuitUploadResponse(
            circuit_type=intent.circuit_type.value,
            num_qubits=circuit.num_qubits,
            explanation=explanation,
            visualization=visualization,
            exports=exports,
            source_format=file_format,
            original_content=file_content_str,
            cleaned_content=cleaned_content
        )
        
        # Add custom circuit information
        response.custom_gates = intent.params.get("custom_gates", [])
        response.custom_description = intent.params.get("custom_description", "")
        
        return response
        
    except HTTPException as he:
        # Just re-raise HTTP exceptions
        raise he
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error processing circuit file: {str(e)}\n{error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to process circuit file: {str(e)}")