@echo off
REM Simple Model Manager Launcher - Fixed Version
REM This version should not close immediately

echo ========================================
echo   Ultimate Copilot - Model Manager
echo   Simple Launch Script (Fixed)
echo ========================================
echo.

REM Set working directory
cd /d "%~dp0"
echo Current directory: %CD%
echo.

REM Check if Python is available
echo Checking Python...
python --version
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Python not found in PATH
    echo 📥 Please install Python 3.8+ from https://python.org
    echo.
    pause
    exit /b 1
)
echo ✅ Python found
echo.

REM Check if Node.js is available
echo Checking Node.js...
node --version
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Node.js not found in PATH
    echo 📥 Please install Node.js 16+ from https://nodejs.org
    echo.
    pause
    exit /b 1
)
echo ✅ Node.js found
echo.

REM Check if required directories exist
if not exist "frontend\model manager" (
    echo ❌ ERROR: Model Manager directory not found
    echo Expected: frontend\model manager
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)
echo ✅ Model Manager directory found
echo.

REM Launch the Python script
echo 🚀 Starting Model Manager...
echo 📊 Backend will be available at: http://localhost:8002
echo 🎨 Frontend will be available at: http://localhost:5173
echo.
echo ⏳ Starting services (this may take a moment)...
echo.

python launch_simple_model_manager.py

echo.
echo 👋 Model Manager has stopped
echo.
pause
