# Victor - Existing Infrastructure

## Overview
This document details the existing infrastructure components that are already set up and operational for the Victor project.

## Current Components

### Local Mac Mini Environment
- **Ollama**: 
  - Already installed on the Mac Mini
  - Listening on port 11434
  - Configured for GPU acceleration
  - Will be used for local model execution

### Docker Containers
- **PostgreSQL**:
  - Running in a Docker container
  - pgvector extension installed
  - Listening on port 5433 (non-standard port)
  - Ready for vector database implementation

- **LiteLLM**:
  - Running in a Docker container
  - Listening on port 4000
  - Already configured with connection to Claude
  - Will be used for orchestrating model interactions

- **Open-WebUI**:
  - Running in a Docker container
  - Listening on port 3000
  - Connected to LiteLLM via OpenAI API connection
  - Provides the user interface

### External Infrastructure
- **Nginx Reverse Proxy**:
  - Running on a separate computer
  - Already forwarding requests from https://ai.victorromeosierra.com/
  - Configured to point to Open-WebUI

## Integration Considerations

### System Touchpoints
1. **Database Schema**:
   - Need to implement our vector database schema in the existing PostgreSQL instance
   - No need to create a new container

2. **Embedding Service**:
   - New component to be developed
   - Will connect to existing PostgreSQL
   - Will interface with Ollama for embeddings

3. **LiteLLM Integration**:
   - Existing LiteLLM setup needs configuration for our use case
   - RAG integration needs to be implemented

4. **Open-WebUI Customization**:
   - May need customization for code-specific interactions
   - Should maintain existing functionality

5. **Automation Solution**:
   - Need to implement GitHub webhook handling
   - May use N8N or a simpler solution based on needs

## Network Architecture

```
                                 ┌───────────────────┐
                                 │                   │
                                 │  Nginx Reverse    │
                                 │     Proxy         │
                                 │                   │
                                 └─────────┬─────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           Mac Mini                                   │
│                                                                      │
│  ┌───────────────┐    ┌────────────────┐    ┌──────────────────┐    │
│  │               │    │                │    │                  │    │
│  │   Open-WebUI  │◄───┤    LiteLLM     │◄───┤      Ollama      │    │
│  │  (port 3000)  │    │   (port 4000)  │    │   (port 11434)   │    │
│  │               │    │                │    │                  │    │
│  └───────┬───────┘    └────────────────┘    └──────────────────┘    │
│          │                                           ▲               │
│          │                                           │               │
│          │                                  ┌────────┴───────┐       │
│          │                                  │                │       │
│          │                                  │   Embedding    │       │
│          │                                  │    Service     │       │
│          │                                  │    (new)       │       │
│          │                                  │                │       │
│          │                                  └────────┬───────┘       │
│          │                                           │               │
│          │                                           │               │
│          ▼                                           ▼               │
│  ┌───────────────┐                          ┌────────────────┐       │
│  │               │                          │                │       │
│  │  GitHub       │                          │   PostgreSQL   │       │
│  │  Webhook      │                          │   (port 5433)  │       │
│  │  Handler      │                          │                │       │
│  │               │                          │                │       │
│  └───────────────┘                          └────────────────┘       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Next Steps

1. Implement the database schema in the existing PostgreSQL instance
2. Develop the embedding service to process the Lua codebase
3. Configure LiteLLM to work with our RAG implementation
4. Set up GitHub webhook handling for automatic updates
5. Test integration with Open-WebUI