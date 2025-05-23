#!/bin/bash
# Restart Victor API container

cd /home/flamernz/Dev/Victor/src/docker

echo "Stopping Victor API..."
docker-compose -f docker-compose.simple.yml stop victor-api

echo "Starting Victor API with correct environment..."
docker-compose -f docker-compose.simple.yml up -d victor-api

echo "Waiting for Victor API to start..."
sleep 10

echo "Testing Victor API..."
curl -s http://localhost:8000/health | jq .

echo "Testing embedding functionality..."
curl -s -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "waypoint", "limit": 2, "search_type": "vector"}' | jq .

echo "Done!"