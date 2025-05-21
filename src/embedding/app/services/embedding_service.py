import os
import numpy as np
import torch
import logging
from typing import List, Dict, Any, Optional, Union
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert

from app.models import Embedding

# Configure logging
logger = logging.getLogger("victor-embedding-service")

class EmbeddingService:
    """
    Service for generating and managing embeddings for code chunks.
    """
    
    def __init__(self):
        # Load the embedding model
        self.model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        logger.info(f"Initializing embedding service with model: {self.model_name}")
        
        try:
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Embedding model loaded successfully. Dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    
    async def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate an embedding for a text string.
        """
        try:
            # Ensure the model is on the correct device
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
            
            # Generate embedding
            embedding = self.model.encode(text)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def store_embedding(
        self, 
        db: AsyncSession,
        chunk_id: int, 
        embedding: np.ndarray
    ) -> int:
        """
        Store an embedding in the database.
        """
        try:
            # Check if an embedding already exists for this chunk
            result = await db.execute(
                select(Embedding).where(
                    Embedding.chunk_id == chunk_id,
                    Embedding.model_name == self.model_name
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update the existing embedding
                existing.embedding = embedding.tolist()
                await db.commit()
                return existing.id
            else:
                # Insert a new embedding
                stmt = insert(Embedding).values(
                    chunk_id=chunk_id,
                    model_name=self.model_name,
                    dimensions=self.embedding_dim,
                    embedding=embedding.tolist()
                )
                result = await db.execute(stmt)
                await db.commit()
                return result.inserted_primary_key[0]
        except Exception as e:
            await db.rollback()
            logger.error(f"Error storing embedding: {e}")
            raise
    
    async def batch_generate_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for a batch of texts.
        """
        try:
            # Ensure the model is on the correct device
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
            
            # Generate embeddings in batch
            embeddings = self.model.encode(texts)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise