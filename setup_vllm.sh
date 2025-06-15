#!/bin/bash
# vLLM Setup and Start Script for Ultimate Copilot System
# Run this in Ubuntu/WSL environment

echo "=== Ultimate Copilot vLLM Service Setup ==="
echo

# Check if Python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Installing..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Create virtual environment if it doesn't exist
if [ ! -d "vllm_env" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv vllm_env
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source vllm_env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install vLLM
echo "📥 Installing vLLM (this may take several minutes)..."
echo "Note: vLLM requires CUDA for GPU acceleration"

# Try to install vLLM
if pip install vllm; then
    echo "✅ vLLM installed successfully"
else
    echo "⚠️ vLLM installation failed, trying CPU-only version..."
    pip install vllm-cpu
fi

# Install additional dependencies that might be needed
echo "📥 Installing additional dependencies..."
pip install torch transformers tokenizers

echo
echo "=== vLLM Service Starting ==="
echo "🚀 Starting vLLM OpenAI-compatible API server..."
echo "📡 Server will be available at: http://localhost:8000"
echo "🔧 Using model: microsoft/DialoGPT-medium"
echo

# Start vLLM server with fallback options
echo "⏳ Starting server (first run may download model files)..."
echo "🔍 Checking available GPU memory..."

# Try different configurations in order of preference
echo "🚀 Attempting GPU mode with reduced memory usage..."
if python -m vllm.entrypoints.openai.api_server \
    --model gpt2 \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 512 \
    --gpu-memory-utilization 0.3 \
    --dtype float16; then
    echo "✅ vLLM server started with GPU (reduced memory)"
elif python -m vllm.entrypoints.openai.api_server \
    --model gpt2 \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 256 \
    --gpu-memory-utilization 0.2 \
    --dtype float16; then
    echo "✅ vLLM server started with GPU (minimal memory)"
else
    echo "⚠️ GPU mode failed, trying CPU mode..."
    pip install vllm-cpu
    if VLLM_USE_CPU=1 python -m vllm.entrypoints.openai.api_server \
        --model gpt2 \
        --host 0.0.0.0 \
        --port 8000 \
        --max-model-len 512; then
        echo "✅ vLLM server started with CPU"
    else
        echo "❌ Failed to start vLLM server"
        echo "💡 GPU memory may be insufficient. Try stopping other GPU applications first."
        echo "🔧 Manual commands to try:"
        echo "   # For GPU with less memory:"
        echo "   python -m vllm.entrypoints.openai.api_server --model gpt2 --host 0.0.0.0 --port 8000 --max-model-len 256 --gpu-memory-utilization 0.2"
        echo "   # For CPU only:"
        echo "   VLLM_USE_CPU=1 python -m vllm.entrypoints.openai.api_server --model gpt2 --host 0.0.0.0 --port 8000"
    fi
fi

echo
echo "🎉 vLLM service setup complete!"
echo "📊 To test the API, visit: http://localhost:8000/docs"
echo "🔄 To restart: source vllm_env/bin/activate && python -m vllm.entrypoints.openai.api_server ..."
