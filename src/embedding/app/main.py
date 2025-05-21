from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import logging
from dotenv import load_dotenv

from app.db import get_db, init_db
from app.models import CodeChunk, Embedding, File
from app.services.embedding_service import EmbeddingService
from app.services.indexing_service import IndexingService
from app.services.retrieval_service import RetrievalService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("victor-embedding")

# Create FastAPI app
app = FastAPI(
    title="Victor Embedding Service",
    description="API for embedding and retrieving Lua code for the Victor AI assistant",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
embedding_service = EmbeddingService()
indexing_service = IndexingService(embedding_service)
retrieval_service = RetrievalService()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    await init_db()
    logger.info("Database initialized")

# Model definitions
class IndexFileRequest(BaseModel):
    file_path: str
    content: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5
    filter: Optional[Dict[str, Any]] = None

class CodeSearchResponse(BaseModel):
    chunks: List[Dict[str, Any]]
    total: int

# Endpoints
@app.post("/index/file", status_code=202)
async def index_file(
    request: IndexFileRequest, 
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """
    Index a file from the codebase for retrieval.
    If content is not provided, the file will be read from disk.
    """
    background_tasks.add_task(
        indexing_service.index_file,
        db,
        request.file_path,
        request.content
    )
    return {"message": f"Indexing of {request.file_path} scheduled"}

@app.post("/index/directory", status_code=202)
async def index_directory(
    directory_path: str,
    recursive: bool = True,
    file_pattern: str = "*.lua",
    background_tasks: BackgroundTasks,
    db = Depends(get_db)
):
    """
    Index all matching files in a directory for retrieval.
    """
    background_tasks.add_task(
        indexing_service.index_directory,
        db,
        directory_path,
        recursive,
        file_pattern
    )
    return {"message": f"Indexing of directory {directory_path} scheduled"}

@app.post("/query", response_model=CodeSearchResponse)
async def query(
    request: QueryRequest,
    db = Depends(get_db)
):
    """
    Query the vector database for relevant code chunks.
    """
    results = await retrieval_service.retrieve(
        db,
        request.query,
        request.top_k,
        request.filter
    )
    return {
        "chunks": results,
        "total": len(results)
    }

@app.get("/stats")
async def get_stats(db = Depends(get_db)):
    """
    Get statistics about the indexed code.
    """
    file_count = await db.execute("SELECT COUNT(*) FROM victor.files")
    file_count = await file_count.scalar()
    
    chunk_count = await db.execute("SELECT COUNT(*) FROM victor.chunks")
    chunk_count = await chunk_count.scalar()
    
    embedding_count = await db.execute("SELECT COUNT(*) FROM victor.embeddings")
    embedding_count = await embedding_count.scalar()
    
    return {
        "files": file_count,
        "chunks": chunk_count,
        "embeddings": embedding_count
    }

@app.delete("/index/file")
async def delete_file(
    file_path: str,
    db = Depends(get_db)
):
    """
    Delete a file and its chunks from the index.
    """
    await indexing_service.delete_file(db, file_path)
    return {"message": f"File {file_path} deleted from index"}

@app.get("/health")
async def health_check():
    """
    Check if the service is healthy.
    """
    return {"status": "healthy"}