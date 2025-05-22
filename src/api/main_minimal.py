"""
Minimal Victor API for testing basic functionality
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Victor API Minimal", description="Minimal API for testing")

class EnhancePromptRequest(BaseModel):
    prompt: str
    model: Optional[str] = "codellama"

class EnhancePromptResponse(BaseModel):
    enhanced_prompt: str

@app.get("/")
async def root():
    return {"message": "Welcome to Victor API Minimal", "status": "operational"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "minimal"}

@app.post("/enhance_prompt", response_model=EnhancePromptResponse)
async def enhance_prompt(request: EnhancePromptRequest):
    """
    Minimal enhance prompt - just returns a basic enhancement
    """
    return {"enhanced_prompt": f"[MINIMAL MODE] {request.prompt}"}

@app.get("/debug/env")
async def debug_env():
    """
    Debug endpoint to check environment variables
    """
    return {
        "DATABASE_URL": os.getenv("DATABASE_URL", "not set"),
        "EMBEDDING_PROVIDER": os.getenv("EMBEDDING_PROVIDER", "not set"),
        "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL", "not set"),
        "PYTHONPATH": os.getenv("PYTHONPATH", "not set"),
        "working_dir": os.getcwd()
    }

@app.get("/debug/imports")
async def debug_imports():
    """
    Debug endpoint to test imports
    """
    results = {}
    
    # Test basic imports
    try:
        import sqlalchemy
        results["sqlalchemy"] = sqlalchemy.__version__
    except Exception as e:
        results["sqlalchemy"] = f"Error: {str(e)}"
    
    try:
        import pgvector
        results["pgvector"] = "OK"
    except Exception as e:
        results["pgvector"] = f"Error: {str(e)}"
    
    try:
        import tree_sitter_languages
        results["tree_sitter_languages"] = "OK"
    except Exception as e:
        results["tree_sitter_languages"] = f"Error: {str(e)}"
    
    try:
        from embedding.app.services.retrieval_service import RetrievalService
        results["retrieval_service"] = "OK"
    except Exception as e:
        results["retrieval_service"] = f"Error: {str(e)}"
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)