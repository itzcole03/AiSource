@echo off
cls
echo.
echo ================================================
echo   ULTIMATE COPILOT - GET UNSTUCK HELPER
echo ================================================
echo.
echo This script will help diagnose and fix common issues
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo [1/5] Checking Python environment...
python -c "import sys; print(f'Python {sys.version}')"

echo.
echo [2/5] Checking workspace structure...
if not exist "core" (
    echo ERROR: Missing core directory
    echo Please ensure you're in the Ultimate Copilot project root
    pause
    exit /b 1
)

echo Core directory: OK
echo Agents directory: %cd%\agents
echo Logs directory: %cd%\logs

echo.
echo [3/5] Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "logs\agents" mkdir logs\agents
echo Directories created successfully

echo.
echo [4/5] Running quick agent test...
python -c "
import sys
import os
sys.path.insert(0, '.')
try:
    from core.simple_agents import SimpleOrchestratorAgent
    print('Agent imports: OK')
except Exception as e:
    print(f'Agent import error: {e}')
    sys.exit(1)
"

if errorlevel 1 (
    echo ERROR: Agent import failed
    echo Check the error message above
    pause
    exit /b 1
)

echo.
echo [5/5] Testing autonomous operation...
echo Running 30-second test...
timeout /t 2 /nobreak >nul

python -c "
import asyncio
import sys
import os
sys.path.insert(0, '.')

async def quick_test():
    try:
        from core.simple_agents import SimpleOrchestratorAgent
        agent = SimpleOrchestratorAgent()
        await agent.agent_initialize()
        
        task = {'type': 'quick_test', 'workspace': os.getcwd()}
        result = await agent.process_task(task, {})
        
        print(f'Quick test result: {result[\"status\"]}')
        return True
    except Exception as e:
        print(f'Quick test failed: {e}')
        return False

result = asyncio.run(quick_test())
sys.exit(0 if result else 1)
"

if errorlevel 1 (
    echo.
    echo WARNING: Quick test had issues, but system may still work
    echo Check logs\agents\ directory for details
) else (
    echo.
    echo SUCCESS: All systems operational!
)

echo.
echo ================================================
echo   DIAGNOSIS COMPLETE
echo ================================================
echo.
echo OPTIONS:
echo [1] Run demo mode (safe testing)
echo [2] Run overnight autonomous operation
echo [3] View recent logs
echo [4] Exit
echo.
set /p choice="Choose option (1-4): "

if "%choice%"=="1" (
    echo Starting demo mode...
    python demo.py
) else if "%choice%"=="2" (
    echo Starting overnight operation...
    python run_overnight.py
) else if "%choice%"=="3" (
    echo.
    echo Recent logs:
    if exist "logs\overnight_operation.log" (
        echo --- Overnight Operation Log (last 10 lines) ---
        powershell "Get-Content logs\overnight_operation.log | Select-Object -Last 10"
    )
    echo.
    if exist "logs\agents\orchestrator_work.log" (
        echo --- Orchestrator Log (last 5 lines) ---
        powershell "Get-Content logs\agents\orchestrator_work.log | Select-Object -Last 5"
    )
    pause
) else (
    echo Exiting...
)

echo.
echo Done.
pause
