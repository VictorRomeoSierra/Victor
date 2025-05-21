#!/bin/bash

# Run Victor containers using the docker-compose file in src/docker directory

# Set script to exit on error
set -e

# Navigate to the docker directory from scripts
cd "$(dirname "$0")/../src/docker"

# Determine Docker Compose command
if command -v docker-compose &> /dev/null; then
  DOCKER_COMPOSE="docker-compose"
else
  DOCKER_COMPOSE="docker compose"
fi

# Function to display usage information
function show_usage {
    echo "Usage: ./run.sh [command]"
    echo ""
    echo "Commands:"
    echo "  up        - Start the Victor API and n8n services"
    echo "  down      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  logs      - View logs from all services"
    echo "  api       - Start only the Victor API service"
    echo "  n8n       - Start only the n8n service"
    echo "  status    - Check the status of all services"
    echo "  build     - Rebuild the Victor API service"
    echo "  help      - Show this help message"
}

# Parse command line arguments
case "$1" in
    up)
        echo "Starting Victor services..."
        $DOCKER_COMPOSE up -d
        ;;
    down)
        echo "Stopping Victor services..."
        $DOCKER_COMPOSE down
        ;;
    restart)
        echo "Restarting Victor services..."
        $DOCKER_COMPOSE restart
        ;;
    logs)
        echo "Showing logs for Victor services..."
        $DOCKER_COMPOSE logs -f
        ;;
    api)
        echo "Starting Victor API service..."
        $DOCKER_COMPOSE up -d victor-api
        ;;
    n8n)
        echo "Starting n8n service..."
        $DOCKER_COMPOSE up -d n8n
        ;;
    status)
        echo "Status of Victor services:"
        $DOCKER_COMPOSE ps
        ;;
    build)
        echo "Rebuilding Victor API service..."
        $DOCKER_COMPOSE build victor-api
        ;;
    help|*)
        show_usage
        ;;
esac