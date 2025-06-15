# vLLM Setup Guide for Ultimate Copilot System

## Quick Setup (Ubuntu/WSL)

### Option 1: Run the automated setup script
```bash
# In Ubuntu terminal, navigate to the project directory
cd /mnt/c/Users/YOUR_USERNAME/Downloads/project-bolt-withastro-astro-tczzygud/project/project/ultimate_copilot

# Make the script executable and run it
chmod +x setup_vllm.sh
./setup_vllm.sh
```

### Option 2: Manual setup
```bash
# 1. Create virtual environment
python3 -m venv vllm_env

# 2. Activate virtual environment
source vllm_env/bin/activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install vLLM
pip install vllm

# 5. Start the server
python -m vllm.entrypoints.openai.api_server \
    --model microsoft/DialoGPT-medium \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 2048
```

## Alternative Models (if DialoGPT-medium fails)

### For systems with limited VRAM:
```bash
# Use GPT-2 (smaller model)
python -m vllm.entrypoints.openai.api_server \
    --model gpt2 \
    --host 0.0.0.0 \
    --port 8000 \
    --max-model-len 1024
```

### For systems with more VRAM:
```bash
# Use larger models like Llama-2-7B
python -m vllm.entrypoints.openai.api_server \
    --model meta-llama/Llama-2-7b-hf \
    --host 0.0.0.0 \
    --port 8000
```

## Testing the vLLM Service

Once running, test the API:
```bash
# Test endpoint
curl http://localhost:8000/v1/models

# Or visit in browser:
# http://localhost:8000/docs
```

## Integration with Ultimate Copilot

After vLLM is running:
1. The Ultimate Copilot System will automatically detect it
2. vLLM will appear as an available provider in the dashboard
3. Models will be load-balanced across Ollama, LM Studio, and vLLM

## Troubleshooting

### CUDA Issues:
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# If CUDA not available, use CPU version
pip install vllm-cpu
```

### Memory Issues:
- Reduce `--max-model-len` parameter
- Use smaller models like `gpt2`
- Close other GPU-intensive applications

### Port Conflicts:
- Change port: `--port 8001`
- Check if port 8000 is in use: `netstat -an | grep 8000`
