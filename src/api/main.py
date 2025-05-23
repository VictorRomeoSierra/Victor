"""
Victor API - Main FastAPI application
Integrates DCS Lua code analysis directly without external service calls
"""

from fastapi import FastAPI, Body, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import os
import sys
import logging

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
logger.info(f"Python path: {sys.path}")
logger.info(f"Working directory: {os.getcwd()}")

try:
    # Import embedding app services
    from embedding.app.services.retrieval_service import RetrievalService
    from embedding.app.services.embedding_service import EmbeddingService
    # Import debug endpoint
    from api.debug_endpoint import router as debug_router
    
    # Import database session
    from api.db import get_db
except ImportError as e:
    logger.error(f"Import error: {e}")
    raise

app = FastAPI(title="Victor API", description="API for Victor DCS Lua coding assistant")

# Add debug router if available
try:
    app.include_router(debug_router, prefix="/api", tags=["debug"])
except NameError:
    logger.warning("Debug router not available")

# Initialize services
embedding_service = EmbeddingService()
retrieval_service = RetrievalService(embedding_service)

class EnhancePromptRequest(BaseModel):
    prompt: str
    model: Optional[str] = "codellama"

class EnhancePromptResponse(BaseModel):
    enhanced_prompt: str

class ReindexRequest(BaseModel):
    directory_path: str
    recursive: bool = True
    file_pattern: str = "*.lua"

class SearchRequest(BaseModel):
    query: str
    limit: int = 5
    search_type: str = "hybrid"  # "text", "vector", or "hybrid"

class ContextRequest(BaseModel):
    query: str
    limit: int = 5
    detailed: bool = True

@app.get("/")
async def root():
    return {"message": "Welcome to Victor API", "status": "operational"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/enhance_prompt", response_model=EnhancePromptResponse)
async def enhance_prompt(
    request: EnhancePromptRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Enhance a prompt with context from the DCS Lua codebase.
    """
    query = request.prompt
    model = request.model
    
    # Check if query is DCS-related
    if is_dcs_related(query):
        try:
            # Search for relevant code snippets
            chunks = await retrieval_service.hybrid_search(db, query, limit=5)
            
            if chunks:
                # Format context for LLM
                context = retrieval_service.format_context_for_llm(chunks)
                
                # Enhance the prompt with real context
                enhanced_prompt = f"""You are an expert in DCS World Lua programming assistant.
Use the following relevant code snippets from the XSAF codebase to help answer the question.

{context}

Question: {query}

Instructions:
- Reference specific functions, variables, or patterns from the provided code snippets when relevant
- Explain how the code works and provide examples based on the XSAF patterns shown
- If the code snippets don't contain relevant information, acknowledge this and provide general DCS Lua guidance
"""
                return {"enhanced_prompt": enhanced_prompt}
            else:
                # No relevant snippets found, but still enhance for DCS context
                enhanced_prompt = f"""You are an expert in DCS World Lua programming assistant.

Question: {query}

Instructions:
- Provide detailed guidance for DCS World Lua scripting
- Include practical examples and best practices
- Focus on DCS-specific APIs and patterns
"""
                return {"enhanced_prompt": enhanced_prompt}
                
        except Exception as e:
            logger.error(f"Error in enhance_prompt: {e}")
            # Fall through to return original prompt
    
    # Return original prompt if not DCS-related or if enhancement fails
    return {"enhanced_prompt": query}

@app.post("/search")
async def search_code(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Search for code snippets in the DCS Lua codebase.
    """
    try:
        if request.search_type == "text":
            results = await retrieval_service.text_search(db, request.query, request.limit)
        elif request.search_type == "vector":
            results = await retrieval_service.vector_search(db, request.query, request.limit)
        else:  # hybrid
            results = await retrieval_service.hybrid_search(db, request.query, request.limit)
        
        return {
            "results": results,
            "count": len(results),
            "search_type": request.search_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")

@app.post("/context")
async def get_context(
    request: ContextRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Get formatted context for a query, suitable for RAG.
    """
    try:
        # Search for relevant chunks
        chunks = await retrieval_service.hybrid_search(db, request.query, request.limit)
        
        if request.detailed:
            # Return detailed information
            return {
                "context": retrieval_service.format_context_for_llm(chunks),
                "snippet_count": len(chunks),
                "results": chunks
            }
        else:
            # Return just the formatted context
            return {
                "context": retrieval_service.format_context_for_llm(chunks),
                "snippet_count": len(chunks)
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting context: {str(e)}")

@app.get("/stats")
async def get_index_stats(db: AsyncSession = Depends(get_db)):
    """
    Get statistics about the current index.
    """
    try:
        # Count total chunks
        total_result = await db.execute(text("SELECT COUNT(*) FROM lua_chunks"))
        total_chunks = total_result.scalar()
        
        # Count chunks by type
        type_result = await db.execute(
            text("""
                SELECT chunk_type, COUNT(*) as count 
                FROM lua_chunks 
                GROUP BY chunk_type 
                ORDER BY count DESC
            """)
        )
        chunks_by_type = {row.chunk_type: row.count for row in type_result}
        
        # Count unique files
        file_result = await db.execute(
            text("SELECT COUNT(DISTINCT file_path) FROM lua_chunks")
        )
        unique_files = file_result.scalar()
        
        # Count chunks with embeddings
        embedding_result = await db.execute(
            text("SELECT COUNT(*) FROM lua_chunks WHERE embedding IS NOT NULL")
        )
        chunks_with_embeddings = embedding_result.scalar()
        
        return {
            "total_chunks": total_chunks,
            "unique_files": unique_files,
            "chunks_with_embeddings": chunks_with_embeddings,
            "chunks_by_type": chunks_by_type,
            "embedding_provider": embedding_service.get_provider_info()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.post("/reindex")
async def reindex_codebase(request: ReindexRequest):
    """
    Trigger re-indexing of the codebase.
    Note: This endpoint returns instructions for manual reindexing.
    In the future, this could trigger an async job.
    """
    return {
        "status": "info",
        "message": "To reindex the codebase, use the indexing service",
        "instructions": [
            "1. Use the embedding service's /index/directory endpoint",
            "2. Or run the indexing script directly",
            f"3. Directory: {request.directory_path}",
            f"4. Recursive: {request.recursive}",
            f"5. Pattern: {request.file_pattern}"
        ],
        "note": "The indexing will automatically exclude XSAF.DB/, Moose/, and Mist.lua files"
    }

def is_dcs_related(query: str) -> bool:
    """
    Check if a query is related to DCS World.
    """
    dcs_keywords = [
        "dcs", "lua", "mission", "script", "trigger", "event", "xsaf",
        "waypoint", "aircraft", "helicopter", "unit", "group", "coalition",
        "task", "zone", "airbase", "missioncommands", "timer", "scheduler"
    ]
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in dcs_keywords)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)