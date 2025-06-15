@echo off
REM vLLM CPU Server Startup Batch File for Windows
REM This batch file starts vLLM in CPU mode via WSL/Ubuntu

echo 🚀 Starting vLLM CPU Server via WSL...
echo.

REM Check if WSL is available
wsl --version >nul 2>&1
if errorlevel 1 (
    echo ❌ WSL not found! Please install Windows Subsystem for Linux first.
    echo    Visit: https://docs.microsoft.com/en-us/windows/wsl/install
    pause
    exit /b 1
)

echo ✅ WSL detected, starting Ubuntu terminal...
echo 💻 Running vLLM in CPU mode (no GPU required)
echo 🔧 Server will be available at: http://localhost:8000
echo.

REM Default model - you can change this
set MODEL_NAME=microsoft/DialoGPT-medium

REM Alternative CPU-friendly models:
REM set MODEL_NAME=microsoft/DialoGPT-small
REM set MODEL_NAME=gpt2
REM set MODEL_NAME=distilgpt2
REM set MODEL_NAME=microsoft/CodeGPT-small-py

echo 📦 Starting with model: %MODEL_NAME%
echo.

REM Change to the project directory in WSL and start vLLM
wsl bash -c "cd /mnt/c/Users/bcmad/Downloads/project-bolt-withastro-astro-tczzygud/project/project/ultimate_copilot && ./start_vllm_cpu.sh %MODEL_NAME%"

echo.
echo 🛑 vLLM server has been stopped
pause
