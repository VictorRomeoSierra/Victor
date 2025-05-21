# Refined Integration Plan for Victor

After reviewing the existing tools (LiteLLM, Ollama, Open-WebUI) and the dcs-lua-analyzer code, this document outlines a refined integration plan that takes advantage of the capabilities of each component.

## Architecture Overview

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
         └────────────►│   Victor API    │
                       │  (RAG Service)  │
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
                                ▲
                                │
                                │
                       ┌─────────────────┐
                       │                 │
                       │      n8n        │◄────┐
                       │                 │     │
                       └─────────────────┘     │
                                               │
                                         GitHub Webhooks
```

## Component Roles

### 1. Open-WebUI

Open-WebUI provides the user interface for interacting with Victor. It already has robust support for:
- Chat conversations with multiple models
- File uploads for RAG
- Web search capabilities
- Responsive design for different devices
- Markdown and LaTeX support
- User authentication and permissions

This eliminates the need to build a custom UI from scratch.

### 2. LiteLLM

LiteLLM will serve as the model router and orchestrator with:
- Pre-request hooks for RAG enhancement
- Model selection based on query type
- Unified interface for different Ollama models 
- Fallback mechanisms for model failures

### 3. Ollama

Ollama will be the model execution engine, providing:
- Local execution of various LLM models
- GPU acceleration for inference
- Model management (pull, create, etc.)

### 4. Victor API Service

This will be a new service built from the dcs-lua-analyzer code that provides:
- Code parsing using tree-sitter
- Vector storage and retrieval
- Enhanced context building for LLMs
- DCS-specific code understanding

### 5. PostgreSQL with pgvector

Will store the code vectors and metadata with:
- Semantic search capabilities
- Metadata storage for code relationships
- Efficient vector search using pgvector

### 6. n8n Automation Platform

n8n will handle workflow automation with a focus on:
- GitHub integration for automatic codebase updates
- Automated re-indexing of code when changes are detected
- Scheduled maintenance tasks
- Notification workflows for system events
- Database maintenance and backups
- Potential integration with VSCode extensions

## Implementation Approach

### Phase 1: Core API Development

#### Move and Adapt dcs-lua-analyzer Core Components

1. **Extract the Core Parser**: 
   - Move the `lua_embedder.py` code to Victor project
   - Enhance parser with better DCS-specific pattern recognition
   - Improve chunking strategy for Lua code

2. **Adapt Database Schema**:
   - Use the existing pgvector schema as starting point
   - Add additional metadata fields for DCS context
   - Create migration scripts for schema updates

3. **Build Victor API Service**:
   - Create FastAPI endpoints for LiteLLM integration
   - Implement context enhancement for prompts
   - Build specialized formatting for DCS code

### Phase 2: LiteLLM Integration

1. **Configure LiteLLM**:
   - Set up pre-request hooks to the Victor API
   - Configure model routing for different query types
   - Implement fallback strategies

2. **Create Context Enhancement Endpoint**:
   ```python
   @app.post("/enhance_prompt")
   async def enhance_prompt(
       request: EnhancePromptRequest
   ):
       query = request.prompt
       model = request.model
       
       # Check if query is DCS-related
       if is_dcs_related(query):
           # Get relevant code snippets
           snippets = await retrieve_code_snippets(query)
           
           # Format context based on model
           context = format_context_for_model(snippets, model)
           
           # Enhance the prompt
           enhanced_prompt = f"""You are an expert in DCS World Lua programming.
           Use the following code snippets to help answer the question.
           
           {context}
           
           Question: {query}
           """
           
           return {"enhanced_prompt": enhanced_prompt}
       
       # Return original prompt if not DCS-related
       return {"enhanced_prompt": query}
   ```

3. **Connect to Open-WebUI**:
   - Configure Open-WebUI to use LiteLLM endpoint
   - Set up custom prompt templates for DCS queries

### Phase 3: n8n Workflow Implementation

1. **Set Up n8n with PostgreSQL**:
   - Use the existing docker-compose configuration for n8n with PostgreSQL
   - Configure environment variables for database connections
   - Set up persistent storage for workflows and data

2. **Create GitHub Integration Workflow**:
   - Set up a webhook endpoint to receive GitHub events
   - Create a workflow to filter for relevant file changes
   - Implement automated code pulling and processing

3. **Implement Re-indexing Workflow**:
   - Build a workflow that calls the Victor API to re-index changed files
   - Set up automatic vector database updates
   - Create notification system for completed updates

4. **Database Maintenance Workflows**:
   - Schedule regular database backups
   - Create cleanup processes for outdated entries
   - Implement performance optimization tasks

### Phase 4: Enhanced Features

1. **Implement Multi-Context Reasoning**:
   - Add different context types (function context, module context, etc.)
   - Create context selection logic based on query
   - Build context composition strategies

2. **Add Code Relationship Awareness**:
   - Track dependencies between files
   - Map function calls and relationships
   - Enhance context with related code

3. **Create DCS-Specific Templates**:
   - Develop specialized templates for common DCS questions
   - Add parameter suggestions for DCS functions
   - Include documentation links for relevant topics

## Deployment Strategy

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  # Open-WebUI (already running)
  # Configuration to connect to LiteLLM

  # LiteLLM
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

  # Victor API Service
  victor-api:
    build:
      context: .
      dockerfile: ./victor-api/Dockerfile
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_HOST=postgres
      - POSTGRES_DB=vectordb
      - POSTGRES_USER=victor_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
    volumes:
      - ./victor-api:/app
    depends_on:
      - postgres

  # PostgreSQL with pgvector
  postgres:
    image: ankane/pgvector:latest
    ports:
      - "5433:5432"
    environment:
      - POSTGRES_DB=vectordb
      - POSTGRES_USER=victor_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-db.sql:/docker-entrypoint-initdb.d/init-db.sql

  # n8n for workflow automation
  n8n:
    image: docker.n8n.io/n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=${POSTGRES_DB}
      - DB_POSTGRESDB_USER=${POSTGRES_USER}
      - DB_POSTGRESDB_PASSWORD=${POSTGRES_PASSWORD}
      - N8N_HOST=${N8N_HOST:-localhost}
      - N8N_PORT=5678
      - NODE_ENV=production
      - WEBHOOK_URL=${WEBHOOK_URL:-http://localhost:5678/}
      - EXECUTIONS_PROCESS=main
    volumes:
      - n8n_storage:/home/node/.n8n
      - ./workflows:/home/node/.n8n/workflows
    depends_on:
      - postgres
      - victor-api

volumes:
  postgres_data:
  n8n_storage:
```

