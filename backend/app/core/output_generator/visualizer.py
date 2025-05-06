import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import logging
from qiskit import QuantumCircuit
from qiskit.visualization import plot_histogram, plot_bloch_multivector, plot_state_qsphere
from typing import Optional, Dict, Any
import matplotlib.patheffects as path_effects

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CircuitVisualizer")

class CircuitVisualizer:
    """Generates professional visualizations for quantum circuits with enhanced styling."""

    def __init__(self):
        """Initialize the circuit visualizer with modern styling."""
        # Modern theme styling
        self.circuit_style = {
            'backgroundcolor': 'white',
            'displaycolor': {
                # Single-qubit gates - Row 1
                'h': '#E53935',      # Hadamard - Red
                'x': '#4285F4',      # Pauli-X - Blue
                'y': '#FF00FF',      # Pauli-Y - Pink (Row 4)
                'z': '#4FC3F7',      # Pauli-Z - Light blue (Row 2)
        
                # Row 2 gates
                's': '#4FC3F7',      # S-gate - Light blue
                't': '#4FC3F7',      # T-gate - Light blue
                'p': '#4FC3F7',      # Phase - Light blue
                'sdg': '#4FC3F7',    # S dagger - Light blue (T† in image)
                'tdg': '#4FC3F7',    # T dagger - Light blue (S† in image)
        
                # Row 3 gates
                'rz': '#9E9E9E',     # Rz - Gray
                'id': '#9E9E9E',     # Identity - Gray
                'barrier': '#9E9E9E', # Barrier - Gray (matches the : symbol)
                'reset': '#F4511E',  # Reset - Gray (matches black circle)
                'if_else': '#E65100', # Conditional - Orange (matches 'if')
        
                # Row 4 gates (pink row)
                'rx': '#FF00FF',     # Rx - Pink
                'ry': '#FF00FF',     # Ry - Pink
                'rxx': '#FF00FF',    # Rxx - Pink
                'rzz': '#FF00FF',    # Rzz - Pink
                'u': '#FF00FF',      # U - Pink
        
                # Row 5/bottom row - special gates
                'cx': '#4285F4',     # CNOT - Blue (matches the control target symbol)
                'ccx': '#9E9E9E',    # Toffoli - Gray (RCCX in image)
                'cz': '#4285F4',     # CZ - Blue 
                'cp': '#4FC3F7',     # Controlled phase - Light blue
                'swap': '#4FC3F7',   # SWAP - Light blue
        
                # Measurement - appears black in the image
                'measure': '#A9A9A9', # Measurement - Black
                
                # Conditional operation - added with a distinctive color
                'conditional': '#4CAF50', # Conditional - Orange
            },
            'linecolor': '#424242',        # Dark gray lines
            'textcolor': '#212121',          # Changed to white for better contrast on colored backgrounds
            'showindex': True,
            'fontsize': 10,               # Reduced font size
        }

    def _get_qiskit_compatible_style(self):
        """Returns a copy of the circuit style with only Qiskit-compatible options."""
        qiskit_style = self.circuit_style.copy()
        # Remove non-standard keys that Qiskit doesn't support
        for key in ['gridcolor', 'qubitlinecolor']:
            if key in qiskit_style:
                qiskit_style.pop(key)
        return qiskit_style
    
    def _format_angle(self, angle_value: float) -> str:
        """Format rotation angles in terms of π for better readability."""
        pi = np.pi
        # Use a smaller epsilon for better precision with pi fractions
        epsilon = 1e-6
        
        # Common fractions of pi with their string representations
        pi_fractions = {
            pi/4: "π/4",
            pi/3: "π/3",
            pi/2: "π/2", 
            pi/6: "π/6",
            pi/8: "π/8",
            5*pi/4: "5π/4",
            3*pi/4: "3π/4",
            2*pi/3: "2π/3",
            5*pi/3: "5π/3",
            3*pi/2: "3π/2",
            2*pi: "2π",
            pi: "π",
            -pi/4: "-π/4",
            -pi/3: "-π/3",
            -pi/2: "-π/2",
            -2*pi/3: "-2π/3",
            -3*pi/4: "-3π/4",
            -pi: "-π",
            -3*pi/2: "-3π/2"
        }
        
        # Use tolerance-based comparison for pi fractions
        for val, label in pi_fractions.items():
            if abs(angle_value - val) < epsilon:
                return label
                
        # For multiples of π/12 (common in quantum algorithms)
        num = round(angle_value * 12 / pi)
        if abs(angle_value - num * pi/12) < epsilon:
            if num == 0:
                return "0"
            elif num == 12:
                return "π"
            elif num == -12:
                return "-π"
            elif num % 12 == 0:
                return f"{num//12}π"
            else:
                # Get the simplified fraction
                from math import gcd
                g = gcd(abs(num), 12)
                if g > 1:
                    num, den = num // g, 12 // g
                    return f"{num}π/{den}" if num != 1 else f"π/{den}"
                return f"{num}π/12"
        
        # For other values, return formatted float with 2 decimal places
        return f"{angle_value:.2f}"

    def _apply_figure_styling(self, fig: plt.Figure, ax: Optional[plt.Axes] = None):
        """Apply consistent styling to the matplotlib figure."""
        if ax is None and len(fig.axes) > 0:
            ax = fig.axes[0]
        
        if ax:
            # Style spines
            for spine in ax.spines.values():
                spine.set_edgecolor(self.circuit_style.get('linecolor', '#424242'))
                spine.set_linewidth(0.8)
            
            # Set background color
            ax.set_facecolor(self.circuit_style.get('backgroundcolor', 'white'))
            
            # Remove title and axis labels
            ax.set_title("")
            ax.set_xlabel("")
            ax.set_ylabel("")
        
        # Set figure background
        fig.patch.set_facecolor(self.circuit_style.get('backgroundcolor', 'white'))
        
        # Apply tight layout with reduced padding
        fig.tight_layout(pad=0.1)

    def _process_circuit_for_visualization(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Process the circuit for enhanced visualization."""
        # Create a copy to work with to avoid modifying the original
        circuit_to_draw = circuit.copy()
        
        # Define a nice representation for various gates
        gate_display_names = {
            'h': 'H',
            'x': 'X',
            'y': 'Y',
            'z': 'Z',
            's': 'S',
            't': 'T',
            'sdg': 'S†',
            'tdg': 'T†',
            'cx': 'CNOT',
            'cz': 'CZ',
            'ccx': 'CCX',
            'swap': 'SWAP',
            'rzz': 'RZZ',
            'measure': '',  # Empty label for measurement gates
            'reset': 'R',
        }
        
        # Process gate labels and visualization properties
        for i, (instruction, qargs, cargs) in enumerate(circuit_to_draw.data):
            gate_name = instruction.name.lower()
            logger.info(f"Processing gate {i}: {gate_name} with params: {getattr(instruction, 'params', [])}")
            
            # Check if this is a conditional gate by looking at the label
            if hasattr(instruction, 'label') and instruction.label and 'IF' in instruction.label:
                logger.info(f"Found conditional gate with label: {instruction.label}")
                continue  # The label is already set correctly

            # Handle conditional gates by looking for modified gate names
            elif "_if_" in gate_name:
                try:
                    # Extract the original gate name and condition value
                    parts = gate_name.split("_if_")
                    if len(parts) == 2:
                        original_gate = parts[0]
                        condition_value = parts[1]
                        gate_label = gate_display_names.get(original_gate, original_gate.upper())
                        label = f"{gate_label} IF({condition_value})"
                        instruction.label = label
                        logger.info(f"Processing conditional gate via name: {label}")
                        # Also set a special color for this gate
                        if hasattr(instruction, '_display'):
                            instruction._display['fill'] = self.circuit_style['displaycolor'].get('conditional', '#E65100')
                except Exception as e:
                    logger.error(f"Error processing conditional gate name: {e}")

            # Handle rotation gates (rx, ry, rz)
            elif gate_name in ['rx', 'ry', 'rz', 'p', 'u1', 'cp'] and hasattr(instruction, 'params') and instruction.params:
                try:
                    angle_param = instruction.params[0]
                    angle_str = self._format_angle(angle_param)
                    
                    # Create compact gate labels - simplify format for rotation gates
                    if gate_name in ['rx', 'ry', 'rz']:
                        # Shorter gate names
                        if gate_name == 'rx':
                            label = f"Rx({angle_str})"
                        elif gate_name == 'ry':
                            label = f"Ry({angle_str})"
                        elif gate_name == 'rz':
                            label = f"Rz({angle_str})"
                    elif gate_name == 'p':
                        label = f"P({angle_str})"
                    elif gate_name == 'u1':
                        label = f"U1({angle_str})"
                    elif gate_name == 'cp':
                        label = f"CP({angle_str})"
                    
                    logger.info(f"Setting rotation gate label: {label}")
                    instruction.label = label
                    
                except Exception as e:
                    logger.error(f"Error processing rotation gate {gate_name}: {e}")

            # Handle two-qubit gates
            elif gate_name in gate_display_names:
                instruction.label = gate_display_names[gate_name]
            
            # Handle controlled rotation gates
            elif gate_name in ['crx', 'cry', 'crz', 'cu1'] and hasattr(instruction, 'params') and instruction.params:
                try:
                    angle_param = instruction.params[0]
                    angle_str = self._format_angle(angle_param)
                    
                    # Shorter gate names
                    if gate_name == 'crx':
                        label = f"CRx({angle_str})"
                    elif gate_name == 'cry':
                        label = f"CRy({angle_str})"
                    elif gate_name == 'crz':
                        label = f"CRz({angle_str})"
                    elif gate_name == 'cu1':
                        label = f"CU1({angle_str})"
                        
                    instruction.label = label
                except Exception as e:
                    logger.error(f"Error processing controlled rotation gate {gate_name}: {e}")
            
            # Handle conditional operations - using condition attribute if available
            elif hasattr(instruction, 'condition') and instruction.condition is not None:
                try:
                    creg, val = instruction.condition
                    gate_label = gate_display_names.get(gate_name, gate_name.upper())
                    label = f"{gate_label} IF({val})"
                    instruction.label = label
                    logger.info(f"Processing conditional gate via condition attribute: {label}")
                except Exception as e:
                    logger.error(f"Error processing conditional gate: {e}")

        return circuit_to_draw

    def generate_circuit_image(self, circuit: QuantumCircuit, fold: Optional[int] = None, 
                              transparent_bg: bool = True, dpi: int = 150) -> str:  # Return just the string
        """Generate a visualization of the quantum circuit with optimized dimensions."""
        logger.info(f"Generating circuit image with {len(circuit.data)} gates")
        logger.info(f"Circuit operations: {[instr.name for instr, _, _ in circuit.data]}")

        # Process the circuit for visualization
        circuit_to_draw = self._process_circuit_for_visualization(circuit)

        # Calculate circuit properties
        n_gates = len(circuit_to_draw.data)
        n_qubits = circuit_to_draw.num_qubits
        n_cbits = circuit_to_draw.num_clbits
        total_rows = n_qubits + n_cbits
        
        # Calculate width based on number of gates, but smaller scale
        width = min(18, max(6, n_gates * 0.5))  # Reduced scaling factor
        
        # Calculate height based on qubits and cbits, smaller scale
        height = max(1.5, total_rows * 0.35 + 0.2)  # Reduced scaling factor
        
        # Only fold if more than 20 gates (increased threshold)
        auto_fold = None
        if n_gates > 20:  # Only fold after 20 gates
            auto_fold = max(10, min(20, n_gates // 3))  # Larger fold columns
            fold_factor = max(1, n_gates // auto_fold if auto_fold > 0 else 1)
            height = max(height, 1 + 0.35 * total_rows * fold_factor)

        # Create figure with adjusted size
        fig = plt.figure(figsize=(width, height), dpi=dpi)
        ax = fig.add_subplot(111)

        # Draw the circuit with proper styling
        try:
            # Set name to empty to avoid the title
            circuit_to_draw.name = ""
            
            # Draw the circuit
            style = self._get_qiskit_compatible_style()
            style['fontsize'] = 10  # Smaller font size for gate labels
            
            circuit_to_draw.draw(
                output='mpl',
                style=style,
                scale=0.8,  # Smaller gate sizes
                plot_barriers=True,
                idle_wires=True,
                fold=auto_fold,
                ax=ax
            )
            
            # Find all the measure gates and add an 'M' text on top
            import matplotlib.patches as patches
            measure_rects = []
            for child in ax.get_children():
                if isinstance(child, patches.Rectangle):
                    # Check if this is a measurement gate by color
                    face_color = child.get_facecolor()
                    if len(face_color) == 4 and face_color[0] <= 0.15 and face_color[1] <= 0.15 and face_color[2] <= 0.15:
                        measure_rects.append(child)
            
            # Add 'M' label to each measurement gate
            for rect in measure_rects:
                # Get the center of the rectangle
                x = rect.get_x() + rect.get_width()/2
                y = rect.get_y() + rect.get_height()/2
                
                # Add a white 'M' text
                text = ax.text(
                    x, y, 'M', 
                    color='white', 
                    ha='center', 
                    va='center', 
                    fontsize=9, 
                    fontweight='bold'
                )
                
                # Add a slight shadow to make it more visible
                text.set_path_effects([
                    path_effects.withStroke(linewidth=0.5, foreground='black')
                ])
            
            # Check for any conditional gates (those with "IF" in their label)
            # and create a more distinctive visual appearance for them
            conditional_gates = []
            for child in ax.get_children():
                if isinstance(child, patches.Rectangle):
                    # Try to find the associated text element that contains "IF"
                    rect_x = child.get_x() + child.get_width()/2
                    rect_y = child.get_y() + child.get_height()/2
                    
                    for text_obj in ax.texts:
                        # Check if text object is close to this rectangle
                        if "IF" in text_obj.get_text() and abs(text_obj.get_position()[0] - rect_x) < 0.5:
                            # This is a conditional gate
                            conditional_gates.append((child, text_obj))
                            # Change rectangle color to indicate conditional
                            child.set_facecolor(self.circuit_style['displaycolor'].get('conditional', '#4CAF50'))
                            child.set_edgecolor('none')
                            # Make text white for better contrast
                            text_obj.set_color('black')
                            # Add a shadow to make it more readable
                            
                            text_obj.set_fontsize(6)
                            text_obj.set_fontweight('normal')  # Use normal weight instead of bold
                            
                            text_obj.set_path_effects([])
            
            # Apply consistent figure styling
            self._apply_figure_styling(fig, ax)
            
        except Exception as e:
            logger.error(f"Error drawing circuit: {e}")
            ax.text(0.5, 0.5, f"Error generating circuit visualization: {str(e)}",
                   horizontalalignment='center', verticalalignment='center',
                   fontsize=10, color='red')
            ax.axis('off')

        # Trim excess whitespace around the figure
        plt.tight_layout(pad=0.05)
        
        # Save with tight bounding box to remove excess margins
        buf = io.BytesIO()
        plt.savefig(buf, format='png', 
                   transparent=transparent_bg, 
                   dpi=dpi, 
                   bbox_inches='tight', 
                   pad_inches=0.02)  # Minimal padding
        plt.close(fig)
        buf.seek(0)
        
        # Return just the base64 encoded image as a string
        return base64.b64encode(buf.getvalue()).decode('utf-8')

    def generate_statevector_visualization(self, statevector=None, plot_type='bloch', 
                           title=None, figsize=(8, 6), dpi=150) -> str:
        """Generate a visualization of a quantum state."""
        logger.info(f"Generating statevector visualization of type {plot_type}")
        fig = plt.figure(figsize=figsize)
    
        try:
            # Instead of trying to process the statevector, just create an error image
            # This is a temporary solution until we can debug the issue properly
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, 
                    "Statevector visualization is not available for this circuit type",
                    horizontalalignment='center', 
                    verticalalignment='center',
                    fontsize=12, 
                    color='black',
                    wrap=True)
            ax.axis('off')
            fig.patch.set_facecolor('white')
        
        except Exception as e:
            logger.error(f"Error generating state visualization: {e}")
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Error generating state visualization: {str(e)}",
                horizontalalignment='center', verticalalignment='center',
                fontsize=12, color='red')
            ax.axis('off')
    
        # Convert to base64 image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
    
        # Return just the base64 encoded image as a string
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    
    def generate_measurement_histogram(self, counts=None, figsize=(8, 5), dpi=150, title=None) -> str:
        """Generate a histogram visualization of measurement results."""
        fig = plt.figure(figsize=figsize)
        
        try:
            # Handle case where a circuit is passed instead of counts
            if counts is None:
                raise ValueError("No measurement results provided")
                
            if isinstance(counts, QuantumCircuit):
                # Simulate the circuit to get counts
                from qiskit import Aer, execute
                circuit = counts  # Rename for clarity
                
                # Check if circuit has measurements
                has_measurements = any(instr.name == 'measure' for instr, _, _ in circuit.data)
                
                if not has_measurements:
                    # Add measurements to all qubits if none exist
                    measuring_circuit = circuit.copy()
                    measuring_circuit.measure_all()
                else:
                    measuring_circuit = circuit
                    
                # Run simulation
                backend = Aer.get_backend('qasm_simulator')
                job = execute(measuring_circuit, backend, shots=1024)
                counts = job.result().get_counts()
            
            logger.info(f"Generating measurement histogram with {len(counts)} outcomes")
            plot_histogram(counts, title=title or 'Measurement Results')
            
            # Apply consistent styling
            self._apply_figure_styling(fig)
            
        except Exception as e:
            logger.error(f"Error generating histogram: {e}")
            ax = fig.add_subplot(111)
            ax.text(0.5, 0.5, f"Error generating histogram: {str(e)}",
                  horizontalalignment='center', verticalalignment='center',
                  fontsize=12, color='red')
            ax.axis('off')
        
        # Convert to base64 image
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        
        # Return just the base64 encoded image as a string
        return base64.b64encode(buf.getvalue()).decode('utf-8')