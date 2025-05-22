"""
Embedding Service - Generates embeddings for code chunks
Supports multiple providers: Ollama, OpenAI, and Sentence Transformers
Ported from dcs-lua-analyzer project
"""

import os
import numpy as np
import torch
import logging
from typing import List, Dict, Any, Optional, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger("victor-embedding-service")

# We'll handle the model import error gracefully for now
try:
    from app.models import Embedding
except ImportError:
    # If models aren't available, we'll skip the database operations
    Embedding = None
    logger.warning("Could not import Embedding model - database operations will be disabled")

class EmbeddingService:
    """
    Service for generating and managing embeddings for code chunks.
    Supports multiple embedding providers.
    """
    
    def __init__(self, provider: Optional[str] = None):
        # Determine the embedding provider
        self.provider = provider or os.getenv("EMBEDDING_PROVIDER", "ollama")
        logger.info(f"Initializing embedding service with provider: {self.provider}")
        
        # Initialize based on provider
        if self.provider == "sentence_transformers":
            self._init_sentence_transformers()
        elif self.provider == "ollama":
            self._init_ollama()
        elif self.provider == "openai":
            self._init_openai()
        else:
            raise ValueError(f"Unknown embedding provider: {self.provider}")
    
    def _init_sentence_transformers(self):
        """Initialize Sentence Transformers model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            logger.info(f"Sentence Transformers model loaded. Dimension: {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to load Sentence Transformers model: {e}")
            raise
    
    def _init_ollama(self):
        """Initialize Ollama configuration."""
        self.model_name = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://skyeye-server:11434")
        self.embedding_dim = 768  # nomic-embed-text dimension
        logger.info(f"Ollama embedding service initialized. Model: {self.model_name}")
    
    def _init_openai(self):
        """Initialize OpenAI configuration."""
        self.model_name = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-ada-002")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set")
        self.embedding_dim = 1536  # ada-002 dimension
        logger.info(f"OpenAI embedding service initialized. Model: {self.model_name}")
    
    async def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate an embedding for a text string.
        """
        try:
            if self.provider == "sentence_transformers":
                return await self._generate_st_embedding(text)
            elif self.provider == "ollama":
                return await self._generate_ollama_embedding(text)
            elif self.provider == "openai":
                return await self._generate_openai_embedding(text)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def _generate_st_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using Sentence Transformers."""
        if torch.cuda.is_available():
            self.model = self.model.to("cuda")
        return self.model.encode(text)
    
    async def _generate_ollama_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using Ollama."""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.ollama_base_url}/api/embeddings",
                json={"model": self.model_name, "prompt": text}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return np.array(data["embedding"], dtype=np.float32)
                else:
                    error_text = await response.text()
                    raise Exception(f"Ollama embedding failed: {response.status} - {error_text}")
    
    async def _generate_openai_embedding(self, text: str) -> np.ndarray:
        """Generate embedding using OpenAI."""
        import openai
        
        openai.api_key = self.openai_api_key
        response = await openai.embeddings.create(
            model=self.model_name,
            input=text
        )
        return np.array(response.data[0].embedding, dtype=np.float32)
    
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
            if self.provider == "sentence_transformers":
                # Ensure the model is on the correct device
                if torch.cuda.is_available():
                    self.model = self.model.to("cuda")
                return self.model.encode(texts)
            else:
                # For Ollama and OpenAI, process sequentially
                embeddings = []
                for text in texts:
                    embedding = await self.generate_embedding(text)
                    embeddings.append(embedding)
                return embeddings
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current embedding provider."""
        return {
            "provider": self.provider,
            "model": self.model_name,
            "dimension": self.embedding_dim,
            "base_url": getattr(self, 'ollama_base_url', None) if self.provider == "ollama" else None
        }