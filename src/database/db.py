import os
from typing import Dict, List, Optional, Any, Tuple

import psycopg2
from psycopg2.extras import Json, execute_values

class VectorDB:
    def __init__(self, 
                 host: str = None, 
                 port: int = None, 
                 dbname: str = None, 
                 user: str = None, 
                 password: str = None):
        """
        Initialize the vector database connection.
        
        Args:
            host: PostgreSQL host
            port: PostgreSQL port
            dbname: Database name
            user: Database user
            password: Database password
        """
        self.host = host or os.getenv("POSTGRES_HOST", "localhost")
        self.port = port or int(os.getenv("POSTGRES_PORT", "5432"))
        self.dbname = dbname or os.getenv("POSTGRES_DB", "vectordb")
        self.user = user or os.getenv("POSTGRES_USER", "victor_user")
        self.password = password or os.getenv("POSTGRES_PASSWORD", "")
        
        self.conn = None
        
    def connect(self) -> None:
        """
        Connect to the PostgreSQL database.
        """
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(
                    host=self.host,
                    port=self.port,
                    dbname=self.dbname,
                    user=self.user,
                    password=self.password
                )
                print(f"Connected to {self.dbname} at {self.host}:{self.port}")
            except Exception as e:
                print(f"Error connecting to database: {e}")
                raise
                
    def disconnect(self) -> None:
        """
        Disconnect from the PostgreSQL database.
        """
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            print("Disconnected from database")
            
    def store_file(self, file_path: str, content: str, repo_name: Optional[str] = None, 
                  branch_name: Optional[str] = None, language: str = "lua") -> int:
        """
        Store a file in the database.
        
        Args:
            file_path: Path to the file
            content: Content of the file
            repo_name: Name of the repository
            branch_name: Name of the branch
            language: Programming language
            
        Returns:
            ID of the inserted file
        """
        self.connect()
        
        cursor = self.conn.cursor()
        try:
            # Check if file already exists
            cursor.execute(
                "SELECT id FROM victor.code_files WHERE file_path = %s",
                (file_path,)
            )
            result = cursor.fetchone()
            
            if result:
                # Update existing file
                file_id = result[0]
                cursor.execute(
                    """
                    UPDATE victor.code_files 
                    SET file_content = %s, repo_name = %s, branch_name = %s, language = %s, last_updated = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """,
                    (content, repo_name, branch_name, language, file_id)
                )
            else:
                # Insert new file
                cursor.execute(
                    """
                    INSERT INTO victor.code_files (file_path, file_content, repo_name, branch_name, language) 
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (file_path, content, repo_name, branch_name, language)
                )
                file_id = cursor.fetchone()[0]
                
            self.conn.commit()
            return file_id
        except Exception as e:
            self.conn.rollback()
            print(f"Error storing file: {e}")
            raise
        finally:
            cursor.close()
            
    def store_chunks(self, file_id: int, chunks: List[Dict[str, Any]]) -> List[int]:
        """
        Store code chunks in the database.
        
        Args:
            file_id: ID of the file
            chunks: List of code chunks
            
        Returns:
            List of chunk IDs
        """
        self.connect()
        
        cursor = self.conn.cursor()
        try:
            # Delete existing chunks for this file
            cursor.execute(
                "DELETE FROM victor.code_chunks WHERE file_id = %s",
                (file_id,)
            )
            
            # Insert new chunks
            chunk_ids = []
            for chunk in chunks:
                cursor.execute(
                    """
                    INSERT INTO victor.code_chunks 
                    (file_id, chunk_type, start_line, end_line, content, embedding, metadata) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        file_id, 
                        chunk["chunk_type"], 
                        chunk["start_line"], 
                        chunk["end_line"], 
                        chunk["content"], 
                        chunk["embedding"], 
                        Json(chunk["metadata"]) if "metadata" in chunk else None
                    )
                )
                chunk_id = cursor.fetchone()[0]
                chunk_ids.append(chunk_id)
                
            self.conn.commit()
            return chunk_ids
        except Exception as e:
            self.conn.rollback()
            print(f"Error storing chunks: {e}")
            raise
        finally:
            cursor.close()
            
    def search_similar(self, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar code chunks.
        
        Args:
            query_vector: Query vector
            limit: Maximum number of results
            
        Returns:
            List of similar code chunks
        """
        self.connect()
        
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                """
                SELECT c.id, c.content, c.metadata, f.file_path, c.chunk_type,
                       c.start_line, c.end_line, 1 - (c.embedding <-> %s) as similarity
                FROM victor.code_chunks c
                JOIN victor.code_files f ON c.file_id = f.id
                ORDER BY c.embedding <-> %s
                LIMIT %s
                """,
                (query_vector, query_vector, limit)
            )
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "content": row[1],
                    "metadata": row[2],
                    "file_path": row[3],
                    "chunk_type": row[4],
                    "start_line": row[5],
                    "end_line": row[6],
                    "similarity": row[7]
                })
                
            return results
        except Exception as e:
            print(f"Error searching similar chunks: {e}")
            raise
        finally:
            cursor.close()