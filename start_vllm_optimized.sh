#!/bin/bash
# Optimized vLLM CPU Server for Ultimate Copilot Agents
# Designed for 8GB RAM constraint with fast, lightweight models

echo "🧠 Starting Optimized vLLM CPU Server for AI Agents..."

# CPU optimization environment variables
export CUDA_VISIBLE_DEVICES=""
export VLLM_USE_MODELSCOPE=false
export VLLM_WORKER_MULTIPROC_METHOD=spawn
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

# Select model based on parameter or use default
case "${1:-small}" in
    "small"|"fast")
        MODEL_NAME="distilgpt2"
        MAX_LEN=1024
        BATCH_SIZE=4
        echo "⚡ Using DistilGPT2 (fastest, 82M params)"
        ;;
    "medium"|"balanced")
        MODEL_NAME="gpt2"
        MAX_LEN=1536
        BATCH_SIZE=3
        echo "⚖️ Using GPT2 (balanced, 124M params)"
        ;;
    "large"|"quality")
        MODEL_NAME="gpt2-medium"
        MAX_LEN=2048
        BATCH_SIZE=2
        echo "🎯 Using GPT2-Medium (quality, 355M params)"
        ;;
    "code"|"programming")
        MODEL_NAME="microsoft/CodeGPT-small-py"
        MAX_LEN=1024
        BATCH_SIZE=3
        echo "💻 Using CodeGPT-Small-Py (code-focused, 117M params)"
        ;;
    *)
        MODEL_NAME="$1"
        MAX_LEN=1024
        BATCH_SIZE=4
        echo "🔧 Using custom model: $MODEL_NAME"
        ;;
esac

echo "📊 Configuration:"
echo "   Model: $MODEL_NAME"
echo "   Max Length: $MAX_LEN tokens"
echo "   Batch Size: $BATCH_SIZE"
echo "   CPU Threads: 4"
echo "   Memory: Optimized for 8GB RAM"
echo ""

# Check if running in correct environment
if ! command -v python &> /dev/null; then
    echo "❌ Python not found! Make sure your venv is activated:"
    echo "   source /path/to/your/venv/bin/activate"
    exit 1
fi

# Check if vLLM is installed
if ! python -c "import vllm" &> /dev/null; then
    echo "❌ vLLM not found! Install with:"
    echo "   pip install vllm"
    exit 1
fi

echo "🚀 Starting vLLM CPU server..."
echo "🌐 API will be available at: http://localhost:8000"
echo "📚 Models endpoint: http://localhost:8000/v1/models"
echo "💬 Chat endpoint: http://localhost:8000/v1/chat/completions"
echo ""

# Start vLLM with CPU-optimized settings
python -m vllm.entrypoints.openai.api_server \
    --model "$MODEL_NAME" \
    --host 0.0.0.0 \
    --port 8000 \
    --device cpu \
    --dtype float32 \
    --max-model-len $MAX_LEN \
    --max-num-batched-tokens $((MAX_LEN * BATCH_SIZE)) \
    --max-num-seqs $BATCH_SIZE \
    --max-logprobs 5 \
    --disable-log-stats \
    --tensor-parallel-size 1 \
    --pipeline-parallel-size 1 \
    --trust-remote-code \
    --disable-custom-all-reduce

echo ""
echo "✅ vLLM CPU server started successfully!"
echo "🔧 Optimized for Ultimate Copilot intelligent agents"
echo "🛑 Press Ctrl+C to stop"
