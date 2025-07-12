#!/bin/bash
# Build and run the Docker container for ClipsAI Web GUI

echo "🐳 Building ClipsAI Web GUI Docker container..."

# Stop existing container if running
docker stop clipsai-webgui 2>/dev/null
docker rm clipsai-webgui 2>/dev/null

# Build the image
docker build -t clipsai/webgui:latest -f Dockerfile .

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo ""
    echo "🚀 Starting container on port 5555..."
    
    # Run the container
    docker run -d \
        --name clipsai-webgui \
        -p 5555:5555 \
        -e PUID=99 \
        -e PGID=100 \
        -e PORT=5555 \
        -v $(pwd)/config:/config \
        -v $(pwd)/data:/data \
        -v $(pwd)/uploads:/app/uploads \
        -v $(pwd)/logs:/app/logs \
        clipsai/webgui:latest
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Container started successfully!"
        echo ""
        echo "🌐 Access the web interface at: http://localhost:5555"
        echo ""
        echo "📊 Check container status:"
        echo "   docker ps | grep clipsai-webgui"
        echo ""
        echo "📝 View logs:"
        echo "   docker logs clipsai-webgui"
        echo ""
        echo "🛑 Stop container:"
        echo "   docker stop clipsai-webgui"
    else
        echo "❌ Failed to start container"
        exit 1
    fi
else
    echo "❌ Build failed"
    exit 1
fi