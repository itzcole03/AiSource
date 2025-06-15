@echo off
cls
echo.
echo ===============================================
echo   ULTIMATE COPILOT - OPTIMIZED LAUNCHER V2
echo ===============================================
echo.
echo 🚀 8GB VRAM Optimized AI Development Assistant
echo 🤖 Multi-Agent Orchestration System
echo 🔧 Zero Subscription Cost
echo ⚡ Unlimited Local Execution
echo.

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python 3.8+ is required
    echo Please install Python and try again
    echo.
    pause
    exit /b 1
)

REM Check virtual environment
if exist "env\Scripts\activate.bat" (
    echo 🐍 Activating virtual environment...
    call env\Scripts\activate.bat
) else (
    echo ⚠️ No virtual environment found, using system Python
)

REM Create logs directory
if not exist "logs" mkdir logs

echo.
echo ===============================================
echo   STARTUP OPTIONS
echo ===============================================
echo.
echo [1] 🚀 Quick Start (Recommended)
echo [2] 📊 With Dashboard
echo [3] 🔧 Advanced Configuration
echo [4] 🧪 System Check & Optimization
echo [5] 📚 Help & Documentation
echo [0] ❌ Exit
echo.
set /p choice="Select option (1-5): "

if "%choice%"=="1" goto quick_start
if "%choice%"=="2" goto with_dashboard
if "%choice%"=="3" goto advanced_config
if "%choice%"=="4" goto system_check
if "%choice%"=="5" goto help
if "%choice%"=="0" goto exit
goto menu

:quick_start
echo.
echo 🚀 Starting Ultimate Copilot System (Quick Mode)...
echo.
echo Initializing components:
echo - ✅ VRAM Manager (8GB optimized)
echo - ✅ Multi-Agent System
echo - ✅ LLM Provider Detection
echo - ✅ Editor Integration
echo.
python main.py
goto end

:with_dashboard
echo.
echo 📊 Starting Ultimate Copilot with Dashboard...
echo.
echo Starting dashboard in new window...
start "Ultimate Copilot Dashboard" cmd /k "python -m streamlit run frontend\dashboard.py --server.port 8501 --server.address localhost"
timeout /t 3 /nobreak >nul

echo Starting main system...
python main.py
goto end

:advanced_config
echo.
echo 🔧 Advanced Configuration Options:
echo.
echo [1] Edit System Configuration
echo [2] Edit Models Configuration  
echo [3] Reset to Default Settings
echo [4] View Current Settings
echo [B] Back to Main Menu
echo.
set /p config_choice="Select option: "

if "%config_choice%"=="1" (
    if exist "config\system_config.yaml" (
        notepad config\system_config.yaml
    ) else (
        echo Creating default system config...
        copy config\system_config.yaml.example config\system_config.yaml
        notepad config\system_config.yaml
    )
    goto advanced_config
)
if "%config_choice%"=="2" (
    notepad config\models_config.yaml
    goto advanced_config
)
if "%config_choice%"=="3" (
    echo Resetting configurations to defaults...
    copy /y config\system_config.yaml.example config\system_config.yaml
    copy /y config\models_config_optimized_8gb.yaml config\models_config.yaml
    echo ✅ Configuration reset complete
    pause
    goto advanced_config
)
if "%config_choice%"=="4" (
    echo.
    echo Current Configuration:
    echo =====================
    python -c "
import yaml
try:
    with open('config/system_config.yaml', 'r') as f:
        config = yaml.safe_load(f)
        print(f'System Version: {config.get(\"system\", {}).get(\"version\", \"Unknown\")}')
        print(f'Debug Mode: {config.get(\"system\", {}).get(\"debug\", False)}')
        print(f'Enabled Providers: {list(config.get(\"llm_providers\", {}).keys())}')
except Exception as e:
    print(f'Error reading config: {e}')
"
    echo.
    pause
    goto advanced_config
)
if /i "%config_choice%"=="B" goto menu
goto advanced_config

:system_check
echo.
echo 🧪 System Check & Optimization
echo ==============================
echo.

echo Checking system requirements...
python -c "
import sys
import subprocess
import os
from pathlib import Path

print(f'✅ Python Version: {sys.version.split()[0]}')

# Check GPU
try:
    result = subprocess.run(['nvidia-smi', '--query-gpu=memory.total', '--format=csv,noheader,nounits'], 
                          capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        vram_mb = int(result.stdout.strip())
        vram_gb = vram_mb / 1024
        print(f'✅ GPU VRAM: {vram_gb:.1f}GB')
        if vram_gb >= 8:
            print('✅ VRAM is sufficient for all models')
        elif vram_gb >= 6:
            print('⚠️ VRAM is sufficient for medium models')
        else:
            print('⚠️ VRAM is limited - will use small models only')
    else:
        print('⚠️ No NVIDIA GPU detected - using CPU models')
except Exception:
    print('⚠️ GPU detection failed - assuming CPU mode')

# Check available models
providers_status = {}
providers = {
    'Ollama': 'http://localhost:11434/api/tags',
    'LM Studio': 'http://localhost:1234/v1/models',
    'vLLM': 'http://localhost:8000/v1/models'
}

import requests
for name, url in providers.items():
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            print(f'✅ {name}: Available')
        else:
            print(f'❌ {name}: Not running')
    except:
        print(f'❌ {name}: Not available')

print(f'✅ Config Directory: {\"Exists\" if Path(\"config\").exists() else \"Missing\"}')
print(f'✅ Logs Directory: {\"Exists\" if Path(\"logs\").exists() else \"Will be created\"}')
"

echo.
echo Running VRAM optimization...
python -c "
import sys
sys.path.append('.')
try:
    from core.vram_manager import VRAMManager
    import asyncio
    
    async def optimize():
        vram = VRAMManager()
        info = await vram.optimize_for_system()
        print(f'🎯 Optimization Level: {info[\"optimization_level\"]}')
        print(f'🎯 Max VRAM: {info[\"configured_max_gb\"]:.1f}GB')
        print(f'🎯 Recommended Models: {len(info[\"recommended_models\"])}')
        for model in info[\"recommended_models\"][:5]:
            print(f'   - {model}')
    
    asyncio.run(optimize())
except Exception as e:
    print(f'⚠️ VRAM optimization check failed: {e}')
"

echo.
echo System check complete!
pause
goto menu

:help
echo.
echo 📚 Ultimate Copilot System Help
echo ===============================
echo.
echo Quick Setup:
echo 1. Ensure Python 3.8+ is installed
echo 2. Install at least one LLM provider (Ollama recommended)
echo 3. Run option 1 (Quick Start)
echo.
echo Supported LLM Providers:
echo - Ollama (Local, Free) - Recommended
echo - LM Studio (Local, Free, GUI)
echo - vLLM (Local, High Performance)
echo - Cloud APIs (Optional fallback)
echo.
echo System Requirements:
echo - 8GB+ RAM (16GB recommended)
echo - Optional: 8GB+ VRAM for GPU acceleration
echo - Windows 10/11, Linux, or macOS
echo.
echo Documentation:
echo - README.md - Main documentation
echo - docs/INSTALL_GUIDE.md - Detailed setup
echo - docs/TROUBLESHOOTING.md - Common issues
echo.
echo Dashboard URL: http://localhost:8501
echo API Endpoint: http://localhost:8000
echo.
pause
goto menu

:exit
echo.
echo Goodbye! 👋
echo.
exit /b 0

:end
echo.
echo System has stopped. Press any key to return to menu...
pause >nul
goto menu

:menu
cls
goto :eof
