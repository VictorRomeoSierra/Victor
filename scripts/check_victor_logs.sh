#!/bin/bash

# Quick script to check Victor API status and logs

echo "Checking Docker containers..."
cd "$(dirname "$0")/../src/docker"

# Check if container is running
docker-compose ps

echo -e "\n\nChecking Victor API logs (last 50 lines)..."
docker-compose logs --tail=50 victor-api

echo -e "\n\nChecking container health..."
docker inspect victor-api | grep -A 5 "State"

echo -e "\n\nTrying direct curl to container..."
# Get container IP
CONTAINER_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(docker-compose ps -q victor-api))
echo "Container IP: $CONTAINER_IP"

if [ ! -z "$CONTAINER_IP" ]; then
    echo "Testing health endpoint directly..."
    curl -s "http://$CONTAINER_IP:8000/health" || echo "Failed to reach container directly"
fi

echo -e "\n\nChecking for import errors..."
docker-compose logs victor-api | grep -i "error\|exception\|traceback" | tail -20

echo -e "\n\nTo see full logs, run:"
echo "cd src/docker && docker-compose logs -f victor-api"