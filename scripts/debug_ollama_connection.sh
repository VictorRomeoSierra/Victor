#!/bin/bash

# Debug script for Ollama connectivity issues

echo "=== Debugging Ollama Connection ==="
echo

# First check if Ollama is running on the host
echo "1. Checking Ollama on host machine..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Ollama is running on host (localhost:11434)"
    curl -s http://localhost:11434/api/tags | jq '.models[].name' 2>/dev/null | head -5
else
    echo "✗ Ollama is NOT accessible on host"
    echo "  Make sure Ollama is running: ollama serve"
fi

echo
echo "2. Checking Docker network setup..."
cd "$(dirname "$0")/../src/docker"

# Get container name
CONTAINER_NAME=$(docker-compose -f docker-compose.simple.yml ps -q victor-api)
if [ -z "$CONTAINER_NAME" ]; then
    echo "✗ Victor API container is not running"
    exit 1
fi

echo "Container ID: $CONTAINER_NAME"

# Check host.docker.internal resolution
echo
echo "3. Testing host.docker.internal resolution in container..."
docker exec $CONTAINER_NAME nslookup host.docker.internal 2>/dev/null || \
docker exec $CONTAINER_NAME getent hosts host.docker.internal || \
docker exec $CONTAINER_NAME cat /etc/hosts | grep host.docker.internal

# Test different connection methods
echo
echo "4. Testing Ollama connectivity from container..."

# Test 1: Using host.docker.internal
echo -n "   host.docker.internal:11434... "
docker exec $CONTAINER_NAME curl -s -m 5 http://host.docker.internal:11434/api/tags > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Success"
else
    echo "✗ Failed"
fi

# Test 2: Using host IP directly
echo -n "   Getting host IP... "
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    HOST_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
else
    # Linux
    HOST_IP=$(hostname -I | awk '{print $1}')
fi
echo "$HOST_IP"

echo -n "   Direct IP $HOST_IP:11434... "
docker exec $CONTAINER_NAME curl -s -m 5 http://$HOST_IP:11434/api/tags > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Success"
else
    echo "✗ Failed"
fi

# Test 3: Check if it's a firewall issue
echo
echo "5. Checking Ollama binding..."
OLLAMA_PROCESS=$(ps aux | grep -i ollama | grep -v grep)
if [ ! -z "$OLLAMA_PROCESS" ]; then
    echo "Ollama process found:"
    echo "$OLLAMA_PROCESS" | head -1
    
    # Check what address Ollama is bound to
    LISTEN_ADDR=$(netstat -an | grep 11434 | grep LISTEN || lsof -i :11434 2>/dev/null | grep LISTEN)
    if [ ! -z "$LISTEN_ADDR" ]; then
        echo
        echo "Ollama listening on:"
        echo "$LISTEN_ADDR"
        
        if echo "$LISTEN_ADDR" | grep -q "127.0.0.1"; then
            echo
            echo "⚠️  WARNING: Ollama is only listening on localhost (127.0.0.1)"
            echo "   Docker containers cannot access services bound only to localhost"
            echo
            echo "   To fix this, start Ollama with:"
            echo "   OLLAMA_HOST=0.0.0.0:11434 ollama serve"
        fi
    fi
else
    echo "✗ Ollama process not found"
fi

echo
echo "6. Testing from Victor API Python environment..."
docker exec $CONTAINER_NAME python -c "
import requests
import os

ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://host.docker.internal:11434')
print(f'OLLAMA_BASE_URL: {ollama_url}')

try:
    response = requests.get(f'{ollama_url}/api/tags', timeout=5)
    print(f'✓ Connection successful: {response.status_code}')
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f'  Found {len(models)} models')
except Exception as e:
    print(f'✗ Connection failed: {e}')
"

echo
echo "=== Recommendations ==="
echo "If Ollama is only bound to localhost, restart it with:"
echo "  OLLAMA_HOST=0.0.0.0:11434 ollama serve"
echo
echo "Or use the host IP address in your configuration:"
echo "  OLLAMA_BASE_URL=http://$HOST_IP:11434"