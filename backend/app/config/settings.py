# app/config.py
import os
from pydantic import BaseModel  # Using BaseModel instead of BaseSettings

class Settings(BaseModel):
    """Application settings."""
    
    # Application settings
    APP_NAME: str = "Quantum Circuit Generator"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Generate quantum circuits from natural language or images"
    
    # API Keys
    OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
    
    # Quantum Backend settings
    IBMQ_TOKEN: str = os.environ.get("IBMQ_TOKEN", "")
    USE_IBMQ: bool = False
    
    # Visualization settings
    MAX_QUBIT_VISUALIZATION: int = 8  # Maximum qubits for which to generate visualizations

# Initialize settings
settings = Settings()