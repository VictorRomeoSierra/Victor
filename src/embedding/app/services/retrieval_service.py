"""
Retrieval Service - Searches and retrieves relevant code chunks
Ported from dcs-lua-analyzer project
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
import numpy as np

from .embedding_service import EmbeddingService

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("victor-retrieval-service")

class RetrievalService:
    """
    Service for retrieving relevant code chunks based on queries.
    """
    
    def __init__(self, embedding_service: Optional[EmbeddingService] = None):
        """
        Initialize the retrieval service.
        
        Args:
            embedding_service: Optional embedding service instance
        """
        self.embedding_service = embedding_service or EmbeddingService()
        self.search_limit = int(os.getenv("SEARCH_LIMIT", "10"))
    
    async def text_search(
        self, 
        db: AsyncSession,
        query: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform text-based search using PostgreSQL's ILIKE.
        
        Args:
            db: Database session
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching chunks with metadata
        """
        try:
            limit = limit or self.search_limit
            
            # SQL query for text search
            sql = text("""
                SELECT 
                    id,
                    file_path,
                    chunk_type,
                    content,
                    meta_data,
                    line_start,
                    line_end
                FROM lua_chunks
                WHERE content ILIKE :query
                ORDER BY 
                    CASE 
                        WHEN chunk_type = 'function' THEN 1
                        WHEN chunk_type = 'table_constructor' THEN 2
                        ELSE 3
                    END,
                    line_start
                LIMIT :limit
            """)
            
            result = await db.execute(
                sql,
                {"query": f"%{query}%", "limit": limit}
            )
            
            chunks = []
            for row in result:
                chunks.append({
                    "id": row.id,
                    "file_path": row.file_path,
                    "chunk_type": row.chunk_type,
                    "content": row.content,
                    "metadata": row.meta_data,
                    "line_start": row.line_start,
                    "line_end": row.line_end,
                    "score": 1.0  # Text search doesn't have a natural score
                })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error in text search: {e}")
            return []
    
    async def vector_search(
        self,
        db: AsyncSession,
        query: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search using embeddings.
        
        Args:
            db: Database session
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching chunks with similarity scores
        """
        try:
            limit = limit or self.search_limit
            
            # Generate embedding for the query
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            # Convert to list for SQL
            embedding_list = query_embedding.tolist()
            
            # SQL query for vector similarity search
            sql = text("""
                SELECT 
                    id,
                    file_path,
                    chunk_type,
                    content,
                    meta_data,
                    line_start,
                    line_end,
                    1 - (embedding <=> :embedding::vector) as similarity
                FROM lua_chunks
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> :embedding::vector
                LIMIT :limit
            """)
            
            result = await db.execute(
                sql,
                {"embedding": embedding_list, "limit": limit}
            )
            
            chunks = []
            for row in result:
                chunks.append({
                    "id": row.id,
                    "file_path": row.file_path,
                    "chunk_type": row.chunk_type,
                    "content": row.content,
                    "metadata": row.meta_data,
                    "line_start": row.line_start,
                    "line_end": row.line_end,
                    "score": float(row.similarity)
                })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Error in vector search: {e}")
            return []
    
    async def hybrid_search(
        self,
        db: AsyncSession,
        query: str,
        limit: Optional[int] = None,
        text_weight: float = 0.3,
        vector_weight: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining text and vector similarity.
        
        Args:
            db: Database session
            query: Search query
            limit: Maximum number of results
            text_weight: Weight for text search results
            vector_weight: Weight for vector search results
            
        Returns:
            List of matching chunks with combined scores
        """
        try:
            limit = limit or self.search_limit
            
            # Perform both searches
            text_results = await self.text_search(db, query, limit * 2)
            vector_results = await self.vector_search(db, query, limit * 2)
            
            # Create a combined score map
            score_map = {}
            
            # Add text search results
            for result in text_results:
                chunk_id = result["id"]
                score_map[chunk_id] = {
                    "chunk": result,
                    "text_score": result["score"],
                    "vector_score": 0.0
                }
            
            # Add vector search results
            for result in vector_results:
                chunk_id = result["id"]
                if chunk_id in score_map:
                    score_map[chunk_id]["vector_score"] = result["score"]
                else:
                    score_map[chunk_id] = {
                        "chunk": result,
                        "text_score": 0.0,
                        "vector_score": result["score"]
                    }
            
            # Calculate combined scores
            combined_results = []
            for chunk_id, data in score_map.items():
                combined_score = (
                    text_weight * data["text_score"] + 
                    vector_weight * data["vector_score"]
                )
                chunk = data["chunk"].copy()
                chunk["score"] = combined_score
                chunk["text_score"] = data["text_score"]
                chunk["vector_score"] = data["vector_score"]
                combined_results.append(chunk)
            
            # Sort by combined score and limit
            combined_results.sort(key=lambda x: x["score"], reverse=True)
            return combined_results[:limit]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
    
    def format_context_for_llm(
        self,
        chunks: List[Dict[str, Any]],
        max_tokens: int = 8000
    ) -> str:
        """
        Format retrieved chunks into context for LLM consumption.
        
        Args:
            chunks: List of retrieved chunks
            max_tokens: Maximum tokens to include (rough estimate)
            
        Returns:
            Formatted context string
        """
        context_parts = []
        current_tokens = 0
        
        for chunk in chunks:
            # Create a formatted chunk with metadata
            chunk_text = f"File: {chunk['file_path']} (lines {chunk['line_start']}-{chunk['line_end']})\n"
            chunk_text += f"Type: {chunk['chunk_type']}\n"
            
            # Add DCS keywords if present
            if chunk.get('metadata', {}).get('dcs_keywords'):
                keywords = ', '.join(chunk['metadata']['dcs_keywords'])
                chunk_text += f"DCS Keywords: {keywords}\n"
            
            chunk_text += f"```lua\n{chunk['content']}\n```\n"
            
            # Rough token estimation (4 chars = 1 token)
            chunk_tokens = len(chunk_text) // 4
            
            if current_tokens + chunk_tokens > max_tokens:
                break
            
            context_parts.append(chunk_text)
            current_tokens += chunk_tokens
        
        return "\n".join(context_parts)
    
    async def retrieve(
        self, 
        db: AsyncSession, 
        query: str, 
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant code chunks for a query.
        Wrapper for compatibility with existing code.
        """
        # Use hybrid search by default
        return await self.hybrid_search(db, query, limit=top_k)
    
    async def retrieve_by_keyword(
        self,
        db: AsyncSession,
        keyword: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve code chunks containing a specific keyword.
        Wrapper for compatibility with existing code.
        """
        return await self.text_search(db, keyword, limit=top_k)
    
    async def get_related_chunks(
        self,
        db: AsyncSession,
        chunk_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get chunks related to a specific chunk (same file, nearby lines).
        
        Args:
            db: Database session
            chunk_id: ID of the reference chunk
            limit: Maximum number of related chunks
            
        Returns:
            List of related chunks
        """
        try:
            # First get the reference chunk
            sql = text("""
                SELECT file_path, line_start, line_end
                FROM lua_chunks
                WHERE id = :chunk_id
            """)
            
            result = await db.execute(sql, {"chunk_id": chunk_id})
            ref_chunk = result.first()
            
            if not ref_chunk:
                return []
            
            # Get related chunks from the same file
            sql = text("""
                SELECT 
                    id,
                    file_path,
                    chunk_type,
                    content,
                    meta_data,
                    line_start,
                    line_end,
                    ABS(line_start - :ref_line) as distance
                FROM lua_chunks
                WHERE file_path = :file_path
                AND id != :chunk_id
                ORDER BY distance
                LIMIT :limit
            """)
            
            result = await db.execute(
                sql,
                {
                    "file_path": ref_chunk.file_path,
                    "ref_line": ref_chunk.line_start,
                    "chunk_id": chunk_id,
                    "limit": limit
                }
            )
            
            related_chunks = []
            for row in result:
                related_chunks.append({
                    "id": row.id,
                    "file_path": row.file_path,
                    "chunk_type": row.chunk_type,
                    "content": row.content,
                    "metadata": row.meta_data,
                    "line_start": row.line_start,
                    "line_end": row.line_end,
                    "distance": row.distance
                })
            
            return related_chunks
            
        except Exception as e:
            logger.error(f"Error getting related chunks: {e}")
            return []