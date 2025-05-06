# app/main.py

import logging
logging.getLogger('qiskit').setLevel(logging.ERROR)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# Standard library imports
import logging
from typing import List, Dict, Any

# Application imports
from app.api.routes import (
    text_input,
    circuit_templates,
    image_input,
    exports,
    circuit_upload  # Added our new module
)
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION
)

# Configure CORS
origins = settings.ALLOWED_ORIGINS if hasattr(settings, "ALLOWED_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(text_input.router)
app.include_router(circuit_templates.router)  
app.include_router(image_input.router)
app.include_router(exports.router)
app.include_router(circuit_upload.router)  # Added our new router

@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint providing application information.
    """
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "version": settings.APP_VERSION,
        "features": [
            "Natural language to quantum circuit generation",
            "Educational circuit explanations",
            "Circuit visualization",
            "Multiple export formats",
            "Template-based circuit generation",
            "Image to quantum circuit generation",
            "Jupyter Notebook export",
            "Circuit file upload and processing"  # Added our new feature
        ]
    }

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for monitoring systems.
    """
    return {"status": "healthy"}

def custom_openapi():
    """
    Customize OpenAPI schema with additional information.
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        routes=app.routes,
    )
    
    # Add additional information to the schema if needed
    openapi_schema["info"]["x-logo"] = {
        "url": "https://path-to-your-logo-if-available.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi