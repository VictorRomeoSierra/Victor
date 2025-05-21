from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
import datetime

Base = declarative_base()

class File(Base):
    __tablename__ = "files"
    __table_args__ = {"schema": "victor"}
    
    id = Column(Integer, primary_key=True)
    file_path = Column(Text, nullable=False, unique=True)
    file_name = Column(Text, nullable=False)
    file_extension = Column(Text, nullable=False)
    last_modified = Column(TIMESTAMP, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    content_hash = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class CodeChunk(Base):
    __tablename__ = "chunks"
    __table_args__ = {"schema": "victor"}
    
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("victor.files.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    chunk_type = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    metadata = Column(JSON, nullable=False, default={})
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class Embedding(Base):
    __tablename__ = "embeddings"
    __table_args__ = {"schema": "victor"}
    
    id = Column(Integer, primary_key=True)
    chunk_id = Column(Integer, ForeignKey("victor.chunks.id", ondelete="CASCADE"), nullable=False)
    model_name = Column(Text, nullable=False)
    dimensions = Column(Integer, nullable=False)
    embedding = Column(Vector(1536))  # Adjust dimensions based on model
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)

class Dependency(Base):
    __tablename__ = "dependencies"
    __table_args__ = {"schema": "victor"}
    
    id = Column(Integer, primary_key=True)
    source_file_id = Column(Integer, ForeignKey("victor.files.id", ondelete="CASCADE"), nullable=False)
    target_file_id = Column(Integer, ForeignKey("victor.files.id", ondelete="CASCADE"), nullable=False)
    dependency_type = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)

class Function(Base):
    __tablename__ = "functions"
    __table_args__ = {"schema": "victor"}
    
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("victor.files.id", ondelete="CASCADE"), nullable=False)
    chunk_id = Column(Integer, ForeignKey("victor.chunks.id", ondelete="CASCADE"))
    name = Column(Text, nullable=False)
    signature = Column(Text, nullable=False)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    description = Column(Text)
    metadata = Column(JSON, nullable=False, default={})
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class FunctionCall(Base):
    __tablename__ = "function_calls"
    __table_args__ = {"schema": "victor"}
    
    id = Column(Integer, primary_key=True)
    source_function_id = Column(Integer, ForeignKey("victor.functions.id", ondelete="CASCADE"))
    target_function_id = Column(Integer, ForeignKey("victor.functions.id", ondelete="CASCADE"))
    file_id = Column(Integer, ForeignKey("victor.files.id", ondelete="CASCADE"), nullable=False)
    line_number = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)

class Variable(Base):
    __tablename__ = "variables"
    __table_args__ = {"schema": "victor"}
    
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey("victor.files.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    var_type = Column(Text)
    scope = Column(Text, nullable=False)
    line_number = Column(Integer, nullable=False)
    description = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)

class QueryHistory(Base):
    __tablename__ = "query_history"
    __table_args__ = {"schema": "victor"}
    
    id = Column(Integer, primary_key=True)
    query = Column(Text, nullable=False)
    context = Column(JSON, nullable=False, default={})
    response = Column(Text)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.datetime.utcnow)
    user_feedback = Column(Integer)  # -1, 0, 1 for negative, neutral, positive