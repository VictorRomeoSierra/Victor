#!/bin/bash

# Quick test script to verify Victor API deployment

echo "=== Testing Victor API Deployment ==="
echo

API_URL="${1:-http://localhost:8000}"
echo "Testing API at: $API_URL"
echo

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$API_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    http_code=$(echo "$response" | tail -n 1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        echo -e "${GREEN}✓${NC} (HTTP $http_code)"
        if [ ! -z "$body" ]; then
            echo "  Response: $(echo "$body" | head -n 1)..."
        fi
    else
        echo -e "${RED}✗${NC} (HTTP $http_code)"
        echo "  Error: $body"
    fi
    echo
}

# Run tests
test_endpoint "Health Check" "GET" "/health"
test_endpoint "Stats" "GET" "/stats"
test_endpoint "Text Search" "POST" "/search" '{"query":"waypoint","limit":2,"search_type":"text"}'
test_endpoint "Context Generation" "POST" "/context" '{"query":"How to create waypoints?","limit":2,"detailed":false}'
test_endpoint "Prompt Enhancement" "POST" "/enhance_prompt" '{"prompt":"How do I spawn units in DCS?","model":"codellama"}'

# Check if Ollama is accessible from container
echo "Checking Ollama connectivity..."
# Find the actual container name (might be prefixed with directory name)
CONTAINER_ID=$(docker ps -q -f name=victor-api | head -1)
if [ ! -z "$CONTAINER_ID" ]; then
    docker exec $CONTAINER_ID curl -s http://host.docker.internal:11434/api/tags > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} Ollama is accessible from container"
    else
        echo -e "${RED}✗${NC} Cannot reach Ollama from container"
        echo "  Run ./scripts/debug_ollama_connection.sh for details"
    fi
else
    echo -e "${RED}✗${NC} Victor API container not found"
fi

echo
echo "=== Test Summary ==="
echo "If all tests passed, Victor API is working correctly!"
echo "For detailed logs: cd src/docker && docker-compose -f docker-compose.simple.yml logs victor-api"