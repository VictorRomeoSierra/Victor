import logging
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pgvector.sqlalchemy import cosine_distance

from app.services.embedding_service import EmbeddingService

# Configure logging
logger = logging.getLogger("victor-retrieval-service")

class RetrievalService:
    """
    Service for retrieving relevant code chunks based on a query.
    """
    
    def __init__(self):
        self.embedding_service = EmbeddingService()
    
    async def retrieve(
        self, 
        db: AsyncSession, 
        query: str, 
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve the most relevant code chunks for a query.
        """
        try:
            # Generate embedding for the query
            query_embedding = await self.embedding_service.generate_embedding(query)
            
            # Build the SQL query
            sql = """
            WITH ranked_chunks AS (
                SELECT 
                    c.id as chunk_id,
                    c.content,
                    c.chunk_type,
                    c.start_line,
                    c.end_line,
                    c.metadata,
                    f.file_path,
                    f.file_name,
                    cosine_distance(e.embedding, :query_embedding) as distance
                FROM 
                    victor.embeddings e
                JOIN 
                    victor.chunks c ON e.chunk_id = c.id
                JOIN 
                    victor.files f ON c.file_id = f.id
                WHERE 
                    e.model_name = :model_name
            """
            
            # Add filters if provided
            params = {
                "query_embedding": query_embedding.tolist(),
                "model_name": self.embedding_service.model_name,
                "limit": top_k
            }
            
            if filters:
                if "file_extension" in filters:
                    sql += " AND f.file_extension = :file_extension"
                    params["file_extension"] = filters["file_extension"]
                if "chunk_type" in filters:
                    sql += " AND c.chunk_type = :chunk_type"
                    params["chunk_type"] = filters["chunk_type"]
                if "file_path" in filters:
                    sql += " AND f.file_path LIKE :file_path"
                    params["file_path"] = f"%{filters['file_path']}%"
            
            # Complete the query
            sql += """
                ORDER BY distance ASC
                LIMIT :limit
            )
            SELECT * FROM ranked_chunks;
            """
            
            # Execute the query
            result = await db.execute(text(sql), params)
            chunks = result.mappings().all()
            
            # Convert to list of dictionaries
            return [dict(chunk) for chunk in chunks]
            
        except Exception as e:
            logger.error(f"Error retrieving chunks: {e}")
            raise
    
    async def retrieve_by_keyword(
        self,
        db: AsyncSession,
        keyword: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve code chunks containing a specific keyword.
        """
        try:
            # Build the SQL query
            sql = """
            SELECT 
                c.id as chunk_id,
                c.content,
                c.chunk_type,
                c.start_line,
                c.end_line,
                c.metadata,
                f.file_path,
                f.file_name
            FROM 
                victor.chunks c
            JOIN 
                victor.files f ON c.file_id = f.id
            WHERE 
                c.content ILIKE :keyword
            """
            
            # Add filters if provided
            params = {
                "keyword": f"%{keyword}%",
                "limit": top_k
            }
            
            if filters:
                if "file_extension" in filters:
                    sql += " AND f.file_extension = :file_extension"
                    params["file_extension"] = filters["file_extension"]
                if "chunk_type" in filters:
                    sql += " AND c.chunk_type = :chunk_type"
                    params["chunk_type"] = filters["chunk_type"]
                if "file_path" in filters:
                    sql += " AND f.file_path LIKE :file_path"
                    params["file_path"] = f"%{filters['file_path']}%"
            
            # Complete the query
            sql += """
                ORDER BY 
                    CASE 
                        WHEN c.content ILIKE :exact_keyword THEN 0
                        ELSE 1
                    END,
                    length(c.content) ASC
                LIMIT :limit
            """
            
            params["exact_keyword"] = f"%{keyword}%"
            
            # Execute the query
            result = await db.execute(text(sql), params)
            chunks = result.mappings().all()
            
            # Convert to list of dictionaries
            return [dict(chunk) for chunk in chunks]
            
        except Exception as e:
            logger.error(f"Error retrieving chunks by keyword: {e}")
            raise
    
    async def hybrid_search(
        self,
        db: AsyncSession,
        query: str,
        keyword: Optional[str] = None,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform a hybrid search using both vector similarity and keyword matching.
        """
        try:
            # If no keyword is provided, extract it from the query
            if not keyword:
                # Simple keyword extraction - in a real system, use NLP
                keywords = [word for word in query.split() if len(word) > 3]
                keyword = keywords[0] if keywords else query.split()[0]
            
            # Get results from both methods
            vector_results = await self.retrieve(db, query, top_k=top_k, filters=filters)
            keyword_results = await self.retrieve_by_keyword(db, keyword, top_k=top_k, filters=filters)
            
            # Combine and deduplicate results
            seen_ids = set()
            combined_results = []
            
            # Add vector results first (higher priority)
            for result in vector_results:
                chunk_id = result["chunk_id"]
                if chunk_id not in seen_ids:
                    seen_ids.add(chunk_id)
                    combined_results.append(result)
            
            # Add keyword results
            for result in keyword_results:
                chunk_id = result["chunk_id"]
                if chunk_id not in seen_ids and len(combined_results) < top_k:
                    seen_ids.add(chunk_id)
                    combined_results.append(result)
            
            return combined_results[:top_k]
            
        except Exception as e:
            logger.error(f"Error performing hybrid search: {e}")
            raise