@echo off
title Ultimate Copilot - Start Everything
color 0a

cls
echo.
echo ===============================================
echo   ULTIMATE COPILOT - START EVERYTHING
echo ===============================================
echo.
echo 🚀 Starting all services automatically...
echo.

REM Check if we're in the right directory
if not exist "enhanced_dashboard_api.py" (
    echo ❌ Error: Please run from the Ultimate Copilot directory
    echo Current directory: %CD%
    pause
    exit /b 1
)

echo ✅ Directory check passed
echo.

REM Quick dependency check and install if needed
echo 📦 Checking dependencies...
python -c "import fastapi, uvicorn, pydantic, requests" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    python -m pip install fastapi uvicorn pydantic requests --quiet
    echo ✅ Dependencies installed
) else (
    echo ✅ Dependencies OK
)
echo.

echo 🚀 Starting services...
echo.

echo 1/4 - API Server (port 8001)...
start "Ultimate Copilot API" /min cmd /c "python -c \"import uvicorn; from enhanced_dashboard_api import EnhancedDashboardAPI; api = EnhancedDashboardAPI(); uvicorn.run(api.app, host='127.0.0.1', port=8001)\" || pause"

timeout /t 3 /nobreak >nul

echo 2/4 - Console Dashboard...
start "Ultimate Copilot Console" cmd /c "python enhanced_dashboard_integration.py || pause"

timeout /t 2 /nobreak >nul

echo 3/4 - GUI Dashboard...
start "Ultimate Copilot GUI" cmd /c "python consolidated_dashboard.py || pause"

timeout /t 2 /nobreak >nul

echo 4/4 - Universal Launcher...
start "Ultimate Copilot Launcher" cmd /c "python universal_dashboard_launcher.py || pause"

echo.
echo ⏳ Waiting for services to initialize...
timeout /t 5 /nobreak >nul

echo.
echo 🌐 Opening web interfaces...
start "" "http://127.0.0.1:8001/docs"
timeout /t 2 /nobreak >nul
start "" "%~dp0enhanced_dashboard.html"

echo.
echo ===============================================
echo   🎉 ALL SERVICES STARTED SUCCESSFULLY!
echo ===============================================
echo.
echo Available interfaces:
echo   📊 API Documentation: http://127.0.0.1:8001/docs
echo   🌐 Web Dashboard: enhanced_dashboard.html  
echo   💻 Console Dashboard: Running in window
echo   🖥️  GUI Dashboard: Running in window
echo   🚀 Universal Launcher: Running in window
echo.
echo Services are running in separate windows.
echo Close this window or press any key to continue.
echo.
pause >nul

cls
echo.
echo ===============================================
echo   ULTIMATE COPILOT SYSTEM STATUS
echo ===============================================
echo.
echo All services should now be running.
echo.
echo Quick actions:
echo   • Press 'R' to restart all services
echo   • Press 'S' to check system status  
echo   • Press 'D' to open developer tools
echo   • Press 'Q' to quit
echo.

:action_menu
set /p action="Enter action (R/S/D/Q): "

if /i "%action%"=="R" (
    echo Restarting services...
    goto restart_services
)
if /i "%action%"=="S" (
    echo Checking system status...
    goto status_check
)
if /i "%action%"=="D" (
    start "" "developer_tools.bat"
    goto action_menu
)
if /i "%action%"=="Q" (
    goto quit
)
goto action_menu

:restart_services
cls
echo.
echo ♻️  Restarting all services...
echo.
taskkill /f /fi "WindowTitle eq Ultimate Copilot*" >nul 2>&1
timeout /t 2 /nobreak >nul
goto start_services

:status_check
cls
echo.
echo 🔍 System Status Check...
echo.
python -c "
import requests
import psutil
import os

print('🌐 Service Status:')
try:
    response = requests.get('http://127.0.0.1:8001/health', timeout=3)
    print(f'  ✅ API Server: Running (Status {response.status_code})')
except:
    print('  ❌ API Server: Not responding')

print()
print('💻 System Resources:')
print(f'  CPU Usage: {psutil.cpu_percent()}%%')
print(f'  Memory Usage: {psutil.virtual_memory().percent}%%')

print()
print('🪟 Active Windows:')
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if 'python' in proc.info['name'].lower() and any('dashboard' in str(cmd).lower() for cmd in proc.info['cmdline'] or []):
            print(f'  🐍 {proc.info[\"name\"]} (PID: {proc.info[\"pid\"]})')
    except:
        pass
"
echo.
pause
goto action_menu

:quit
echo.
echo Thank you for using Ultimate Copilot!
echo Services will continue running in background windows.
echo.
timeout /t 2 /nobreak >nul
exit /b 0
