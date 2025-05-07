# run.py
import uvicorn
import sys

if __name__ == "__main__":
    try:
        uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
    except Exception as e:
        print(f"Error starting the application: {e}")
        sys.exit(1)
