import os
import glob
import hashlib
import logging
import re
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete, text

from app.models import File, CodeChunk
from app.services.embedding_service import EmbeddingService
from app.services.lua_parser import LuaParser

# Configure logging
logger = logging.getLogger("victor-indexing-service")

class IndexingService:
    """
    Service for indexing Lua code files into the database.
    """
    
    def __init__(self, embedding_service: EmbeddingService):
        self.embedding_service = embedding_service
        self.lua_parser = LuaParser()
    
    async def index_file(
        self, 
        db: AsyncSession,
        file_path: str,
        content: Optional[str] = None
    ) -> bool:
        """
        Index a single file into the database.
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path) and not content:
                logger.error(f"File does not exist: {file_path}")
                return False
            
            # Read file content if not provided
            if not content:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            # Get file metadata
            file_name = os.path.basename(file_path)
            file_extension = os.path.splitext(file_name)[1].lower()
            
            if not content:
                logger.warning(f"Empty file content: {file_path}")
                return False
            
            # Calculate content hash
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Get file stats
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                last_modified = datetime.fromtimestamp(stat.st_mtime)
                size_bytes = stat.st_size
            else:
                # For content provided without file
                last_modified = datetime.now()
                size_bytes = len(content.encode())
            
            # Check if file already exists in database
            result = await db.execute(
                select(File).where(File.file_path == file_path)
            )
            existing_file = result.scalar_one_or_none()
            
            file_id = None
            if existing_file:
                # Check if the file has changed
                if existing_file.content_hash == content_hash:
                    logger.info(f"File unchanged, skipping: {file_path}")
                    return True
                
                # Update the existing file
                existing_file.last_modified = last_modified
                existing_file.size_bytes = size_bytes
                existing_file.content_hash = content_hash
                existing_file.updated_at = datetime.now()
                file_id = existing_file.id
                
                # Delete existing chunks
                await db.execute(
                    delete(CodeChunk).where(CodeChunk.file_id == file_id)
                )
            else:
                # Insert new file
                stmt = insert(File).values(
                    file_path=file_path,
                    file_name=file_name,
                    file_extension=file_extension,
                    last_modified=last_modified,
                    size_bytes=size_bytes,
                    content_hash=content_hash,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                result = await db.execute(stmt)
                file_id = result.inserted_primary_key[0]
            
            # Parse the file into chunks
            chunks = await self.lua_parser.parse_file_content(content, file_path)
            
            # Insert chunks and generate embeddings
            for idx, chunk in enumerate(chunks):
                # Insert chunk
                stmt = insert(CodeChunk).values(
                    file_id=file_id,
                    chunk_index=idx,
                    chunk_type=chunk["type"],
                    content=chunk["content"],
                    start_line=chunk["start_line"],
                    end_line=chunk["end_line"],
                    metadata=chunk["metadata"],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                result = await db.execute(stmt)
                chunk_id = result.inserted_primary_key[0]
                
                # Generate and store embedding
                embedding = await self.embedding_service.generate_embedding(chunk["content"])
                await self.embedding_service.store_embedding(db, chunk_id, embedding)
            
            await db.commit()
            logger.info(f"Successfully indexed file: {file_path}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error indexing file {file_path}: {e}")
            return False
    
    async def index_directory(
        self,
        db: AsyncSession,
        directory_path: str,
        recursive: bool = True,
        file_pattern: str = "*.lua"
    ) -> Dict[str, Any]:
        """
        Index all matching files in a directory.
        """
        try:
            # Check if directory exists
            if not os.path.isdir(directory_path):
                logger.error(f"Directory does not exist: {directory_path}")
                return {"success": False, "indexed": 0, "failed": 0, "error": "Directory not found"}
            
            # Find all matching files
            pattern = os.path.join(directory_path, "**", file_pattern) if recursive else os.path.join(directory_path, file_pattern)
            files = glob.glob(pattern, recursive=recursive)
            
            logger.info(f"Found {len(files)} files matching pattern {file_pattern} in {directory_path}")
            
            # Index each file
            indexed = 0
            failed = 0
            
            for file_path in files:
                if await self.index_file(db, file_path):
                    indexed += 1
                else:
                    failed += 1
            
            logger.info(f"Indexed {indexed} files, {failed} failed")
            return {
                "success": True,
                "indexed": indexed,
                "failed": failed
            }
            
        except Exception as e:
            logger.error(f"Error indexing directory {directory_path}: {e}")
            return {"success": False, "indexed": 0, "failed": 0, "error": str(e)}
    
    async def delete_file(
        self,
        db: AsyncSession,
        file_path: str
    ) -> bool:
        """
        Delete a file and all its chunks from the database.
        """
        try:
            # Find the file
            result = await db.execute(
                select(File).where(File.file_path == file_path)
            )
            file = result.scalar_one_or_none()
            
            if not file:
                logger.warning(f"File not found in database: {file_path}")
                return False
            
            # Delete the file (will cascade to chunks and embeddings)
            await db.delete(file)
            await db.commit()
            
            logger.info(f"Successfully deleted file: {file_path}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting file {file_path}: {e}")
            return False