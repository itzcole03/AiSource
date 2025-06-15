@echo off
title vLLM Server - Ultimate Copilot AGI
echo ========================================
echo   vLLM Server for Ultimate Copilot AGI
echo   8GB VRAM Optimized Configuration
echo ========================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found at .venv
    echo Please create it with: python -m venv .venv
    echo Then install vllm: pip install vllm
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Check if vllm is installed
python -c "import vllm" 2>nul
if errorlevel 1 (
    echo ERROR: vLLM not installed in virtual environment
    echo Installing vLLM...
    pip install vllm
    if errorlevel 1 (
        echo Failed to install vLLM
        pause
        exit /b 1
    )
)

echo.
echo Available Models for 8GB VRAM:
echo 1. microsoft/DialoGPT-medium (Recommended - Fast, good quality)
echo 2. microsoft/DialoGPT-small (Fastest, lighter quality)
echo 3. codellama/CodeLlama-7b-hf (Code-focused, may be tight on VRAM)
echo 4. mistralai/Mistral-7B-v0.1 (General purpose, may be tight on VRAM)
echo.

REM Default to DialoGPT-medium for best balance
set MODEL_NAME=microsoft/DialoGPT-medium
set /p "MODEL_CHOICE=Enter model choice (1-4) or press Enter for default (1): "

if "%MODEL_CHOICE%"=="2" set MODEL_NAME=microsoft/DialoGPT-small
if "%MODEL_CHOICE%"=="3" set MODEL_NAME=codellama/CodeLlama-7b-hf
if "%MODEL_CHOICE%"=="4" set MODEL_NAME=mistralai/Mistral-7B-v0.1

echo.
echo Starting vLLM server with model: %MODEL_NAME%
echo Server will be available at: http://localhost:8000
echo.
echo VRAM Optimizations:
echo - Max model length: 2048 tokens
echo - GPU memory utilization: 0.85 (85%%)
echo - Tensor parallel size: 1
echo.

REM Start vLLM with 8GB VRAM optimizations
python -m vllm.entrypoints.openai.api_server ^
    --model %MODEL_NAME% ^
    --host 0.0.0.0 ^
    --port 8000 ^
    --max-model-len 2048 ^
    --gpu-memory-utilization 0.85 ^
    --tensor-parallel-size 1 ^
    --dtype float16 ^
    --max-num-seqs 16 ^
    --max-num-batched-tokens 2048

echo.
echo vLLM server stopped.
pause
