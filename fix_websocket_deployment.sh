#!/bin/bash

# Script to fix WebSocket timeout issues in HEMIS backend
echo "🔧 Fixing WebSocket timeout issues..."

# Stop the current backend container
echo "📦 Stopping current backend container..."
docker-compose -f docker-compose.yml stop hemis-backend

# Rebuild the backend container with new configuration
echo "🔨 Rebuilding backend container with eventlet support..."
docker-compose -f docker-compose.yml build hemis-backend

# Start the backend container
echo "🚀 Starting backend container..."
docker-compose -f docker-compose.yml up -d hemis-backend

# Wait for the container to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 10

# Check if the backend is healthy
echo "🏥 Checking backend health..."
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy and ready!"
else
    echo "❌ Backend health check failed. Check logs:"
    docker logs hemis-backend --tail=50
fi

# Show recent logs
echo "📋 Recent backend logs:"
docker logs hemis-backend --tail=20

echo "🎉 WebSocket fix deployment complete!"
echo "💡 The backend now uses eventlet workers which handle WebSocket connections much better."
echo "🔍 Monitor the logs with: docker logs hemis-backend -f"
