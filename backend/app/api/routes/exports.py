# app/api/routes/exports.py
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from ..models.response_models import CircuitResponse
from ...core.circuit_builder.builder import CircuitBuilder
from ...core.nlp_processor.intent_parser import CircuitIntent, CircuitType
from ...core.output_generator.export_generator import ExportGenerator

router = APIRouter(
    prefix="/exports",
    tags=["exports"],
    responses={404: {"description": "Not found"}},
)

@router.get("/jupyter", response_class=Response)
async def get_jupyter_notebook(
    circuit_type: str = Query(..., description="Type of the circuit"),
    num_qubits: int = Query(2, description="Number of qubits in the circuit", ge=1, le=10)
):
    """Generate and download a Jupyter Notebook for the specified circuit."""
    try:
        # Create the circuit builder
        circuit_builder = CircuitBuilder()
        
        # Parse the circuit type
        try:
            circuit_type_enum = CircuitType(circuit_type)
        except ValueError:
            circuit_type_enum = CircuitType.CUSTOM
        
        # Create circuit intent
        intent = CircuitIntent(circuit_type_enum, {"num_qubits": num_qubits})
        
        # Build the circuit
        circuit = circuit_builder.build_circuit(intent)
        
        # Create export generator
        export_generator = ExportGenerator()
        
        # Generate Jupyter Notebook
        jupyter_notebook = export_generator.generate_jupyter_notebook(
            circuit, 
            circuit_type,
            f"A {circuit_type.replace('_', ' ')} quantum circuit with {num_qubits} qubits"
        )
        
        # Return as a downloadable file
        return Response(
            content=jupyter_notebook,
            media_type="application/x-ipynb+json",
            headers={
                "Content-Disposition": f"attachment; filename=quantum_circuit_{circuit_type}.ipynb"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate Jupyter Notebook: {str(e)}")