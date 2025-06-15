@echo off
cls
echo.
echo ==========================================
echo   ULTIMATE COPILOT SWARM - QUICK START
echo ==========================================
echo.
echo Starting the autonomous agent swarm...
echo This will get your copilot running immediately!
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found. Starting swarm...
echo.

REM Run the swarm
python run_swarm.py

echo.
echo Swarm session ended.
pause
