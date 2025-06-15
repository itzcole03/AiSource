#!/bin/bash
# launch_vllm_auto.sh
# Fully automates detection of model directories and Conda environment

# 0. Source conda before any usage
if [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/anaconda3/etc/profile.d/conda.sh"
elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
    source "$HOME/miniconda3/etc/profile.d/conda.sh"
else
    echo "Could not find conda.sh in ~/anaconda3 or ~/miniconda3. Please check your Conda installation."
    exit 1
fi

# 1. Auto-detect Conda environment containing vllm
CONDA_ENV=$(conda env list | awk '/vllm/ {print $1; exit}')
if [ -z "$CONDA_ENV" ]; then
    # Try to find any env with vllm installed
    for env in $(conda env list | awk 'NR>2 {print $1}'); do
        if conda run -n "$env" pip show vllm &>/dev/null; then
            CONDA_ENV="$env"; break
        fi
    done
fi
if [ -z "$CONDA_ENV" ]; then
    echo "No Conda environment with vllm found! Please install vllm in a Conda environment."
    exit 1
fi

# 2. Auto-discover model directories (deep search, common locations)
SEARCH_PATHS=(
    "$HOME/vllm_models"
    "$HOME/models"
    "$HOME/.cache/huggingface"
    "/mnt/c/Users/bcmad/.lmstudio/models"
    "/mnt/c/Users/bcmad/OneDrive/Desktop/vllm"
)

MODEL_DIRS=()
for path in "${SEARCH_PATHS[@]}"; do
    if [ -d "$path" ]; then
        # Find subdirs containing config.json or model files
        while IFS= read -r dir; do
            MODEL_DIRS+=("$dir")
        done < <(find "$path" -type f \( -iname "config.json" -o -iname "*gguf*" -o -iname "pytorch_model.bin" \) -exec dirname {} \; | sort -u)
    fi
done

if [ ${#MODEL_DIRS[@]} -eq 0 ]; then
    echo "No vLLM-compatible models found!"
    exit 1
fi

# --- Flag Parsing ---
if [[ "$1" == "--list-models" ]]; then
    # Only print models that are likely loadable by vLLM
    echo "Available vLLM-loadable models:"
    idx=1
    for mdir in "${MODEL_DIRS[@]}"; do
        msize=$(du -sh "$mdir" | cut -f1)
        if ls "$mdir"/*.gguf &>/dev/null; then
            mformat="GGUF"
            loadable=1
        elif [ -f "$mdir/pytorch_model.bin" ]; then
            mformat="PyTorch"
            loadable=1
        elif [ -f "$mdir/config.json" ]; then
            mformat="Transformers"
            loadable=1
        else
            mformat="Unknown"
            loadable=0
        fi
        if [ $loadable -eq 1 ]; then
            echo "[$idx] $(basename "$mdir") - $msize - $mformat"
            idx=$((idx+1))
        fi
    done
    exit 0
fi
if [[ "$1" == "--hw-info" ]]; then
    if command -v nvidia-smi &>/dev/null; then
        echo "Detected NVIDIA GPU(s):"
        nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv
        GPU_COUNT=$(nvidia-smi -L | wc -l)
        VRAM_TOTAL=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader | awk '{sum+=$1} END {print sum}')
    else
        echo "No NVIDIA GPU detected. Running in CPU mode."
        GPU_COUNT=0
        VRAM_TOTAL=0
    fi
    RAM_TOTAL=$(free -h | awk '/Mem:/ {print $2}')
    echo "System RAM: $RAM_TOTAL"
    exit 0
fi
if [[ "$1" == "--status" ]]; then
    if [ -f ~/vllm_server_status.txt ]; then
        statusline=$(cat ~/vllm_server_status.txt)
        if echo "$statusline" | grep -q RUNNING; then
            # Double-check process
            if ps aux | grep vllm.entrypoints.openai.api_server | grep -v grep > /dev/null; then
                echo "$statusline" | sed 's/^RUNNING:/Server running:/'
            else
                echo "Server not running"
            fi
        else
            echo "$statusline"
        fi
    else
        echo "Server not running"
    fi
    exit 0
fi

# --- Hardware Detection (default interactive mode) ---
if command -v nvidia-smi &>/dev/null; then
    echo "Detected NVIDIA GPU(s):"
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv
    GPU_COUNT=$(nvidia-smi -L | wc -l)
    VRAM_TOTAL=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader | awk '{sum+=$1} END {print sum}')
else
    echo "No NVIDIA GPU detected. Running in CPU mode."
    GPU_COUNT=0
    VRAM_TOTAL=0
fi
RAM_TOTAL=$(free -h | awk '/Mem:/ {print $2}')
echo "System RAM: $RAM_TOTAL"

# --- Model Listing with Size/Format (interactive mode) ---
echo "\nAvailable models:"
MODEL_INFO=()
for i in "${!MODEL_DIRS[@]}"; do
    mdir="${MODEL_DIRS[$i]}"
    msize=$(du -sh "$mdir" | cut -f1)
    # Try to detect format
    if ls "$mdir"/*.gguf &>/dev/null; then
        mformat="GGUF"
    elif ls "$mdir"/pytorch_model.bin &>/dev/null; then
        mformat="PyTorch"
    elif ls "$mdir"/config.json &>/dev/null; then
        mformat="Transformers"
    else
        mformat="Unknown"
    fi
    MODEL_INFO+=("[$((i+1))] $(basename "$mdir") - $msize - $mformat")
    echo "${MODEL_INFO[-1]}"
done

# --- Suggest Parameters ---
SUGGEST_PARALLEL=1
if [ "$GPU_COUNT" -gt 1 ]; then
    echo "\nYou have $GPU_COUNT GPUs. For large models, consider tensor parallelism."
    SUGGEST_PARALLEL=$GPU_COUNT
fi
if [ "$VRAM_TOTAL" -ne 0 ]; then
    echo "Total VRAM across all GPUs: ${VRAM_TOTAL} MiB"
fi

# --- Model Selection ---
echo
read -p "Enter model number to launch: " model_idx
model="${MODEL_DIRS[$((model_idx-1))]}"
echo "Selected: $model"

# --- Advanced Options ---
read -p "Number of GPUs to use [default: $SUGGEST_PARALLEL]: " NUM_GPUS
if [ -z "$NUM_GPUS" ]; then NUM_GPUS=$SUGGEST_PARALLEL; fi
read -p "Custom vLLM options (or leave blank): " CUSTOM_OPTS

# --- Memory Fit Warning ---
if [ "$VRAM_TOTAL" -ne 0 ]; then
    mdir_size=$(du -sm "$model" | cut -f1)
    if [ "$mdir_size" -gt "$VRAM_TOTAL" ]; then
        echo "WARNING: Model size ($mdir_size MiB) exceeds total VRAM ($VRAM_TOTAL MiB). vLLM may use CPU offloading or fail to load."
    fi
fi

# --- Launch vLLM ---
source ~/anaconda3/etc/profile.d/conda.sh
conda activate "$CONDA_ENV"
echo "Starting vLLM with model: $model (env: $CONDA_ENV) on $NUM_GPUS GPU(s)"
nohup python -m vllm.entrypoints.openai.api_server --model "$model" --tensor-parallel-size $NUM_GPUS $CUSTOM_OPTS > ~/vllm_server.log 2>&1 &
echo "vLLM server started. Log: ~/vllm_server.log"
# Write status file
ps -C python -o pid=,args= | grep vllm.entrypoints.openai.api_server | grep "$model" > /dev/null
if [ $? -eq 0 ]; then
    echo "RUNNING: $model ($(date))" > ~/vllm_server_status.txt
else
    echo "FAILED TO START: $model ($(date))" > ~/vllm_server_status.txt
fi
