"""
Alternative fix for vector search SQL syntax
"""

# The issue is that asyncpg doesn't support the ::vector casting syntax in parameters
# We have a few options:

# Option 1: Use CAST function (what we just did)
sql_option1 = """
    SELECT 
        id,
        file_path,
        chunk_type,
        content,
        meta_data,
        line_start,
        line_end,
        1 - (embedding <=> CAST(:embedding AS vector)) as similarity
    FROM lua_chunks
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> CAST(:embedding AS vector)
    LIMIT :limit
"""

# Option 2: Format the vector as a string literal
sql_option2 = """
    SELECT 
        id,
        file_path,
        chunk_type,
        content,
        meta_data,
        line_start,
        line_end,
        1 - (embedding <=> '[{embedding_str}]'::vector) as similarity
    FROM lua_chunks
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> '[{embedding_str}]'::vector
    LIMIT {limit}
"""

# Option 3: Use a parameterized query with explicit type
sql_option3 = """
    SELECT 
        id,
        file_path,
        chunk_type,
        content,
        meta_data,
        line_start,
        line_end,
        1 - (embedding <=> $1::vector) as similarity
    FROM lua_chunks
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> $1::vector
    LIMIT $2
"""