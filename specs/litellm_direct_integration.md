# LiteLLM Direct Integration with DCS Lua Analyzer

## Overview
This document outlines the strategy for integrating the core components of dcs-lua-analyzer (parser, database interface, and retrieval system) directly with LiteLLM, bypassing the existing Ollama middleware approach in dcs-lua-analyzer.

## Components to Use from DCS Lua Analyzer

### 1. Lua Parser and Embedder (`lua_embedder.py`)
- Tree-sitter based Lua parsing
- Semantic chunking of code
- Embedding generation functionality
- Database storage utilities

### 2. Database Schema and Interface (`init-db.sql`, models)
- PostgreSQL with pgvector schema
- Vector storage and retrieval
- Text search capabilities

### 3. API Server Core (`api_server.py`)
- Search endpoints
- Context generation
- Structured data formatting

## Components to Replace

### 1. OpenWebUI Middleware (`openwebui_middleware.py`)
- **Replace with**: Direct LiteLLM integration
- **Reason**: Prefer our LiteLLM architecture over Ollama proxy

### 2. Ollama Stream/Simple RAG Scripts
- **Replace with**: LiteLLM handling for RAG
- **Reason**: Centralize model management through LiteLLM

## LiteLLM Direct Integration Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│   Open-WebUI    │────►│     LiteLLM     │────►│     Ollama      │
│                 │     │                 │     │                 │
└────────┬────────┘     └────────┬────────┘     └─────────────────┘
         │                       │
         │                       │
         │                       ▼
         │             ┌─────────────────┐
         │             │                 │
         └────────────►│  Victor API     │
                       │  (Extended      │
                       │   DCS API)      │
                       │                 │
                       └────────┬────────┘
                                │
                                │
                                ▼
                       ┌─────────────────┐
                       │                 │
                       │   PostgreSQL    │
                       │   pgvector      │
                       │                 │
                       └─────────────────┘
```

## Integration Approach

### 1. Create Victor API Server

Build an enhanced API server based on the dcs-lua-analyzer API, but with additional endpoints specifically for LiteLLM:

```python
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
import psycopg2
import json

app = FastAPI(title="Victor API")

# Reuse existing DCS Lua Analyzer endpoints
@app.post("/search")
async def search(request: QueryRequest):
    # Reuse existing search functionality
    pass

@app.post("/context")
async def get_context(request: QueryRequest):
    # Reuse existing context generation
    pass

# New LiteLLM-specific endpoints
@app.post("/litellm/context")
async def get_litellm_context(query: str, model: str = None):
    """Get context specifically formatted for LiteLLM."""
    # Get base context from existing functionality
    results = text_search(conn, query)
    
    # Format context for LiteLLM based on model
    context = format_context_for_model(results, model)
    
    return {
        "context": context,
        "metadata": {
            "snippet_count": len(results),
            "source": "victor_dcs_analyzer"
        }
    }

@app.post("/litellm/enhance_prompt")
async def enhance_prompt(data: dict = Body(...)):
    """Enhance a prompt with context for LiteLLM."""
    query = data.get("prompt", "")
    model = data.get("model", "codellama")
    
    # Only enhance DCS-related queries
    if is_dcs_related(query):
        context = await get_litellm_context(query, model)
        enhanced_prompt = format_prompt_with_context(query, context["context"], model)
        return {"enhanced_prompt": enhanced_prompt}
    
    # Return original prompt if not DCS-related
    return {"enhanced_prompt": query}
```

### 2. Configure LiteLLM to Use Victor API

Configure LiteLLM to use the Victor API for pre-processing prompts:

```yaml
# litellm_config.yaml

model_list:
  - model_name: "ollama/codellama"
    litellm_params:
      model: "ollama/codellama:7b-instruct"
  - model_name: "ollama/llama3"
    litellm_params:
      model: "ollama/llama3:8b"
  - model_name: "ollama/starcoderbase"
    litellm_params:
      model: "ollama/starcoderbase:7b"

hooks:
  pre_request:
    - path: "http://victor-api:8000/litellm/enhance_prompt"
      timeout: 5.0

router_settings:
  timeout: 30.0
  routing_strategy: "simple-shuffle"
