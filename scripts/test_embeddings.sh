#!/bin/bash

# Wrapper script to run test_embeddings.py inside the victor-api container

echo "Running embedding tests inside Victor API container..."
echo

cd "$(dirname "$0")/.."

# Find the victor-api container
CONTAINER_ID=$(docker ps -q -f name=victor-api | head -1)

if [ -z "$CONTAINER_ID" ]; then
    echo "Error: Victor API container is not running"
    echo "Please start it with: ./scripts/deploy_simple.sh"
    exit 1
fi

# Copy the test script into the container
docker cp scripts/test_embeddings.py $CONTAINER_ID:/tmp/test_embeddings.py

# Run the test script inside the container
# Note: Inside the container, the API is accessible at localhost:8000
docker exec $CONTAINER_ID python /tmp/test_embeddings.py http://localhost:8000

# Clean up
docker exec $CONTAINER_ID rm /tmp/test_embeddings.py