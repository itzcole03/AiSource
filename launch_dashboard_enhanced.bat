@echo off
REM Ultimate Copilot Dashboard Launcher for Windows (Enhanced)
REM This script launches the unified dashboard system with better dependency management

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
    echo.
    echo Download Python from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python is available

REM Change to the project directory
cd /d "%~dp0"
echo [OK] Changed to project directory: %CD%

REM Check if we should use a virtual environment
set USE_VENV=0
if exist "dashboard_env\Scripts\python.exe" (
    echo ✓ Found existing virtual environment
    set USE_VENV=1
    set PYTHON_EXEC=dashboard_env\Scripts\python.exe
) else (
    echo.
    echo Virtual environment not found.
    echo The enhanced dashboard requires specific package versions.
    echo.
    choice /C YN /M "Create virtual environment with compatible packages? (Y/N)"
    if errorlevel 2 goto :skip_venv
    if errorlevel 1 goto :create_venv
)

:create_venv
echo.
echo Creating virtual environment...
python -m venv dashboard_env
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    echo Falling back to user installation...
    goto :skip_venv
)
echo ✓ Virtual environment created
echo Installing compatible packages...
dashboard_env\Scripts\python.exe -m pip install streamlit fastapi==0.103.0 uvicorn pydantic==2.0.3 plotly pandas pyyaml requests psutil
if errorlevel 1 (
    echo ERROR: Failed to install packages to virtual environment
    goto :skip_venv
)
echo ✓ Compatible packages installed
set USE_VENV=1
set PYTHON_EXEC=dashboard_env\Scripts\python.exe

:skip_venv
if %USE_VENV%==0 (
    set PYTHON_EXEC=python
)
REM Activate virtual environment if we're using one
if %USE_VENV%==1 (
    echo Activating virtual environment...
    call dashboard_env\Scripts\activate.bat
    if errorlevel 1 (
        echo WARNING: Failed to activate virtual environment
        echo Continuing with system Python...
        set USE_VENV=0
    ) else (
        echo ✓ Virtual environment activated
    )
)

REM Check if required packages are installed in the target Python
echo.
echo Checking dependencies...
%PYTHON_EXEC% -c "import streamlit, fastapi, uvicorn, plotly, pandas, yaml, requests, psutil" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some required packages may be missing
    echo Installing required packages...
    
    if %USE_VENV%==1 (
        echo Installing to virtual environment...
        pip install streamlit fastapi uvicorn plotly pandas pyyaml requests psutil
    ) else (
        echo Installing to user directory...
        pip install --user streamlit fastapi uvicorn plotly pandas pyyaml requests psutil
    )
    
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        echo.
        echo Please try one of these solutions:
        echo.
        echo 1. Run this script as Administrator
        echo 2. Install packages manually:
        echo    pip install --user streamlit fastapi uvicorn plotly pandas pyyaml requests psutil
        echo 3. Use conda instead of pip:
        echo    conda install streamlit fastapi uvicorn plotly pandas pyyaml requests psutil
        echo.
        pause
        exit /b 1
    )
    echo ✓ Packages installed successfully
) else (
    echo ✓ All required packages are available
)

REM Verify installation
echo.
echo Verifying installation...
python -c "import streamlit; print(f'Streamlit version: {streamlit.__version__}')" 2>nul
if errorlevel 1 (
    echo WARNING: Streamlit verification failed
) else (
    echo ✓ Streamlit verified
)

python -c "import fastapi; print(f'FastAPI version: {fastapi.__version__}')" 2>nul
if errorlevel 1 (
    echo WARNING: FastAPI verification failed
) else (
    echo ✓ FastAPI verified
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

REM Launch the ultra-safe dashboard launcher (no numpy conflicts)
%PYTHON_EXEC% launch_ultimate_safe.py

REM Deactivate virtual environment if we used one
if %USE_VENV%==1 (
    echo.
    echo Deactivating virtual environment...
    deactivate 2>nul
)

echo.
echo Dashboard stopped.
pause
