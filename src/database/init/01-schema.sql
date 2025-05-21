-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema
CREATE SCHEMA IF NOT EXISTS victor;

-- Files table to store information about processed files
CREATE TABLE IF NOT EXISTS victor.files (
    id SERIAL PRIMARY KEY,
    file_path TEXT NOT NULL UNIQUE,
    file_name TEXT NOT NULL,
    file_extension TEXT NOT NULL,
    last_modified TIMESTAMP NOT NULL,
    size_bytes INTEGER NOT NULL,
    content_hash TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on file_path
CREATE INDEX IF NOT EXISTS idx_files_path ON victor.files(file_path);

-- Chunks table to store code chunks
CREATE TABLE IF NOT EXISTS victor.chunks (
    id SERIAL PRIMARY KEY,
    file_id INTEGER NOT NULL REFERENCES victor.files(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    chunk_type TEXT NOT NULL, -- 'function', 'class', 'module', etc.
    content TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(file_id, chunk_index)
);

-- Create indexes for chunks
CREATE INDEX IF NOT EXISTS idx_chunks_file_id ON victor.chunks(file_id);
CREATE INDEX IF NOT EXISTS idx_chunks_type ON victor.chunks(chunk_type);

-- Embeddings table to store vector embeddings
CREATE TABLE IF NOT EXISTS victor.embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER NOT NULL REFERENCES victor.chunks(id) ON DELETE CASCADE,
    model_name TEXT NOT NULL,
    dimensions INTEGER NOT NULL,
    embedding vector(1536) NOT NULL, -- Adjust dimensions based on model
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(chunk_id, model_name)
);

-- Create index for vector search
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON victor.embeddings USING ivfflat (embedding vector_cosine_ops);

-- Dependencies table to track relationships between files
CREATE TABLE IF NOT EXISTS victor.dependencies (
    id SERIAL PRIMARY KEY,
    source_file_id INTEGER NOT NULL REFERENCES victor.files(id) ON DELETE CASCADE,
    target_file_id INTEGER NOT NULL REFERENCES victor.files(id) ON DELETE CASCADE,
    dependency_type TEXT NOT NULL, -- 'import', 'require', 'reference', etc.
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_file_id, target_file_id, dependency_type)
);

-- Create indexes for dependencies
CREATE INDEX IF NOT EXISTS idx_dependencies_source ON victor.dependencies(source_file_id);
CREATE INDEX IF NOT EXISTS idx_dependencies_target ON victor.dependencies(target_file_id);

-- Functions table to track function definitions
CREATE TABLE IF NOT EXISTS victor.functions (
    id SERIAL PRIMARY KEY,
    file_id INTEGER NOT NULL REFERENCES victor.files(id) ON DELETE CASCADE,
    chunk_id INTEGER REFERENCES victor.chunks(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    signature TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    description TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for functions
CREATE INDEX IF NOT EXISTS idx_functions_file_id ON victor.functions(file_id);
CREATE INDEX IF NOT EXISTS idx_functions_name ON victor.functions(name);

-- Function calls table to track function invocations
CREATE TABLE IF NOT EXISTS victor.function_calls (
    id SERIAL PRIMARY KEY,
    source_function_id INTEGER REFERENCES victor.functions(id) ON DELETE CASCADE,
    target_function_id INTEGER REFERENCES victor.functions(id) ON DELETE CASCADE,
    file_id INTEGER NOT NULL REFERENCES victor.files(id) ON DELETE CASCADE,
    line_number INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for function calls
CREATE INDEX IF NOT EXISTS idx_function_calls_source ON victor.function_calls(source_function_id);
CREATE INDEX IF NOT EXISTS idx_function_calls_target ON victor.function_calls(target_function_id);

-- Variables table to track global variables
CREATE TABLE IF NOT EXISTS victor.variables (
    id SERIAL PRIMARY KEY,
    file_id INTEGER NOT NULL REFERENCES victor.files(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    var_type TEXT,
    scope TEXT NOT NULL, -- 'global', 'file', 'function', etc.
    line_number INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for variables
CREATE INDEX IF NOT EXISTS idx_variables_file_id ON victor.variables(file_id);
CREATE INDEX IF NOT EXISTS idx_variables_name ON victor.variables(name);

-- Query history table to track user queries
CREATE TABLE IF NOT EXISTS victor.query_history (
    id SERIAL PRIMARY KEY,
    query TEXT NOT NULL,
    context JSONB NOT NULL DEFAULT '{}'::jsonb,
    response TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_feedback INTEGER -- -1, 0, 1 for negative, neutral, positive
);

-- Create index on query history creation time
CREATE INDEX IF NOT EXISTS idx_query_history_created_at ON victor.query_history(created_at);