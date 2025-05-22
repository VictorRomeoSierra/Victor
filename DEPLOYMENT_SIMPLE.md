# Simplified Victor API Deployment

This guide uses the simplified deployment that relies on Ollama for embeddings (no PyTorch/ML packages needed).

## Steps to Deploy

1. **On the Mac Mini, pull the latest code:**
```bash
cd ~/Dev/Victor
git pull origin main
```

2. **Stop any existing Victor API containers:**
```bash
cd src/docker
docker-compose down victor-api
# or if using the simple compose file already:
docker-compose -f docker-compose.simple.yml down
```

3. **Run the simplified deployment:**
```bash
cd ~/Dev/Victor
./scripts/deploy_simple.sh
```

## What This Does

- Uses `Dockerfile.simple` which only installs essential packages
- Configures Victor API to use Ollama for embeddings
- Starts both Victor API and n8n services
- No PyTorch, transformers, or other ML packages needed
- Much faster build time and smaller container size

## Verify Deployment

After deployment, the script will automatically check the health endpoint. You can also:

```bash
# Check service status
cd src/docker
docker-compose -f docker-compose.simple.yml ps

# Test the API
curl http://localhost:8000/health
curl http://localhost:8000/stats

# Test search functionality
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "waypoint", "limit": 3, "search_type": "text"}'

# View logs
docker-compose -f docker-compose.simple.yml logs -f victor-api
```

## Environment Variables

The deployment uses these defaults (configured in docker-compose.simple.yml):
- `EMBEDDING_PROVIDER=ollama`
- `OLLAMA_BASE_URL=http://host.docker.internal:11434`
- `OLLAMA_EMBED_MODEL=nomic-embed-text`
- `DATABASE_URL=postgresql+asyncpg://postgres:postgres@host.docker.internal:5433/vectordb`

## Troubleshooting

If you encounter issues:

1. **Check Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

2. **Verify database connection:**
```bash
docker exec postgres-vector psql -U dcs_user -d vectordb -c "SELECT COUNT(*) FROM lua_chunks;"
```

3. **Check Victor API logs:**
```bash
cd src/docker
docker-compose -f docker-compose.simple.yml logs victor-api
```

## Managing Services

```bash
# Stop services
cd src/docker
docker-compose -f docker-compose.simple.yml down

# Restart just Victor API
docker-compose -f docker-compose.simple.yml restart victor-api

# View resource usage
docker stats
```