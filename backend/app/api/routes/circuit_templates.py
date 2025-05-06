# app/api/routes/circuit_templates.py
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import traceback
from ...core.nlp_processor.intent_parser import CircuitType
from ...core.circuit_builder.builder import CircuitBuilder
from ..models.response_models import CircuitResponse, CircuitExplanation, CircuitVisualization, CircuitExports, GateExplanation
from ...core.explanation_generator.circuit_explainer import CircuitExplainer
from ...core.output_generator.qiskit_generator import QiskitGenerator
from ...core.output_generator.visualizer import CircuitVisualizer
from ...core.output_generator.export_generator import ExportGenerator

# Define models for circuit templates
class ParameterOption(BaseModel):
    value: str
    label: str

class CircuitParameter(BaseModel):
    name: str
    label: str
    type: str
    default: Any
    min: Optional[int] = None
    max: Optional[int] = None
    options: Optional[List[ParameterOption]] = None

class CircuitTypeInfo(BaseModel):
    id: str
    name: str
    description: str
    parameters: List[CircuitParameter]
    defaultParams: Dict[str, Any]

class CircuitGenerateRequest(BaseModel):
    circuit_type: str
    parameters: Dict[str, Any]

router = APIRouter(
    prefix="/circuits",
    tags=["circuit-templates"],
    responses={404: {"description": "Not found"}},
)

