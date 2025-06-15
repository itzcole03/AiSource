@echo off
REM Quick Start Script for Ultimate Copilot Dashboard v2

echo ========================================
echo Ultimate Copilot Dashboard v2
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Check if the main dashboard file exists
if not exist "ultimate_dashboard_v2.py" (
    echo ERROR: ultimate_dashboard_v2.py not found
    echo Make sure you're running this from the correct directory
    pause
    exit /b 1
)

echo Checking dependencies...

REM Check for tkinter (usually included with Python)
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo WARNING: tkinter not available - GUI will be disabled
) else (
    echo OK: GUI support available
)

echo.
echo Starting Ultimate Copilot Dashboard v2...
echo.
echo Instructions:
echo - The dashboard will open in a new window
echo - Close the window to exit
echo - Check the console for status messages
echo.

REM Launch the dashboard
python launch_dashboard_v2.py

echo.
echo Dashboard session ended.
pause
