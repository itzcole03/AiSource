#!/bin/bash

# --- Robust Conda Sourcing Function ---
source_conda() {
    if [ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/anaconda3/etc/profile.d/conda.sh"
    elif [ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]; then
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
    else
        echo "ERROR: Could not find conda.sh in anaconda3 or miniconda3."
        exit 1
    fi
}

# --- Robust config/env resolution for NUM_GPUS and CUSTOM_OPTS ---
# Priority: environment variable > ~/.vllm_launcher_config > default
if [ -z "$NUM_GPUS" ] || [ -z "$CUSTOM_OPTS" ]; then
    if [ -f "$HOME/.vllm_launcher_config" ]; then
        source "$HOME/.vllm_launcher_config"
    fi
fi
if [ -z "$NUM_GPUS" ]; then NUM_GPUS=1; fi
if [ -z "$CUSTOM_OPTS" ]; then CUSTOM_OPTS=""; fi

# --- Parse --model argument (name or path) ---
MODEL_ARG=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --model)
            MODEL_ARG="$2"
            shift 2
            ;;
        --num-gpus)
            NUM_GPUS="$2"
            shift 2
            ;;
        --custom-opts)
            CUSTOM_OPTS="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# --- Resolve model path if name provided ---
SELECTED_MODEL=""
if [ -n "$MODEL_ARG" ]; then
    # Try to match by name in MODEL_DIRS
    for mdir in "${MODEL_DIRS[@]}"; do
        if [[ "$MODEL_ARG" == "$(basename "$mdir")" ]] || [[ "$MODEL_ARG" == "$mdir" ]]; then
            SELECTED_MODEL="$mdir"
            break
        fi
    done
    # If not found, treat as absolute path if it exists
    if [ -z "$SELECTED_MODEL" ] && [ -d "$MODEL_ARG" ]; then
        SELECTED_MODEL="$MODEL_ARG"
    fi
fi

# --- Auto-discover model directories (deep search, common locations) ---
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
    source_conda
    echo "Available vLLM-loadable models:"
    idx=1
    declare -A seen
    for mdir in "${MODEL_DIRS[@]}"; do
        bname=$(basename "$mdir")
        if [[ -n "${seen[$bname]}" ]]; then
            continue
        fi
        seen[$bname]=1
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
        if [ $loadable -eq 1 ] && [ $(du -s "$mdir" | awk '{print $1}') -gt 5000 ]; then
            echo "[$idx] $bname - $msize - $mformat"
            idx=$((idx+1))
        fi
    done
    exit 0
fi
if [[ "$1" == "--hw-info" ]]; then
    source_conda
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
    source_conda
    if [ -f ~/vllm_server_status.txt ]; then
        statusline=$(cat ~/vllm_server_status.txt)
        if echo "$statusline" | grep -q RUNNING; then
            if ps aux | grep vllm.entrypoints.openai.api_server | grep -v grep > /dev/null; then
                model=$(echo "$statusline" | sed -n 's/^RUNNING: \(.*\) (port .*/\1/p')
                port=$(echo "$statusline" | sed -n 's/.*(port \([0-9]*\)).*/\1/p')
                launched=$(echo "$statusline" | sed -n 's/.*(launched \([0-9]*\)).*/\1/p')
                now=$(date +%s)
                let uptime_sec=now-launched
                if [ $uptime_sec -lt 60 ]; then
                    uptime="${uptime_sec}s"
                elif [ $uptime_sec -lt 3600 ]; then
                    let min=uptime_sec/60
                    let sec=uptime_sec%60
                    uptime="${min}m ${sec}s"
                else
                    let hr=uptime_sec/3600
                    let min=(uptime_sec%3600)/60
                    let sec=uptime_sec%60
                    uptime="${hr}h ${min}m ${sec}s"
                fi
                echo "Server running: $model | port: $port | uptime: $uptime"
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
source_conda
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

# --- Non-interactive launch block ---
if [[ -n "$SELECTED_MODEL" ]]; then
    echo "[INFO] Launching vLLM with model: $SELECTED_MODEL, NUM_GPUS: $NUM_GPUS, CUSTOM_OPTS: $CUSTOM_OPTS"
    source_conda
    conda activate vllm
    python -m vllm.entrypoints.openai.api_server --model "$SELECTED_MODEL" --num-gpus "$NUM_GPUS" $CUSTOM_OPTS
    exit $?
fi

# --- Interactive mode (only if not called with --model) ---
echo "\nAvailable models:"
declare -A seen
MODEL_INFO=()
FILTERED_MODEL_DIRS=()
idx=1
for mdir in "${MODEL_DIRS[@]}"; do
    bname=$(basename "$mdir")
    if [[ -n "${seen[$bname]}" ]]; then
        continue
    fi
    seen[$bname]=1
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
    if [ $loadable -eq 1 ] && [ $(du -s "$mdir" | awk '{print $1}') -gt 5000 ]; then
        MODEL_INFO+=("[$idx] $bname - $msize - $mformat")
        FILTERED_MODEL_DIRS+=("$mdir")
        echo "${MODEL_INFO[-1]}"
        idx=$((idx+1))
    fi

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
selected_model=""
if [[ $model_idx =~ ^[0-9]+$ ]] && [ "$model_idx" -ge 1 ] && [ "$model_idx" -le "${#FILTERED_MODEL_DIRS[@]}" ]; then
    selected_model="${FILTERED_MODEL_DIRS[$((model_idx-1))]}"
