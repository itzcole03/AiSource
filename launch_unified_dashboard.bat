@echo off
REM Ultimate Copilot Dashboard Launcher for Windows
REM This script launches the unified dashboard system

echo.
echo ================================================
echo   Ultimate Copilot Unified Dashboard Launcher
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    pause
    exit /b 1
)

echo ✓ Python is available

REM Change to the project directory
cd /d "%~dp0.."
echo ✓ Changed to project directory: %CD%

REM Check if required packages are installed
echo.
echo Checking dependencies...
python -c "import streamlit, fastapi, uvicorn, plotly, pandas" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some required packages may be missing
    echo Installing required packages to user directory...
    pip install --user streamlit fastapi uvicorn plotly pandas pyyaml requests psutil
    if errorlevel 1 (
        echo ERROR: Failed to install packages to user directory
        echo.
        echo Trying alternative installation methods...
        echo.
        echo Option 1: Install with conda (if available):
        echo   conda install streamlit fastapi uvicorn plotly pandas pyyaml requests psutil
        echo.
        echo Option 2: Install in virtual environment:
        echo   python -m venv dashboard_env
        echo   dashboard_env\Scripts\activate
        echo   pip install streamlit fastapi uvicorn plotly pandas pyyaml requests psutil
        echo.
        echo Option 3: Run as administrator and try again
        echo.
        pause
        exit /b 1
    )
    echo ✓ Packages installed successfully to user directory
) else (
    echo ✓ All required packages are available
)

echo.
echo Starting Ultimate Copilot Dashboard...
echo.
echo The dashboard will open in your web browser at:
echo   http://localhost:8501
echo.
echo Backend API will be available at:
echo   http://localhost:8001
echo.
echo Press Ctrl+C to stop the dashboard
echo.

REM Launch the dashboard
python frontend\launch_dashboard.py

echo.
echo Dashboard stopped.
pause
