@echo off
title vLLM Server - Ultimate Copilot AGI (Advanced)
echo ========================================
echo   vLLM Server - Ultimate Copilot AGI
echo   Advanced 8GB VRAM Configuration
echo ========================================
echo.

REM Set environment variables for optimization
set CUDA_VISIBLE_DEVICES=0
set VLLM_USE_MODELSCOPE=false
set VLLM_WORKER_MULTIPROC_METHOD=spawn

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check and install vllm if needed
python -c "import vllm" 2>nul
if errorllevel 1 (
    echo Installing vLLM and dependencies...
    pip install --upgrade pip
    pip install vllm torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
    if errorlevel 1 (
        echo Failed to install vLLM
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo   Model Selection for 8GB VRAM
echo ========================================
echo.
echo Recommended Models:
echo 1. microsoft/DialoGPT-medium    [Recommended - 1.4GB, Fast, Good Quality]
echo 2. microsoft/DialoGPT-small     [Fastest - 400MB, Light Quality]
echo 3. TinyLlama/TinyLlama-1.1B     [Tiny but Capable - 2GB]
echo 4. microsoft/phi-2               [Code + Chat - 2.8GB]
echo 5. codellama/CodeLlama-7b-hf    [Code Expert - 6.7GB, Tight Fit]
echo 6. mistralai/Mistral-7B-v0.1    [General Purpose - 7GB, Very Tight]
echo.
echo Advanced Options:
echo 7. Custom model path
echo 8. Hugging Face model ID
echo.

set MODEL_NAME=microsoft/DialoGPT-medium
set /p "MODEL_CHOICE=Select model (1-8) or press Enter for default (1): "

if "%MODEL_CHOICE%"=="1" set MODEL_NAME=microsoft/DialoGPT-medium
if "%MODEL_CHOICE%"=="2" set MODEL_NAME=microsoft/DialoGPT-small
if "%MODEL_CHOICE%"=="3" set MODEL_NAME=TinyLlama/TinyLlama-1.1B-Chat-v1.0
if "%MODEL_CHOICE%"=="4" set MODEL_NAME=microsoft/phi-2
if "%MODEL_CHOICE%"=="5" set MODEL_NAME=codellama/CodeLlama-7b-Instruct-hf
if "%MODEL_CHOICE%"=="6" set MODEL_NAME=mistralai/Mistral-7B-Instruct-v0.1
if "%MODEL_CHOICE%"=="7" (
    set /p "MODEL_NAME=Enter custom model path: "
)
if "%MODEL_CHOICE%"=="8" (
    set /p "MODEL_NAME=Enter Hugging Face model ID: "
)

echo.
echo ========================================
echo   Starting vLLM Server
echo ========================================
echo.
echo Model: %MODEL_NAME%
echo Server: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Optimizations Applied:
echo - GPU Memory Utilization: 85%%
echo - Max Model Length: 2048 tokens
echo - Data Type: float16 (memory efficient)
echo - Max Concurrent Sequences: 16
echo - Tensor Parallel: 1 (single GPU)
echo.

REM Create a simple test script
echo import requests > test_vllm.py
echo import json >> test_vllm.py
echo. >> test_vllm.py
echo def test_vllm(): >> test_vllm.py
echo     try: >> test_vllm.py
echo         response = requests.post("http://localhost:8000/v1/chat/completions", >> test_vllm.py
echo             json={"model": "%MODEL_NAME%", "messages": [{"role": "user", "content": "Hello!"}], "max_tokens": 50}) >> test_vllm.py
echo         print("✅ vLLM is working:", response.json()["choices"][0]["message"]["content"]) >> test_vllm.py
echo     except Exception as e: >> test_vllm.py
echo         print("❌ vLLM test failed:", e) >> test_vllm.py
echo. >> test_vllm.py
echo if __name__ == "__main__": test_vllm() >> test_vllm.py

echo Starting vLLM server...
echo (Press Ctrl+C to stop)
echo.

REM Start vLLM with optimized settings for 8GB VRAM
python -m vllm.entrypoints.openai.api_server ^
    --model "%MODEL_NAME%" ^
    --host 0.0.0.0 ^
    --port 8000 ^
    --max-model-len 2048 ^
    --gpu-memory-utilization 0.85 ^
    --tensor-parallel-size 1 ^
    --dtype float16 ^
    --max-num-seqs 16 ^
    --max-num-batched-tokens 2048 ^
    --disable-log-stats ^
    --served-model-name "copilot-model"

echo.
echo ========================================
echo vLLM server has stopped.
echo.
echo To test the server manually, run:
echo python test_vllm.py
echo.
pause
