-- Create lua_chunks table for storing parsed Lua code with embeddings
CREATE TABLE IF NOT EXISTS lua_chunks (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR NOT NULL,
    chunk_type VARCHAR NOT NULL,  -- 'function', 'table', 'comment', etc.
    content TEXT NOT NULL,
    meta_data JSONB,
    embedding vector(768),  -- 768 dimensions for nomic-embed-text
    line_start INTEGER NOT NULL,
    line_end INTEGER NOT NULL,
    parent_id INTEGER REFERENCES lua_chunks(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient searching
CREATE INDEX IF NOT EXISTS idx_lua_chunks_file_path ON lua_chunks(file_path);
CREATE INDEX IF NOT EXISTS idx_lua_chunks_chunk_type ON lua_chunks(chunk_type);
CREATE INDEX IF NOT EXISTS idx_lua_chunks_parent_id ON lua_chunks(parent_id);
CREATE INDEX IF NOT EXISTS idx_lua_chunks_embedding ON lua_chunks USING ivfflat (embedding vector_cosine_ops);

-- Create GIN index for JSONB meta_data
CREATE INDEX IF NOT EXISTS idx_lua_chunks_meta_data ON lua_chunks USING gin (meta_data);

-- Create text search index
CREATE INDEX IF NOT EXISTS idx_lua_chunks_content ON lua_chunks USING gin (to_tsvector('english', content));

-- Create trigger to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_lua_chunks_updated_at BEFORE UPDATE
    ON lua_chunks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();