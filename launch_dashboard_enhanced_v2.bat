@echo off
REM Ultimate Copilot Dashboard Launcher for Windows (Enhanced v2)
REM This script uses the new enhanced Python launcher with automatic port detection

echo.
echo ================================================
echo   Ultimate Copilot Enhanced Dashboard Launcher
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and add it to PATH
    echo.
    echo Download Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python is available

REM Change to the project directory
cd /d "%~dp0"
echo [OK] Changed to project directory: %CD%

REM Check if enhanced launcher exists
if not exist "frontend\launch_dashboard_enhanced.py" (
    echo ERROR: Enhanced launcher not found
    echo Please ensure frontend\launch_dashboard_enhanced.py exists
    pause
    exit /b 1
)

echo [OK] Enhanced launcher found

REM Ask user for launch preference
echo.
echo Choose launch mode:
echo 1. Standard launch (uses existing Python environment)
echo 2. Virtual environment (recommended - creates isolated environment)
echo 3. User installation (installs packages with --user flag)
echo.
choice /C 123 /M "Select option (1-3)"

if errorlevel 3 goto :user_install
if errorlevel 2 goto :venv_launch
if errorlevel 1 goto :standard_launch

:standard_launch
echo.
echo Launching dashboard with standard Python environment...
python frontend\launch_dashboard_enhanced.py
goto :end

:user_install
echo.
echo Launching dashboard with user package installation...
set PYTHONPATH=%CD%;%PYTHONPATH%
python -m pip install --user streamlit fastapi uvicorn plotly pandas pyyaml requests psutil 2>nul
python frontend\launch_dashboard_enhanced.py
goto :end

:venv_launch
echo.
echo Setting up virtual environment for dashboard...

REM Check if virtual environment already exists
if exist "dashboard_env" (
    echo [OK] Found existing virtual environment
    goto :activate_venv
)

echo Creating new virtual environment...
python -m venv dashboard_env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Falling back to standard launch...
    goto :standard_launch
)

echo [OK] Virtual environment created

:activate_venv
echo Activating virtual environment...
call dashboard_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo Falling back to standard launch...
    goto :standard_launch
)

echo [OK] Virtual environment activated

REM Install/update packages in virtual environment
echo Installing dashboard dependencies...
python -m pip install --upgrade pip
python -m pip install streamlit fastapi uvicorn plotly pandas pyyaml requests psutil

echo.
echo [OK] Dependencies installed, launching dashboard...
python frontend\launch_dashboard_enhanced.py

:end
echo.
echo Dashboard session ended.
if exist "dashboard_env" (
    echo.
    echo To run again with the same virtual environment:
    echo   call dashboard_env\Scripts\activate.bat
    echo   python frontend\launch_dashboard_enhanced.py
)
echo.
pause
