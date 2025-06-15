@echo off
cls
echo.
echo ===============================================
echo   ULTIMATE COPILOT SYSTEM LAUNCHER
echo ===============================================
echo.
echo This launcher starts the Ultimate Copilot System featuring:
echo - Custom agent orchestration (8GB VRAM optimized)
echo - Unlimited local model execution  
echo - Void Editor prioritization
echo - VS Code Insiders swarm automation
echo - Multi-provider LLM support (Ollama, LM Studio, vLLM)
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Current directory: %CD%
echo.

echo ===========================================
echo   STARTUP OPTIONS
echo ===========================================
echo.
echo 1. Start Ultimate Copilot System (Recommended)
echo 2. Start with Dashboard
echo 3. Start Hybrid System (CodeGPT + Custom)
echo 4. Dashboard Only
echo 5. Start vLLM Service (Ubuntu/WSL)
echo 6. Show System Status
echo 7. Exit
echo.
set /p choice="Select option (1-7): "

if "%choice%"=="1" goto start_main
if "%choice%"=="2" goto start_with_dashboard
if "%choice%"=="3" goto start_hybrid
if "%choice%"=="4" goto dashboard_only
if "%choice%"=="5" goto start_vllm
if "%choice%"=="6" goto show_status
if "%choice%"=="7" goto exit
goto invalid_choice

:start_main
echo.
echo Starting Ultimate Copilot System...
echo - Custom multi-agent orchestration
echo - 8GB VRAM optimization
echo - Void Editor and VS Code integration
echo - Unlimited local model execution
echo.
python main.py
goto end

:start_with_dashboard
echo.
echo Starting Ultimate Copilot System with Dashboard...
start /B python start_dashboard.py
timeout /t 3 /nobreak >nul
python main.py
goto end

:start_hybrid
echo.
echo Starting Hybrid System...
echo - Custom agents + optional CodeGPT integration
echo - Note: CodeGPT requires paid subscription for meaningful usage
echo.
python main_hybrid.py
goto end

:dashboard_only
echo.
echo Starting Dashboard Only...
echo Open http://localhost:8501 in your browser
echo.
python start_dashboard.py
goto end

:start_vllm
echo.
echo Starting vLLM CPU Service in Ubuntu/WSL...
echo ===========================================
echo.
echo This will automatically:
echo 1. Open Ubuntu terminal
echo 2. Navigate to project directory
echo 3. Activate vLLM virtual environment
echo 4. Start vLLM CPU service on port 8000
echo.
echo The vLLM service will run on http://localhost:8000
echo.
set /p proceed="Continue with vLLM CPU startup? (y/N): "
if /i not "%proceed%"=="y" goto end
echo.
echo Opening Ubuntu terminal and starting vLLM CPU service...
start wsl -d Ubuntu -- bash -c "
cd /mnt/c/Users/%USERNAME%/Downloads/project-bolt-withastro-astro-tczzygud/project/project/ultimate_copilot && 
echo '=== Starting vLLM CPU Service ===' && 
echo 'Activating virtual environment...' && 
source vllm_env/bin/activate && 
echo 'Environment activated: '$(which python) && 
echo 'Starting vLLM CPU server...' && 
echo 'Service will be available at http://localhost:8000' && 
echo 'Press Ctrl+C to stop the service' && 
echo '=================================' && 
VLLM_USE_CPU=1 python3 -m vllm.entrypoints.openai.api_server --model gpt2 --host 0.0.0.0 --port 8000 --max-model-len 512 --dtype float32 || 
echo 'Fallback: trying with python instead of python3...' && 
VLLM_USE_CPU=1 python -m vllm.entrypoints.openai.api_server --model gpt2 --host 0.0.0.0 --port 8000 --max-model-len 512 --dtype float32; 
exec bash"
echo.
echo vLLM CPU service startup initiated in Ubuntu terminal
echo The service will be available at http://localhost:8000 once started
echo Check the Ubuntu terminal for startup progress
echo.
pause
goto end

:show_status
echo.
echo ===========================================
echo   ULTIMATE COPILOT SYSTEM STATUS
echo ===========================================
echo.
echo Python Version:
python --version
echo.
echo Required Packages:
python -c "
import sys
packages = ['fastapi', 'streamlit', 'aiohttp', 'qdrant_client', 'sentence_transformers', 'pyyaml', 'psutil']
for pkg in packages:
    try:
        __import__(pkg.replace('-', '_'))
        print(f'✓ {pkg} - installed')
    except ImportError:
        print(f'✗ {pkg} - missing')
"
echo.
echo Configuration Files:
if exist "config\system_config.yaml" (echo ✓ system_config.yaml - found) else (echo ✗ system_config.yaml - missing)
if exist "config\hybrid_config.yaml" (echo ✓ hybrid_config.yaml - found) else (echo ✗ hybrid_config.yaml - missing)
echo.
echo Local Models (Ollama):
python -c "
import requests
try:
    response = requests.get('http://localhost:11434/api/tags', timeout=2)
    if response.status_code == 200:
        models = response.json().get('models', [])
        print(f'✓ Ollama running with {len(models)} models')
        for model in models[:3]:
            print(f'  - {model.get(\"name\", \"unknown\")}')
        if len(models) > 3:
            print(f'  ... and {len(models) - 3} more')
    else:
        print('⚠ Ollama running but no models found')
except:
    print('✗ Ollama not running or not accessible')
"
echo.
pause
goto menu

:invalid_choice
echo.
echo Invalid choice. Please select 1-7.
echo.
pause
goto menu

:menu
cls
echo.
echo ===============================================
echo   ULTIMATE COPILOT SYSTEM LAUNCHER
echo ===============================================
echo.
echo This launcher starts the Ultimate Copilot System featuring:
echo - Custom agent orchestration (8GB VRAM optimized)
echo - Unlimited local model execution  
echo - Void Editor prioritization
echo - VS Code Insiders swarm automation
echo - Multi-provider LLM support (Ollama, LM Studio, vLLM)
echo.
echo ===========================================
echo   STARTUP OPTIONS
echo ===========================================
echo.
echo 1. Start Ultimate Copilot System (Recommended)
echo 2. Start with Dashboard
echo 3. Start Hybrid System (CodeGPT + Custom)
echo 4. Dashboard Only
echo 5. Start vLLM Service (Ubuntu/WSL)
echo 6. Show System Status
echo 7. Exit
echo.
set /p choice="Select option (1-7): "

if "%choice%"=="1" goto start_main
if "%choice%"=="2" goto start_with_dashboard
if "%choice%"=="3" goto start_hybrid
if "%choice%"=="4" goto dashboard_only
if "%choice%"=="5" goto start_vllm
if "%choice%"=="6" goto show_status
if "%choice%"=="7" goto exit
goto invalid_choice

:exit
echo.
echo Thank you for using Ultimate Copilot System!
echo.
exit /b 0

:end
echo.
echo System has stopped. Press any key to return to menu...
pause >nul
goto menu