```

### 3. Extension Points in LiteLLM

Configure LiteLLM to dynamically route DCS-related queries:

```python
# Example dynamic routing based on content
def custom_get_llm_routing(request: dict):
    prompt = request.get("prompt", "")
    
    # If DCS-related, route to code-specialized model
    if is_dcs_related(prompt):
        return {
            "model": "ollama/codellama:7b-instruct"
        }
    
    # Otherwise, use general-purpose model
    return {
        "model": "ollama/llama3:8b"
    }
```

## Implementation Steps

### 1. Core API Development

- [ ] Move dcs-lua-analyzer code directly into Victor project
- [ ] Extract and modularize core functionality
- [ ] Create enhanced API with LiteLLM-specific endpoints
- [ ] Implement context formatting for different models
- [ ] Add advanced query analysis for DCS detection

### 2. Database Interface

- [ ] Reuse the database schema and connection logic
- [ ] Extend for Victor-specific metadata
- [ ] Optimize for performance
- [ ] Add caching layer

### 3. LiteLLM Configuration

- [ ] Create custom LiteLLM configuration
- [ ] Implement pre-request hooks for context enrichment
- [ ] Set up model routing based on query type
- [ ] Configure fallback strategies

### 4. Open-WebUI Integration

- [ ] Configure Open-WebUI to use LiteLLM directly
- [ ] Create custom UI extensions in Open-WebUI
- [ ] Implement specialized templates for DCS queries
- [ ] Add code-specific UI components

## API Interface

### Context Enhancement API

```
POST /litellm/enhance_prompt
```
Request:
```json
{
  "prompt": "How do I create waypoints for aircraft in DCS?",
  "model": "ollama/codellama:7b-instruct",
  "options": {
    "max_snippets": 5,
    "include_metadata": true
  }
}
```

Response:
```json
{
  "enhanced_prompt": "You are an expert DCS World Lua programming assistant. Answer the following question using the code context provided.\n\nContext:\n[Code snippets related to waypoints]\n\nQuestion: How do I create waypoints for aircraft in DCS?"
}
```

### Model Selection API

```
POST /litellm/select_model
```
Request:
```json
{
  "prompt": "How do I control helicopters in DCS?",
  "available_models": ["ollama/codellama:7b-instruct", "ollama/llama3:8b", "ollama/starcoderbase:7b"]
}
```

Response:
```json
{
  "selected_model": "ollama/codellama:7b-instruct",
  "reasoning": "DCS code question, specialized code model selected"
}
```

## Docker Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  victor-api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://dcs_user:secure_password@postgres:5433/vectordb
    depends_on:
      - postgres

  postgres:
    image: ankane/pgvector:latest
    ports:
      - "5433:5432"
    environment:
      - POSTGRES_USER=dcs_user
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=vectordb
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql

  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    ports:
      - "4000:4000"
    volumes:
      - ./litellm_config.yaml:/app/config.yaml
    environment:
      - PORT=4000
      - HOST=0.0.0.0
    depends_on:
      - victor-api

volumes:
  postgres_data:
```

## Advantages of This Approach

1. **Direct Integration**: No middleware layer between Open-WebUI and LiteLLM
2. **Centralized Model Management**: All model routing handled by LiteLLM
3. **Flexibility**: Easier to switch between different Ollama models
4. **Simplicity**: Cleaner architecture with fewer components
5. **Compatibility**: Works with existing Open-WebUI setup
6. **Scalability**: Can easily add more models and routing logic

## Testing Strategy

1. **Unit Tests**:
   - Test context extraction
   - Test prompt enhancement
   - Test model selection logic

2. **Integration Tests**:
   - Test LiteLLM with Victor API
   - Test Open-WebUI with LiteLLM
   - Test end-to-end query flow

3. **Performance Tests**:
   - Measure response time
   - Test with large code repositories
   - Test concurrent requests

## Next Steps

1. Move dcs-lua-analyzer code directly into Victor project
2. Extract and modularize core functionality
3. Create Victor API with LiteLLM-specific endpoints
4. Configure LiteLLM to use the Victor API
5. Test the integrated system with sample queries