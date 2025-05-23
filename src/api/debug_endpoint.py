"""
Debug endpoint to test embedding generation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import httpx
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class DebugEmbeddingRequest(BaseModel):
    text: str

@router.post("/debug/embedding")
async def debug_embedding(request: DebugEmbeddingRequest):
    """
    Debug endpoint to test embedding generation
    """
    result = {
        "text": request.text,
        "env": {
            "OLLAMA_BASE_URL": os.getenv("OLLAMA_BASE_URL", "not set"),
            "OLLAMA_EMBED_MODEL": os.getenv("OLLAMA_EMBED_MODEL", "not set"),
            "EMBEDDING_PROVIDER": os.getenv("EMBEDDING_PROVIDER", "not set")
        },
        "steps": []
    }
    
    # Step 1: Try to connect to Ollama
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Test connection
            health_response = await client.get(f"{ollama_url}/api/tags")
            result["steps"].append({
                "step": "connect_ollama",
                "status": "success",
                "status_code": health_response.status_code
            })
            
            # Try to generate embedding
            embed_response = await client.post(
                f"{ollama_url}/api/embeddings",
                json={
                    "model": os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
                    "prompt": request.text
                }
            )
            
            if embed_response.status_code == 200:
                embed_data = embed_response.json()
                embedding = embed_data.get("embedding", [])
                result["steps"].append({
                    "step": "generate_embedding",
                    "status": "success",
                    "embedding_dim": len(embedding),
                    "first_5_values": embedding[:5] if embedding else []
                })
                result["embedding_generated"] = True
            else:
                result["steps"].append({
                    "step": "generate_embedding",
                    "status": "failed",
                    "status_code": embed_response.status_code,
                    "error": embed_response.text
                })
                result["embedding_generated"] = False
                
    except Exception as e:
        result["steps"].append({
            "step": "connect_ollama",
            "status": "failed",
            "error": str(e)
        })
        result["embedding_generated"] = False
    
    return result