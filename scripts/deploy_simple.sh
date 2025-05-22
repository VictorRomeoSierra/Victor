#!/bin/bash

# Quick deployment using simplified Docker setup (no ML packages)

echo "=== Deploying Victor API (Simplified) ==="
echo "This version uses Ollama for embeddings and doesn't require PyTorch"
echo

PROJECT_ROOT="$(dirname "$0")/.."
cd "$PROJECT_ROOT"

# Copy necessary files to docker directory
echo "Preparing build context..."
cp "$PROJECT_ROOT/src/requirements.txt" "$PROJECT_ROOT/src/docker/requirements.txt"
[ -f "$PROJECT_ROOT/.env" ] && cp "$PROJECT_ROOT/.env" "$PROJECT_ROOT/src/docker/.env"

cd "$PROJECT_ROOT/src/docker"

# Stop existing services
echo "Stopping existing services..."
docker-compose -f docker-compose.simple.yml down

# Build and start
echo "Building and starting services..."
docker-compose -f docker-compose.simple.yml build victor-api
docker-compose -f docker-compose.simple.yml up -d

# Wait for startup
echo "Waiting for services to start..."
sleep 5

# Check health
echo "Checking service health..."
curl -s http://localhost:8000/health | python3 -m json.tool || echo "Health check failed"

echo
echo "Services status:"
docker-compose -f docker-compose.simple.yml ps

echo
echo "To view logs: docker-compose -f docker-compose.simple.yml logs -f victor-api"
echo "To stop: docker-compose -f docker-compose.simple.yml down"