@echo off
echo ========================================
echo   Unified AI Model Manager Launcher
echo ========================================
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python from https://python.org/
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed
echo.

echo [1/4] Installing/Updating dependencies...
call npm install --user
if errorlevel 1 (
    echo ❌ Failed to install Node.js dependencies
    pause
    exit /b 1
)

echo [2/4] Installing Python backend dependencies...
cd backend
pip install --user -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    cd ..
    pause
    exit /b 1
)
cd ..

echo [3/4] Starting Backend Server...
start "Model Manager Backend" cmd /k "cd backend && python server_optimized.py"

echo [4/4] Starting Marketplace Aggregator...
start "Marketplace Aggregator" cmd /k "node marketplace-aggregator-final-fixed.js"

echo.
echo ⏳ Waiting for services to initialize...
timeout /t 5 /nobreak > nul

echo Starting Frontend Development Server...
start "Model Manager Frontend" cmd /k "npm run dev"

echo.
echo ========================================
echo   🚀 Unified Model Manager Started!
echo ========================================
echo.
echo 📊 Backend API: http://localhost:8080
echo 🛒 Marketplace: http://localhost:3030
echo 🖥️  Frontend: http://localhost:5173
echo.
echo 📝 Services are starting in separate windows.
echo    Close this window when you're done.
echo.
echo ⚠️  If any service fails to start:
echo    1. Check the individual service windows for errors
echo    2. Ensure ports 8080, 3030, and 5173 are available
echo    3. Run 'npm run start-full' for integrated logging
echo.
echo Press any key to open the application in your browser...
pause > nul

start http://localhost:5173

echo.
echo 🎉 Application should now be opening in your browser!
echo    Keep this window open to monitor the services.
echo.
pause