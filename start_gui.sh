#!/bin/bash

echo "🚀 Starting ClipsAI Web GUI..."
echo "=================================="

# Check if Docker is available
if command -v docker &> /dev/null; then
    echo "🐳 Docker found - starting with Docker..."
    
    # Build and run with Docker Compose
    if command -v docker-compose &> /dev/null; then
        echo "📦 Using Docker Compose..."
        docker-compose up --build
    else
        echo "📦 Using Docker..."
        docker build -t clipsai-web .
        docker run -p 8501:8501 -v $(pwd)/temp:/app/temp clipsai-web
    fi
    
elif command -v python3 &> /dev/null; then
    echo "🐍 Python 3 found - installing dependencies..."
    
    # Install pip if not available
    if ! command -v pip3 &> /dev/null; then
        echo "Installing pip..."
        python3 -m ensurepip --default-pip
    fi
    
    # Install Streamlit if not available
    if ! python3 -c "import streamlit" &> /dev/null; then
        echo "Installing Streamlit..."
        pip3 install streamlit
    fi
    
    # Install other basic dependencies
    pip3 install pandas numpy
    
    echo "🎬 Starting Streamlit app..."
    python3 -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0
    
else
    echo "❌ Neither Docker nor Python 3 found!"
    echo "Please install one of the following:"
    echo "1. Docker: https://docs.docker.com/get-docker/"
    echo "2. Python 3: https://www.python.org/downloads/"
    exit 1
fi

echo ""
echo "🎉 ClipsAI Web GUI should now be running!"
echo "Open your browser and go to: http://localhost:8501"
echo ""
echo "📝 Note: You'll need a Hugging Face token for full functionality"
echo "Get one at: https://huggingface.co/settings/tokens"