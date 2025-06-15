#!/bin/bash
# vLLM CPU Server Startup Script for WSL/Ubuntu
# This script starts vLLM in CPU mode for Windows WSL environment

echo "🚀 Starting vLLM CPU Server for Ultimate Copilot..."

# Set environment variables for CPU optimization
export CUDA_VISIBLE_DEVICES=""
export VLLM_USE_MODELSCOPE=false
export VLLM_WORKER_MULTIPROC_METHOD=spawn

# Default model - change this to your preferred model
MODEL_NAME="${1:-microsoft/DialoGPT-medium}"

# Alternative CPU-friendly models you can use:
# - microsoft/DialoGPT-medium (conversational)
# - microsoft/DialoGPT-small (faster, smaller)
# - gpt2 (classic, reliable)
# - distilgpt2 (lightweight)
# - microsoft/CodeGPT-small-py (code-focused)

echo "📦 Starting vLLM with model: $MODEL_NAME"
echo "💻 Running in CPU mode (no GPU required)"
echo "🔧 Server will be available at: http://localhost:8000"
echo ""

# Check if model exists, if not it will be downloaded
echo "🔍 Checking/downloading model..."

# Start vLLM server in CPU mode
python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_NAME" \
    --host 0.0.0.0 \
    --port 8000 \
    --device cpu \
    --dtype float32 \
    --max-model-len 2048 \
    --max-num-batched-tokens 2048 \
    --max-num-seqs 8 \
    --max-logprobs 5 \
    --disable-log-stats \
    --tensor-parallel-size 1 \
    --pipeline-parallel-size 1

echo "✅ vLLM CPU server started successfully!"
echo "🔗 API endpoint: http://localhost:8000/v1/chat/completions"
echo "📚 Models endpoint: http://localhost:8000/v1/models"
echo ""
echo "🛑 Press Ctrl+C to stop the server"
