#!/bin/bash

# Victor API Update Script
# This script updates the Victor API with the new integrated RAG functionality

set -e

echo "========================================"
echo "   Victor API Update Script"
echo "========================================"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

# Check if we're on the Mac Mini or local development
read -p "Are you running this on the Mac Mini (skyeye-server)? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running deployment for Mac Mini..."
    IS_MAC_MINI=true
else
    echo "Running in development mode..."
    IS_MAC_MINI=false
fi

# Step 1: Create/update .env file
echo ""
echo "Step 1: Checking environment configuration..."
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "Creating .env file from .env.example..."
    cp "$PROJECT_ROOT/.env.example" "$PROJECT_ROOT/.env"
    echo "⚠️  Please edit .env file with your configuration before continuing!"
    read -p "Press enter when .env is configured..."
else
    echo "✓ .env file exists"
fi

# Step 2: Apply database migration
echo ""
echo "Step 2: Database migration..."
echo "The following SQL needs to be run on your PostgreSQL database:"
echo "----------------------------------------"
cat "$PROJECT_ROOT/src/database/init/02-lua-chunks.sql"
echo "----------------------------------------"
read -p "Have you applied this migration to the database? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please apply the migration first. You can run:"
    echo "psql -h skyeye-server -p 5433 -U postgres -d vectordb < $PROJECT_ROOT/src/database/init/02-lua-chunks.sql"
    exit 1
fi

# Step 3: Build and deploy
echo ""
echo "Step 3: Building and deploying Victor API..."

# Copy files for Docker build
cp "$PROJECT_ROOT/.env" "$PROJECT_ROOT/src/docker/.env"
cp "$PROJECT_ROOT/src/requirements.txt" "$PROJECT_ROOT/src/docker/requirements.txt"

# Determine Docker Compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

cd "$PROJECT_ROOT/src/docker"

# Stop existing Victor API
echo "Stopping existing Victor API..."
$DOCKER_COMPOSE stop victor-api

# Build new image
echo "Building new Victor API image..."
$DOCKER_COMPOSE build victor-api

# Start updated service
echo "Starting updated Victor API..."
$DOCKER_COMPOSE up -d victor-api

# Wait for service to start
echo "Waiting for service to start..."
sleep 5

# Step 4: Verify deployment
echo ""
echo "Step 4: Verifying deployment..."

if [ "$IS_MAC_MINI" = true ]; then
    API_URL="http://skyeye-server:8000"
else
    API_URL="http://localhost:8000"
fi

# Check health endpoint
if curl -s "$API_URL/health" | grep -q "healthy"; then
    echo "✓ Victor API is healthy"
else
    echo "⚠️  Victor API health check failed"
fi

# Check stats endpoint
echo ""
echo "Checking database statistics..."
curl -s "$API_URL/stats" | python3 -m json.tool || echo "Stats endpoint not responding"

# Step 5: Test search functionality
echo ""
echo "Step 5: Testing search functionality..."
echo "Running test search for 'waypoint'..."
curl -s -X POST "$API_URL/search" \
    -H "Content-Type: application/json" \
    -d '{"query": "waypoint", "limit": 2, "search_type": "text"}' | python3 -m json.tool || echo "Search test failed"

echo ""
echo "========================================"
echo "Deployment Summary:"
echo "- Victor API updated with integrated RAG"
echo "- Database migration applied"
echo "- Service running at: $API_URL"
echo ""
echo "Next steps:"
echo "1. Test N8N workflow with: https://n8n.victorromeosierra.com/webhook-test/victor-chat"
echo "2. Monitor logs: $DOCKER_COMPOSE logs -f victor-api"
echo "3. If needed, reindex XSAF code using the original lua_embedder.py"
echo "========================================"