fi
model="$selected_model"
echo "Selected: $model"

# --- Advanced Options ---
# Read NUM_GPUS and CUSTOM_OPTS from environment or config file
if [ -f "$HOME/.vllm_launcher_config" ]; then
    source "$HOME/.vllm_launcher_config"
fi
if [ -z "$NUM_GPUS" ]; then NUM_GPUS=1; fi
if [ -z "$CUSTOM_OPTS" ]; then CUSTOM_OPTS=""; fi

# --- Memory Fit Warning ---
if [ "$VRAM_TOTAL" -ne 0 ] && [ -n "$model" ]; then
    mdir_size=$(du -sm "$model" | cut -f1)
    if [ "$mdir_size" -gt "$VRAM_TOTAL" ]; then
        echo "WARNING: Model size ($mdir_size MiB) exceeds total VRAM ($VRAM_TOTAL MiB). vLLM may use CPU offloading or fail to load."
    fi
fi

# --- Launch vLLM ---
if [ -n "$model" ]; then
    conda activate "$CONDA_ENV"
    echo "Starting vLLM with model: $model (env: $CONDA_ENV) on $NUM_GPUS GPU(s)"
    nohup python -m vllm.entrypoints.openai.api_server --model "$model" --tensor-parallel-size $NUM_GPUS $CUSTOM_OPTS > ~/vllm_server.log 2>&1 &
    echo "vLLM server started. Log: ~/vllm_server.log"
    # Determine port
    PORT=8000
    if echo "$CUSTOM_OPTS" | grep -q -- '--port'; then
        PORT_VAL=$(echo "$CUSTOM_OPTS" | grep -oP -- '--port[ =]\K[0-9]+' | head -1)
        if [ -n "$PORT_VAL" ]; then
            PORT="$PORT_VAL"
        fi
    fi

# --- Flag Parsing ---
if [[ "$1" == "--list-models" ]]; then
    source_conda
    # Only print models that are likely loadable by vLLM, filter duplicates by basename
    echo "Available vLLM-loadable models:"
    idx=1
    declare -A seen
    for mdir in "${MODEL_DIRS[@]}"; do
        bname=$(basename "$mdir")
        # Skip duplicates
        if [[ -n "${seen[$bname]}" ]]; then
            continue
        fi
        seen[$bname]=1
        msize=$(du -sh "$mdir" | cut -f1)
        # Only include real model dirs
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
        # Skip tiny/empty dirs and non-models
        if [ $loadable -eq 1 ] && [ $(du -s "$mdir" | awk '{print $1}') -gt 5000 ]; then
            echo "[$idx] $bname - $msize - $mformat"
            idx=$((idx+1))
        fi
    done
    exit 0
fi
if [[ "$1" == "--hw-info" ]]; then
    source_conda
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
    source_conda
    if [ -f ~/vllm_server_status.txt ]; then
        statusline=$(cat ~/vllm_server_status.txt)
        if echo "$statusline" | grep -q RUNNING; then
            # Double-check process
            if ps aux | grep vllm.entrypoints.openai.api_server | grep -v grep > /dev/null; then
                # Extract model, port, launch time
                model=$(echo "$statusline" | sed -n 's/^RUNNING: \(.*\) (port .*/\1/p')
                port=$(echo "$statusline" | sed -n 's/.*(port \([0-9]*\)).*/\1/p')
                launched=$(echo "$statusline" | sed -n 's/.*(launched \([0-9]*\)).*/\1/p')
                now=$(date +%s)
                let uptime_sec=now-launched
                if [ $uptime_sec -lt 60 ]; then
                    uptime="${uptime_sec}s"
                elif [ $uptime_sec -lt 3600 ]; then
                    let min=uptime_sec/60
                    let sec=uptime_sec%60
                    uptime="${min}m ${sec}s"
                else
                    let hr=uptime_sec/3600
                    let min=(uptime_sec%3600)/60
                    let sec=uptime_sec%60
                    uptime="${hr}h ${min}m ${sec}s"
                fi
                echo "Server running: $model | port: $port | uptime: $uptime"
            else
                echo "Server not running"
            fi
        else
            echo "$statusline"
        fi
    bname=$(basename "$mdir")
    if [[ -n "${seen[$bname]}" ]]; then
        continue
    fi
    seen[$bname]=1
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
    if [ $loadable -eq 1 ] && [ $(du -s "$mdir" | awk '{print $1}') -gt 5000 ]; then
        MODEL_INFO+=("[$idx] $bname - $msize - $mformat")
        echo "${MODEL_INFO[-1]}"
        idx=$((idx+1))
    fi
done