### LiteLLM Configuration

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
    - path: "http://victor-api:8000/enhance_prompt"
      timeout: 5.0

router_settings:
  timeout: 30.0
  routing_strategy: "simple-shuffle"
```

## Integration with Existing Tools

### Open-WebUI Integration

Open-WebUI already supports LiteLLM through its OpenAI-compatible API interface. We'll utilize this by:

1. Configuring Open-WebUI to connect to LiteLLM:
   - In Open-WebUI settings, set the OpenAI API URL to `http://litellm:4000`
   - Configure model names to match the LiteLLM configuration

2. Utilizing Open-WebUI's Document RAG features:
   - Enable file uploads for Lua files
   - Configure RAG with LiteLLM to use our Victor API

### Ollama Integration

Ollama is already supported by LiteLLM and provides the model execution capabilities. We'll:

1. Ensure the necessary models are available in Ollama:
   ```bash
   ollama pull codellama:7b-instruct
   ollama pull llama3:8b
   ```

2. Create custom models for DCS if needed:
   ```
   FROM codellama:7b-instruct
   
   # set the system message
   SYSTEM """
   You are Victor, an AI assistant specializing in DCS World Lua scripting.
   Your purpose is to help developers understand and modify the XSAF codebase.
   """
   ```

### n8n Integration

n8n will be configured according to the established patterns in n8n-hosting:

1. **Setup and Configuration**:
   - Use the PostgreSQL database configuration from n8n-hosting
   - Configure appropriate environment variables
   - Set up appropriate persistence volumes

2. **GitHub Integration Workflow**:
   - Create webhook endpoints for GitHub repository events
   - Set up a workflow to process push events
   - Implement filtering to only process Lua file changes

3. **Example GitHub Integration Workflow**:
   ```
   [Trigger: Webhook]
         │
         ▼
   [Filter: Push Event]
         │
         ▼
   [Function: Extract Changed Files]
         │
         ▼
   [HTTP Request: Pull Latest Code]
         │
         ▼
   [HTTP Request: Notify Victor API]
         │
         ▼
   [Function: Process Result]
         │
         ▼
   [Notification: Update Complete]
   ```

## Benefits of This Approach

1. **Leverages Existing Tools**: Uses the strengths of Open-WebUI, LiteLLM, Ollama, and n8n without reinventing them.

2. **Focused Development**: Concentrates development effort on the specialized DCS code understanding components.

3. **Modular Architecture**: Each component has a clear responsibility, making it easier to maintain and extend.

4. **Automation-First**: Uses n8n to automate routine tasks like database updates, GitHub integration, and maintenance.

5. **Scalability**: Can easily add more models or features as needed.

6. **User-Friendly**: Provides a polished UI from the start with Open-WebUI.

## Next Steps

1. Set up the project structure for the Victor API service
2. Implement the core parser and database integration
3. Create the context enhancement endpoints
4. Configure LiteLLM with the Victor API
5. Set up n8n and create initial workflows
6. Connect Open-WebUI to LiteLLM
7. Test the full integration with sample DCS code queries