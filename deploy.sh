#!/bin/bash

# Victor Deployment Script
# This script helps deploy the Victor services on a Mac Mini

# Set script to exit on error
set -e

echo "========================================"
echo "   Victor Deployment Script"
echo "========================================"
echo ""

# Check if the .env file exists, create from example if not
if [ ! -f .env ]; then
  echo "Creating .env file from .env.example..."
  cp .env.example .env
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
if ! command -v docker-compose &> /dev/null; then
  echo "Docker Compose is not installed. Please install Docker Compose first."
  exit 1
fi

echo "Pulling latest code from GitHub..."
git pull origin main

echo "Copying .env file to src/docker directory..."
cp .env src/docker/.env

echo "Building Victor API service..."
cd src/docker
docker-compose build victor-api

echo "Starting Victor services..."
docker-compose up -d

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
docker-compose ps

echo ""
echo "For logs, use: docker-compose logs -f"
echo "To stop services: docker-compose down"
echo ""
echo "Deployment complete!"