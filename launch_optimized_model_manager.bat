@echo off
REM Optimized Model Manager Launcher for Windows
REM Starts both backend and frontend with proper error handling

echo ========================================
echo   Ultimate Copilot - Model Manager
echo   Optimized Launch Script for Windows
echo ========================================
echo.

REM Set working directory
cd /d "%~dp0"

REM Check Python
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found or not in PATH
    echo 📥 Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
echo ✅ Python found

REM Check Node.js
echo [2/6] Checking Node.js installation...
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Node.js not found or not in PATH
    echo 📥 Please install Node.js 16+ from https://nodejs.org
    pause
    exit /b 1
)
echo ✅ Node.js found

REM Check npm
echo [3/6] Checking npm installation...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: npm not found
    echo 📥 Please ensure npm is installed with Node.js
    pause
    exit /b 1
)
echo ✅ npm found

REM Install Python dependencies if needed
echo [4/6] Checking Python dependencies...
python -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing Python dependencies...
    pip install fastapi uvicorn requests psutil
    if errorlevel 1 (
        echo ❌ ERROR: Failed to install Python dependencies
        pause
        exit /b 1
    )
)
echo ✅ Python dependencies ready

REM Install Node.js dependencies if needed
echo [5/6] Checking Node.js dependencies...
if not exist "frontend\model manager\node_modules" (
    echo 📦 Installing Node.js dependencies (this may take a few minutes)...
    cd "frontend\model manager"
    npm install
    if errorlevel 1 (
        echo ❌ ERROR: Failed to install Node.js dependencies
        cd ..\..
        pause
        exit /b 1
    )
    cd ..\..
)
echo ✅ Node.js dependencies ready

REM Launch the optimized launcher
echo [6/6] Starting Model Manager...
echo.
echo 🚀 Launching Optimized Model Manager...
echo 📊 Backend will start on: http://localhost:8002
echo 🎨 Frontend will start on: http://localhost:5173
echo.
echo 🛑 Press Ctrl+C to stop all services
echo.

python launch_simple_model_manager.py

echo.
echo 👋 Model Manager stopped
pause
