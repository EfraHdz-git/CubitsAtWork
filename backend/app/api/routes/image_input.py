# app/api/routes/image_input.py
import traceback
from fastapi import APIRouter, HTTPException, UploadFile, File
from ..models.response_models import CircuitResponse, CircuitExplanation, CircuitVisualization, CircuitExports, GateExplanation
from ...core.nlp_processor.intent_parser import CircuitIntent, CircuitType
from ...core.circuit_builder.builder import CircuitBuilder
from ...core.output_generator.qiskit_generator import QiskitGenerator
from ...core.output_generator.visualizer import CircuitVisualizer
from ...core.output_generator.export_generator import ExportGenerator
from ...core.explanation_generator.circuit_explainer import CircuitExplainer
from ...core.explanation_generator.custom_circuit_explainer import CustomCircuitExplainer
from ...core.nlp_processor.vision_parser import VisionCircuitParser

router = APIRouter(
    prefix="/image",
    tags=["image-input"],
    responses={404: {"description": "Not found"}},
)

@router.post("/generate", response_model=CircuitResponse)
async def generate_from_image(file: UploadFile = File(...)):
    try:
        print(f"Processing image file: {file.filename}")
        
        # Read file content
        contents = await file.read()
        
        # Process the image with GPT Vision
        try:
            vision_parser = VisionCircuitParser()
            intent = await vision_parser.parse_image(contents, file.content_type)
        except HTTPException as he:
            # Pass through HTTPExceptions from the parser
            raise he
        
        print(f"Intent detected: {intent.circuit_type} with params: {intent.params}")
        
        # Build the circuit
        circuit_builder = CircuitBuilder()
        circuit = circuit_builder.build_circuit(intent)
        
        # *** KEY FIX: Check if the vision parser provided an explanation ***
        # Get the explanation from the parser if it exists, otherwise create a default one
        if hasattr(intent, "explanation") and intent.explanation:
            print("Using explanation from vision parser!")
            explanation_dict = intent.explanation
            
            # Convert explanation dict to model format
            explanation = CircuitExplanation(
                title=explanation_dict.get("title", f"{intent.circuit_type.value.replace('_', ' ').title()} Circuit"),
                summary=explanation_dict.get("summary", "A quantum circuit implementation."),
                gates=[GateExplanation(
                    gate=g.get("gate", ""),
                    explanation=g.get("explanation", ""),
                    analogy=g.get("analogy", "") if "analogy" in g else None
                ) for g in explanation_dict.get("gates", [])],
                applications=explanation_dict.get("applications", []),
                educational_value=explanation_dict.get("educational_value", "Understanding quantum computing principles."),
                error=explanation_dict.get("error", None)
            )
        else:
            # If no explanation provided by the parser, use the default one
            explanation = CircuitExplanation(
                title=f"{intent.circuit_type.value.replace('_', ' ').title()} Circuit",
                summary="A quantum circuit implementation.",
                gates=[],
                applications=[],
                educational_value="Understanding quantum computing principles."
            )
            
            # Try to generate explanation based on circuit type
            if intent.circuit_type == CircuitType.CUSTOM:
                # Handle custom circuit with default explainer
                pass
            else:
                # Try to generate explanations for known circuit types including QFT
                try:
                    circuit_explainer = CircuitExplainer()
                    explanation_dict = circuit_explainer.generate_explanation(intent, circuit)
                    
                    # Convert explanation dict to model format
                    explanation = CircuitExplanation(
                        title=explanation_dict.get("title", f"{intent.circuit_type.value.replace('_', ' ').title()} Circuit"),
                        summary=explanation_dict.get("summary", "A quantum circuit implementation."),
                        gates=[GateExplanation(
                            gate=g.get("gate", ""),
                            explanation=g.get("explanation", ""),
                            analogy=g.get("analogy", "")
                        ) for g in explanation_dict.get("gates", [])],
                        applications=explanation_dict.get("applications", []),
                        educational_value=explanation_dict.get("educational_value", ""),
                        error=explanation_dict.get("error", None)
                    )
                except Exception as e:
                    print(f"Error generating explanation: {str(e)}")
                    explanation.error = f"Error generating explanation: {str(e)}"
        
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
        
        # For custom circuits, handle explanation differently
        custom_gates = None
        custom_description = None
        
        if intent.circuit_type == CircuitType.CUSTOM:
            # Handle custom circuit
            custom_gates = intent.params.get("custom_gates", [])
            custom_description = intent.params.get("custom_description", "Custom quantum circuit")
        
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
        
        # Prepare the complete response - ensure all required fields are present
        response = CircuitResponse(
            circuit_type=intent.circuit_type.value,
            num_qubits=circuit.num_qubits,
            explanation=explanation,
            visualization=visualization,
            exports=exports,
        )
        
        # Add custom circuit information if applicable
        if intent.circuit_type == CircuitType.CUSTOM:
            response.custom_gates = custom_gates
            response.custom_description = custom_description
        
        # Debug output
        print(f"Response prepared: {response.circuit_type} with {response.num_qubits} qubits")
        print(f"Explanation in response: {explanation.title} - Gates: {len(explanation.gates)} - Applications: {len(explanation.applications)}")
        
        return response
        
    except HTTPException as he:
        # Just re-raise HTTP exceptions
        raise he
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error processing image request: {str(e)}\n{error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")