#!/bin/bash
# Qdrant Vector Database Startup Script for WSL/Ubuntu
# Qdrant is needed for advanced agent memory and vector search

echo "🗃️ Starting Qdrant Vector Database..."

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Installing Docker..."
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    
    echo "✅ Docker installed. Please log out and back in, then run this script again."
    exit 1
fi

# Check if Qdrant container exists
if docker ps -a --format "table {{.Names}}" | grep -q "qdrant"; then
    echo "🔄 Qdrant container exists, starting..."
    docker start qdrant
else
    echo "📦 Creating new Qdrant container..."
    
    # Create data directory
    mkdir -p ./data/qdrant_storage
    
    # Run Qdrant container
    docker run -d \
        --name qdrant \
        -p 6333:6333 \
        -p 6334:6334 \
        -v $(pwd)/data/qdrant_storage:/qdrant/storage:z \
        qdrant/qdrant:latest
fi

# Wait for Qdrant to be ready
echo "⏳ Waiting for Qdrant to start..."
sleep 5

# Check if Qdrant is responding
if curl -s http://localhost:6333/health > /dev/null; then
    echo "✅ Qdrant is running successfully!"
    echo "🔗 Web UI: http://localhost:6333/dashboard"
    echo "🔗 API: http://localhost:6333"
    echo "📊 Collections endpoint: http://localhost:6333/collections"
else
    echo "❌ Qdrant failed to start. Check Docker logs:"
    docker logs qdrant
fi
