-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema
CREATE SCHEMA IF NOT EXISTS victor;

-- Create code_files table
CREATE TABLE IF NOT EXISTS victor.code_files (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    repo_name TEXT,
    branch_name TEXT,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    file_content TEXT,
    language TEXT
);

-- Create code_chunks table
CREATE TABLE IF NOT EXISTS victor.code_chunks (
    id SERIAL PRIMARY KEY,
    file_id INTEGER REFERENCES victor.code_files(id) ON DELETE CASCADE,
    chunk_type TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_chunk UNIQUE(file_id, start_line, end_line)
);

-- Create relations table
CREATE TABLE IF NOT EXISTS victor.code_relations (
    id SERIAL PRIMARY KEY,
    source_chunk_id INTEGER REFERENCES victor.code_chunks(id) ON DELETE CASCADE,
    target_chunk_id INTEGER REFERENCES victor.code_chunks(id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_relation UNIQUE(source_chunk_id, target_chunk_id, relation_type)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_code_files_path ON victor.code_files(file_path);
CREATE INDEX IF NOT EXISTS idx_code_chunks_file_id ON victor.code_chunks(file_id);
CREATE INDEX IF NOT EXISTS idx_code_relations_source ON victor.code_relations(source_chunk_id);
CREATE INDEX IF NOT EXISTS idx_code_relations_target ON victor.code_relations(target_chunk_id);

-- Create vector search index (hnsw)
CREATE INDEX IF NOT EXISTS idx_code_chunks_embedding ON victor.code_chunks USING hnsw (embedding vector_l2_ops);