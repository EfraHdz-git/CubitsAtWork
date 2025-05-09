# application.py
import sys
import os

# Debug information
print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print("Directory contents:", os.listdir('.'))
print("Python path:", sys.path)

try:
    from app.main import app
    print("Successfully imported app.main.app")
    application = app
except Exception as e:
    print(f"Error importing app.main.app: {e}")
    import traceback
    traceback.print_exc()
    
    # Fallback application
    from fastapi import FastAPI
    application = FastAPI()
    
    @application.get("/")
    async def debug_root():
        return {
            "status": "error",
            "message": "Application failed to load properly",
            "python_version": sys.version,
            "cwd": os.getcwd(),
            "dir_contents": os.listdir('.'),
            "python_path": sys.path,
            "error": str(e)
        }