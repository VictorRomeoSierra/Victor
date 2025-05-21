# Victor Troubleshooting Guide

## Container Issues

### Checking Container Status
```bash
cd src/docker
docker-compose ps
```

### Viewing Container Logs
```bash
# View logs from all services
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View logs for a specific service
docker-compose logs victor-api
docker-compose logs n8n
```

### Restarting Services
```bash
# Restart all services
docker-compose restart

# Restart a specific service
docker-compose restart victor-api
docker-compose restart n8n
```

### Container Won't Start

1. Check for port conflicts:
   ```bash
   lsof -i :8000
   lsof -i :5678
   ```

2. Check Docker logs for errors:
   ```bash
   docker-compose logs
   ```

3. Verify environment variables:
   ```bash
   docker-compose config
   ```

## Database Connection Issues

1. Verify PostgreSQL is running:
   ```bash
   psql -h localhost -p 5433 -U dcs_user -d vectordb
   ```

2. Check database connection from Victor API:
   ```bash
   # Follow API logs
   docker-compose logs -f victor-api
   ```

3. Check if pgvector extension is installed:
   ```bash
   psql -h localhost -p 5433 -U dcs_user -d vectordb -c "SELECT * FROM pg_extension WHERE extname = 'vector';"
   ```

## n8n Webhook Issues

1. Verify n8n is running:
   ```bash
   curl http://localhost:5678/healthz
   ```

2. Check if webhooks are registered:
   - Open n8n at http://localhost:5678
   - Go to "Workflows" and check if webhook nodes are active

3. Verify Nginx configuration:
   ```bash
   # On the Nginx server
   curl -I https://ai.victorromeosierra.com/n8n/healthz
   ```

4. Check webhook logs:
   ```bash
   docker-compose logs -f n8n
   ```

## Ollama Connection Issues

1. Verify Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. Check Victor API logs for Ollama connection errors:
   ```bash
   docker-compose logs -f victor-api
   ```

## LiteLLM Connection Issues

1. Verify LiteLLM is running:
   ```bash
   curl http://localhost:4000/health
   ```

2. Check if LiteLLM can connect to Ollama:
   ```bash
   curl -X POST http://localhost:4000/v1/models
   ```

## Common Solutions

1. **Restart Services**:
   ```bash
   cd src/docker
   docker-compose down
   docker-compose up -d
   ```

2. **Update Environment Variables**:
   Edit the .env file, then restart services:
   ```bash
   nano .env
   docker-compose down
   docker-compose up -d
   ```

3. **Rebuild Victor API**:
   ```bash
   docker-compose build victor-api
   docker-compose up -d
   ```

4. **Check Network Connectivity**:
   ```bash
   # Test connection to PostgreSQL
   telnet localhost 5433
   
   # Test connection to Ollama
   telnet localhost 11434
   
   # Test connection to LiteLLM
   telnet localhost 4000
   ```

5. **Update Code**:
   ```bash
   git pull
   docker-compose down
   docker-compose build victor-api
   docker-compose up -d
   ```