@router.get("/templates", response_model=List[CircuitTypeInfo])
async def get_circuit_templates():
    """
    Get a list of available quantum circuit templates with their parameters.
    """
    try:
        circuit_types = [
            CircuitTypeInfo(
                id=CircuitType.BELL_STATE.value,
                name="Bell State",
                description="A simple Bell state circuit that creates quantum entanglement between qubits",
                parameters=[
                    CircuitParameter(
                        name="num_qubits",
                        label="Number of Qubits",
                        type="number",
                        default=2,
                        min=2,
                        max=5
                    ),
                    CircuitParameter(
                        name="measure",
                        label="Add Measurement",
                        type="select",
                        default="yes",
                        options=[
                            ParameterOption(value="yes", label="Yes"),
                            ParameterOption(value="no", label="No")
                        ]
                    )
                ],
                defaultParams={"num_qubits": 2, "measure": "yes"}
            ),
            CircuitTypeInfo(
                id=CircuitType.GHZ_STATE.value,
                name="GHZ State",
                description="Greenberger–Horne–Zeilinger state - a highly entangled quantum state",
                parameters=[
                    CircuitParameter(
                        name="num_qubits",
                        label="Number of Qubits",
                        type="number",
                        default=3,
                        min=3,
                        max=10
                    )
                ],
                defaultParams={"num_qubits": 3}
            ),
            CircuitTypeInfo(
                id=CircuitType.W_STATE.value,
                name="W State",
                description="Another type of entangled quantum state where exactly one qubit is in state |1⟩",
                parameters=[
                    CircuitParameter(
                        name="num_qubits",
                        label="Number of Qubits",
                        type="number",
                        default=3,
                        min=3,
                        max=8
                    )
                ],
                defaultParams={"num_qubits": 3}
            ),
            CircuitTypeInfo(
                id=CircuitType.TELEPORTATION.value,
                name="Quantum Teleportation",
                description="Quantum teleportation protocol that transfers a quantum state using entanglement",
                parameters=[],
                defaultParams={}
            ),
            CircuitTypeInfo(
                id=CircuitType.SUPERDENSE_CODING.value,
                name="Superdense Coding",
                description="Quantum protocol that allows sending two classical bits using one qubit",
                parameters=[],
                defaultParams={}
            ),
            CircuitTypeInfo(
                id=CircuitType.DEUTSCH_JOZSA.value,
                name="Deutsch-Jozsa Algorithm",
                description="Quantum algorithm that determines if a function is constant or balanced",
                parameters=[
                    CircuitParameter(
                        name="num_qubits",
                        label="Number of Qubits",
                        type="number",
                        default=3,
                        min=2,
                        max=8
                    ),
                    CircuitParameter(
                        name="oracle_type",
                        label="Oracle Type",
                        type="select",
                        default="balanced",
                        options=[
                            ParameterOption(value="constant", label="Constant"),
                            ParameterOption(value="balanced", label="Balanced")
                        ]
                    )
                ],
                defaultParams={"num_qubits": 3, "oracle_type": "balanced"}
            ),
            CircuitTypeInfo(
                id=CircuitType.BERNSTEIN_VAZIRANI.value,
                name="Bernstein-Vazirani Algorithm",
                description="Quantum algorithm that determines a hidden bitstring",
                parameters=[
                    CircuitParameter(
                        name="num_qubits",
                        label="Number of Qubits",
                        type="number",
                        default=4,
                        min=3,
                        max=8
                    ),
                    CircuitParameter(
                        name="secret_string",
                        label="Secret String",
                        type="select",
                        default="101",
                        options=[
                            ParameterOption(value="101", label="101"),
                            ParameterOption(value="010", label="010"),
                            ParameterOption(value="111", label="111"),
                            ParameterOption(value="001", label="001")
                        ]
                    )
                ],
                defaultParams={"num_qubits": 4, "secret_string": "101"}
            ),
            CircuitTypeInfo(
                id=CircuitType.SIMON.value,
                name="Simon's Algorithm",
                description="Quantum algorithm that determines a hidden bitstring in a black-box function",
                parameters=[
                    CircuitParameter(
                        name="num_qubits",
                        label="Number of Qubits",
                        type="number",
                        default=6,
                        min=4,
                        max=8
                    )
                ],
                defaultParams={"num_qubits": 6}
            ),
            CircuitTypeInfo(
                id=CircuitType.QFT.value,
                name="Quantum Fourier Transform",
                description="Quantum Fourier Transform circuit - the quantum analog of the discrete Fourier transform",
                parameters=[
                    CircuitParameter(
                        name="num_qubits",
                        label="Number of Qubits",
                        type="number",
                        default=3,
                        min=2,
                        max=8
                    ),
                    CircuitParameter(
                        name="inverse",
                        label="Inverse QFT",
                        type="select",
                        default="no",
                        options=[
                            ParameterOption(value="yes", label="Yes"),
                            ParameterOption(value="no", label="No")
                        ]
                    )
                ],
                defaultParams={"num_qubits": 3, "inverse": "no"}
            ),
            CircuitTypeInfo(
                id=CircuitType.QPE.value,
                name="Quantum Phase Estimation",
                description="Algorithm to estimate the eigenphase of a unitary operator",
                parameters=[
                    CircuitParameter(
                        name="num_qubits",
                        label="Number of Qubits",
                        type="number",
                        default=5,
                        min=3,
                        max=8
                    ),
                    CircuitParameter(
                        name="precision_qubits",
                        label="Precision Qubits",
                        type="number",
                        default=3,
                        min=2,
                        max=6
                    )
                ],
                defaultParams={"num_qubits": 5, "precision_qubits": 3}
            ),
            CircuitTypeInfo(
                id=CircuitType.SHOR.value,
                name="Shor's Algorithm",
                description="Quantum algorithm for integer factorization",
                parameters=[
                    CircuitParameter(
                        name="num_qubits",
                        label="Number of Qubits",
                        type="number",
                        default=7,
                        min=5,
                        max=10
                    ),
                    CircuitParameter(
                        name="number_to_factor",
                        label="Number to Factor",
                        type="select",
                        default="15",
                        options=[
                            ParameterOption(value="15", label="15"),
                            ParameterOption(value="21", label="21"),
                            ParameterOption(value="35", label="35")
                        ]
                    )
                ],
                defaultParams={"num_qubits": 7, "number_to_factor": "15"}
            ),
            CircuitTypeInfo(
                id=CircuitType.GROVERS.value,
                name="Grover's Algorithm",
                description="Quantum search algorithm that finds an element in an unsorted database",
                parameters=[
                    CircuitParameter(
                        name="num_qubits",
                        label="Number of Qubits",
                        type="number",
                        default=3,
                        min=2,
                        max=6
                    ),
                    CircuitParameter(
                        name="iterations",
                        label="Number of Iterations",
                        type="number",
                        default=1,
                        min=1,
                        max=10
                    ),
                    CircuitParameter(
                        name="marked_state",
                        label="Marked State",
                        type="select",
                        default="101",
                        options=[
                            ParameterOption(value="101", label="101"),
                            ParameterOption(value="010", label="010"),
                            ParameterOption(value="111", label="111")
                        ]
                    )
                ],
                defaultParams={"num_qubits": 3, "iterations": 1, "marked_state": "101"}
            ),
            CircuitTypeInfo(
                id=CircuitType.QAOA.value,
                name="Quantum Approximate Optimization Algorithm",
                description="Variational quantum algorithm for solving combinatorial optimization problems",
                parameters=[
                    CircuitParameter(
                        name="num_qubits",
                        label="Number of Qubits",
                        type="number",
                        default=4,
                        min=2,
                        max=8
                    ),
                    CircuitParameter(
                        name="p_layers",
                        label="Number of QAOA Layers",
                        type="number",
                        default=1,
                        min=1,
                        max=3
                    )
                ],
                defaultParams={"num_qubits": 4, "p_layers": 1}
            ),
            CircuitTypeInfo(
                id=CircuitType.VQE.value,
                name="Variational Quantum Eigensolver",
                description="Hybrid quantum-classical algorithm for finding low energy states of molecules",
                parameters=[
                    CircuitParameter(
                        name="num_qubits",
                        label="Number of Qubits",
                        type="number",
                        default=4,
                        min=2,
                        max=8
                    ),
                    CircuitParameter(
                        name="ansatz_depth",
                        label="Ansatz Depth",
                        type="number",
                        default=1,
                        min=1,
                        max=3
                    )
                ],
                defaultParams={"num_qubits": 4, "ansatz_depth": 1}
            ),
            CircuitTypeInfo(
                id=CircuitType.QUANTUM_COUNTING.value,
                name="Quantum Counting Algorithm",
                description="Quantum algorithm that determines the number of solutions to a search problem",
                parameters=[
                    CircuitParameter(
                        name="num_qubits",
                        label="Number of Qubits",
                        type="number",
                        default=6,
                        min=4,
                        max=8
                    ),
                    CircuitParameter(
                        name="counting_qubits",
                        label="Counting Qubits",
                        type="number",
                        default=3,
                        min=2,
                        max=4
                    )
                ],
                defaultParams={"num_qubits": 6, "counting_qubits": 3}
            ),
            CircuitTypeInfo(
                id=CircuitType.QUANTUM_WALK.value,
                name="Quantum Walk",
                description="Quantum version of the classical random walk algorithm",
                parameters=[
                    CircuitParameter(
                        name="num_qubits",
                        label="Number of Qubits",
                        type="number",
                        default=5,
                        min=3,
                        max=8
                    ),
                    CircuitParameter(
                        name="steps",
                        label="Number of Steps",
                        type="number",
                        default=2,
                        min=1,
                        max=5
                    )
                ],
                defaultParams={"num_qubits": 5, "steps": 2}
            ),
            CircuitTypeInfo(
                id=CircuitType.HHL.value,
                name="HHL Algorithm",
                description="Quantum algorithm for solving linear systems of equations",
                parameters=[
                    CircuitParameter(
                        name="num_qubits",
                        label="Number of Qubits",
                        type="number",
                        default=5,
                        min=4,
                        max=8
                    ),
                    CircuitParameter(
                        name="precision_qubits",
                        label="Precision Qubits",
                        type="number",
                        default=3,
                        min=2,
                        max=4
                    )
                ],
                defaultParams={"num_qubits": 5, "precision_qubits": 3}
            )
        ]
        
        return circuit_types
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error getting circuit templates: {str(e)}\n{error_details}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=CircuitResponse)
async def generate_from_template(request: CircuitGenerateRequest):
    """
    Generate a quantum circuit from a selected template and parameters.
    """
    try:
        print(f"Generating circuit of type: {request.circuit_type} with parameters: {request.parameters}")
        
        # Create a CircuitIntent from the template selection
        from ...core.nlp_processor.intent_parser import CircuitIntent
        
        try:
            circuit_type = CircuitType(request.circuit_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid circuit type: {request.circuit_type}")
        
        # Create the circuit intent
        intent = CircuitIntent(circuit_type, request.parameters)
        
        # Build the circuit
        circuit_builder = CircuitBuilder()
        circuit = circuit_builder.build_circuit(intent)
        
        # Initialize response objects with default values
        explanation = CircuitExplanation(
            title=f"{intent.circuit_type.value.replace('_', ' ').title()} Circuit",
            summary="A quantum circuit implementation.",
            gates=[],
            applications=[],
            educational_value="Understanding quantum computing principles."
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
        
        # Generate explanation
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
        response = CircuitResponse(
            circuit_type=intent.circuit_type.value,
            num_qubits=circuit.num_qubits,
            explanation=explanation,
            visualization=visualization,
            exports=exports,
        )
        
        return response
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Error generating circuit from template: {str(e)}\n{error_details}")
        raise HTTPException(status_code=500, detail=str(e))