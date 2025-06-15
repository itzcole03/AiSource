@echo off
cls
echo.
echo ================================================
echo   ULTIMATE COPILOT OVERNIGHT OPERATION
echo ================================================
echo.
echo This will start the autonomous self-improvement
echo system that will run overnight to enhance the
echo Ultimate Copilot continuously.
echo.
echo The system will:
echo  - Analyze code structure every 10 minutes
echo  - Optimize performance every 15 minutes  
echo  - Improve architecture every 20 minutes
echo  - Log all improvements to logs/
echo.
echo Press Ctrl+C to stop autonomous operation
echo.
pause

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Starting overnight autonomous operation...
echo.
echo Check these files for progress:
echo  - logs/overnight_summary.log
echo  - logs/overnight_operation.log
echo  - logs/agents/orchestrator_autonomous.log
echo  - logs/agents/architect_autonomous.log
echo  - logs/agents/backend_autonomous.log
echo.

REM Run the overnight operation
python run_overnight.py

echo.
echo Overnight operation completed.
echo Check logs/ directory for detailed results.
pause
