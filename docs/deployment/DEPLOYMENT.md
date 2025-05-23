# Victor API Deployment Guide

This guide covers deploying the updated Victor API with integrated RAG functionality.

## Prerequisites

- Docker and Docker Compose installed on the Mac Mini
- PostgreSQL database running on port 5433 with pgvector extension
- Ollama running on port 11434
- Access to the XSAF codebase (already indexed in the database)

## Deployment Steps

### 1. Update Code

```bash
cd ~/Dev/Victor
git pull origin main
```

### 2. Configure Environment

Copy and edit the environment file:
```bash
cp .env.example .env
```

Edit `.env` to match your setup:
```env
DATABASE_URL=postgresql+asyncpg://postgres:postgres@skyeye-server:5433/vectordb
EMBEDDING_PROVIDER=ollama
OLLAMA_BASE_URL=http://skyeye-server:11434
OLLAMA_EMBED_MODEL=nomic-embed-text
SEARCH_LIMIT=10
```

### 3. Apply Database Migration

Run the migration to create the `lua_chunks` table (if not already present):
```bash
# Using Docker exec to run in the postgres-vector container
docker exec -i postgres-vector psql -U dcs_user -d vectordb < src/database/init/02-lua-chunks.sql

# Or copy the file first if you have issues with input redirection
docker cp src/database/init/02-lua-chunks.sql postgres-vector:/tmp/
docker exec postgres-vector psql -U dcs_user -d vectordb -f /tmp/02-lua-chunks.sql
```

### 4. Deploy Victor API

Use the update script:
```bash
./scripts/update_victor_api.sh
```

Or manually:
```bash
cd src/docker
docker-compose stop victor-api
docker-compose build victor-api
docker-compose up -d victor-api
```

### 5. Verify Deployment

Test the API:
```bash
# From the Mac Mini
python3 scripts/test_victor_api.py http://localhost:8000

# From another machine
python3 scripts/test_victor_api.py http://skyeye-server:8000
```

Check logs:
```bash
cd src/docker
docker-compose logs -f victor-api
```

## API Endpoints

- `GET /health` - Health check
- `GET /stats` - Index statistics
- `POST /search` - Search for code snippets
- `POST /context` - Get formatted context for RAG
- `POST /enhance_prompt` - Enhance prompts with DCS context

## Integration with N8N

The N8N workflow should continue to work without changes. It calls:
- `POST /enhance_prompt` to get enhanced prompts for DCS queries

Test the webhook:
```bash
curl -X POST https://n8n.victorromeosierra.com/webhook-test/victor-chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "How do I create waypoints in DCS?",
    "model": "codellama"
  }'
```

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is accessible from Docker
- Check DATABASE_URL format includes `+asyncpg`
- Ensure pgvector extension is installed

### Embedding Service Issues
- Check Ollama is running: `curl http://skyeye-server:11434/api/tags`
- Verify the embedding model is available: `nomic-embed-text`
- Check logs for embedding errors

### Search Returns No Results
- Verify the lua_chunks table exists:
  ```bash
  docker exec postgres-vector psql -U dcs_user -d vectordb -c "\dt lua_chunks"
  ```
- Check if the table has data:
  ```bash
  docker exec postgres-vector psql -U dcs_user -d vectordb -c "SELECT COUNT(*) FROM lua_chunks;"
  ```
- Check if embeddings are present:
  ```bash
  docker exec postgres-vector psql -U dcs_user -d vectordb -c "SELECT COUNT(*) FROM lua_chunks WHERE embedding IS NOT NULL;"
  ```
- Try text search first to rule out embedding issues

## Maintenance

### Reindexing Code
If you need to reindex the XSAF codebase:
1. Use the original `lua_embedder.py` from dcs-lua-analyzer
2. Or create an indexing endpoint in Victor API (future enhancement)

### Monitoring
- Check container status: `docker-compose ps`
- View logs: `docker-compose logs -f victor-api`
- Monitor memory usage: `docker stats`

## Architecture Notes

The Victor API now includes:
- Tree-sitter based Lua parsing
- Multi-provider embedding support (Ollama, OpenAI)
- Hybrid search (text + vector)
- Direct database access (no external service calls)

This simplifies the architecture by eliminating the need for a separate dcs-lua-analyzer service.