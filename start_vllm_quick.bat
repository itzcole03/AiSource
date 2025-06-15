@echo off
REM Optimized vLLM CPU Startup for Ultimate Copilot
REM Quick launcher with model selection for 8GB RAM systems

title Ultimate Copilot - vLLM CPU Server

echo.
echo ╔═══════════════════════════════════════════╗
echo ║        Ultimate Copilot vLLM CPU          ║
echo ║            Quick Launcher                 ║
echo ╚═══════════════════════════════════════════╝
echo.

echo Available model configurations:
echo.
echo [1] ⚡ FAST    - DistilGPT2 (smallest, fastest)
echo [2] ⚖️ BALANCED - GPT2 (good balance)  
echo [3] 🎯 QUALITY - GPT2-Medium (best quality)
echo [4] 💻 CODE    - CodeGPT-Small-Py (programming)
echo [5] 🔧 CUSTOM  - Enter your own model
echo.

set /p choice="Select model configuration [1-5]: "

if "%choice%"=="1" set MODEL_TYPE=small
if "%choice%"=="2" set MODEL_TYPE=medium  
if "%choice%"=="3" set MODEL_TYPE=large
if "%choice%"=="4" set MODEL_TYPE=code
if "%choice%"=="5" (
    set /p MODEL_TYPE="Enter model name: "
)

if "%MODEL_TYPE%"=="" (
    echo ❌ Invalid selection, using default (FAST)
    set MODEL_TYPE=small
)

echo.
echo 🚀 Starting vLLM CPU server with %MODEL_TYPE% configuration...
echo 💻 CPU mode optimized for 8GB RAM
echo 🌐 Server will be at: http://localhost:8000
echo.

REM Check WSL and start server
wsl --version >nul 2>&1
if errorlevel 1 (
    echo ❌ WSL not available! Please install WSL with Ubuntu.
    pause
    exit /b 1
)

echo ✅ Starting via WSL Ubuntu...
echo.

REM Execute the optimized script in WSL
wsl bash -c "cd /mnt/c/Users/bcmad/Downloads/project-bolt-withastro-astro-tczzygud/project/project/ultimate_copilot && chmod +x start_vllm_optimized.sh && ./start_vllm_optimized.sh %MODEL_TYPE%"

echo.
echo 🛑 vLLM server stopped
echo 📋 Check the logs above for any errors
pause
