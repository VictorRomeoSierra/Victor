# Victor DCS Assistant - System Overview

## Architecture

```
┌─────────────────┐     ┌──────────────┐     ┌───────────────┐
│   Open-WebUI    │────▶│     N8N      │────▶│  Victor API   │
│  (User Input)   │     │  (Routing)   │     │ (RAG Context) │
└─────────────────┘     └──────────────┘     └───────────────┘
                               │                      │
                               ▼                      ▼
                        ┌──────────────┐     ┌───────────────┐
                        │ Ollama/Claude│◀────│  PostgreSQL   │
                        │   (Models)   │     │  (Embeddings) │
                        └──────────────┘     └───────────────┘
```

## Components

### 1. Open-WebUI
- **Purpose**: User interface for chat interactions
- **Functions**: 10 custom pipe functions (9 Ollama models + Claude)
- **Location**: https://ai.victorromeosierra.com

### 2. N8N Workflows
- **Purpose**: Intelligent routing and request enhancement
- **Webhooks**:
  - Ollama: `https://n8n.victorromeosierra.com/webhook/victor-local-chat`
  - Claude: `https://n8n.victorromeosierra.com/webhook/victor-chat`
- **Features**: 
  - DCS keyword detection
  - Automatic RAG enhancement for DCS queries
  - Model routing

### 3. Victor API
- **Purpose**: RAG system for XSAF code context
- **Port**: 8000 (Docker container on Mac Mini)
- **Endpoints**:
  - `/context` - Get relevant code snippets
  - `/search` - Raw search results
  - `/stats` - Database statistics
  - `/health` - Health check
- **Database**: 37k+ indexed XSAF code chunks

### 4. Models
- **Ollama Models** (Local):
  - CodeLlama (primary for DCS)
  - Qwen2.5 Coder
  - Llama 3.2
  - Mistral
  - DeepSeek R1
  - Gemma 2
  - Codestral
  - DeepSeek Coder v2
  - CodeGemma
- **Claude Model** (Cloud via LiteLLM):
  - Claude 3.7 Sonnet

### 5. PostgreSQL Database
- **Purpose**: Vector storage for code embeddings
- **Port**: 5433
- **Extension**: pgvector
- **Schema**: lua_chunks table with embeddings

## Data Flow

1. **User Query** → Open-WebUI function
2. **Function** → N8N webhook with messages
3. **N8N** checks for DCS keywords:
   - **If DCS**: → Victor API → Get context → Enhance prompt → Model
   - **If not DCS**: → Direct to Model
4. **Model** generates response
5. **Response** → N8N → Open-WebUI → User

## Key Features

- **Automatic Enhancement**: DCS queries automatically get XSAF code context
- **Multi-Model Support**: 10 different models available
- **Fallback Handling**: Graceful degradation if services unavailable
- **Configurable**: Timeouts and debug modes available
- **Production Ready**: All services containerized and monitored

## Maintenance

- **Victor API**: Docker container auto-restarts
- **N8N**: Persistent workflows with version control
- **Database**: Regular backups recommended
- **Monitoring**: Check logs for errors or performance issues

## Future Enhancements

1. **Streaming Responses**: Better UX with progressive text
2. **GitHub Webhooks**: Auto-reindex on code changes
3. **Caching**: Redis for frequent queries
4. **Analytics**: Usage tracking and optimization