@echo off
title Ultimate Copilot - Quick Launch
color 0b

echo.
echo ===============================================
echo   ULTIMATE COPILOT - QUICK LAUNCH
echo ===============================================
echo.
echo 🚀 Starting Enhanced System...
echo.

REM Check if we're in the right directory
if not exist "universal_dashboard_launcher.py" (
    echo ❌ Error: Script not found. Please run from the correct directory.
    pause
    exit /b 1
)

REM Quick dependency check
python -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing missing dependencies...
    python -m pip install fastapi uvicorn pydantic requests
)

echo ✅ Dependencies OK
echo.

REM Start the universal launcher
echo 🚀 Launching Universal Dashboard...
python universal_dashboard_launcher.py

pause
