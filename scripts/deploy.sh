#!/bin/bash

# Victor Deployment Script
# This script helps deploy the Victor services on a Mac Mini

# Set script to exit on error
set -e

echo "========================================"
echo "   Victor Deployment Script"
echo "========================================"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

# Check if the .env file exists, create from example if not
if [ ! -f "$PROJECT_ROOT/.env" ]; then
  echo "Creating .env file from config/.env.example..."
  cp "$PROJECT_ROOT/config/.env.example" "$PROJECT_ROOT/.env"
  echo "Please review and edit the .env file before continuing."
  echo "Then run this script again."
  exit 0
fi

echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
  echo "Docker is not installed. Please install Docker first."
  exit 1
fi

echo "Checking Docker Compose..."
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
  echo "Docker Compose is not installed. Please install Docker Compose first."
  exit 1
fi

# Determine Docker Compose command
if command -v docker-compose &> /dev/null; then
  DOCKER_COMPOSE="docker-compose"
else
  DOCKER_COMPOSE="docker compose"
fi

echo "Pulling latest code from GitHub..."
git pull origin main

echo "Preparing build environment..."
cp "$PROJECT_ROOT/.env" "$PROJECT_ROOT/src/docker/.env"
cp "$PROJECT_ROOT/src/requirements.txt" "$PROJECT_ROOT/src/docker/requirements.txt"

echo "Building Victor API service..."
cd "$PROJECT_ROOT/src/docker"
$DOCKER_COMPOSE build victor-api

echo "Starting Victor services..."
$DOCKER_COMPOSE up -d

echo "========================================"
echo "Services should now be running:"
echo "- Victor API: http://localhost:8000"
echo "- n8n: http://localhost:5678"
echo ""
echo "Don't forget to update your Nginx configuration to route:"
echo "- /n8n/ path to http://localhost:5678"
echo ""
echo "Note for MacOS: If you encounter host.docker.internal resolution issues,"
echo "you can add it to your /etc/hosts file with your local IP:"
echo "  127.0.0.1 host.docker.internal"
echo "========================================"

# Check if services are running
echo "Checking service status..."
$DOCKER_COMPOSE ps

echo ""
echo "For logs, use: $DOCKER_COMPOSE logs -f"
echo "To stop services: $DOCKER_COMPOSE down"
echo ""
echo "Deployment complete!"