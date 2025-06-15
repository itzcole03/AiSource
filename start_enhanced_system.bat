@echo off
cls
title Ultimate Copilot - Enhanced System Launcher
color 0a

:main_menu
cls
echo.
echo ===============================================
echo   ULTIMATE COPILOT - ENHANCED SYSTEM LAUNCHER
echo ===============================================
echo.
echo 🚀 Enhanced Agent System with Memory & Context
echo 🌐 Multiple Dashboard Interfaces Available
echo 🔧 Auto-Dependency Management
echo ⚡ Production-Ready with Fallbacks
echo.
echo ===============================================
echo   SELECT STARTUP OPTION:
echo ===============================================
echo.
echo   1. Quick Start - Universal Launcher (Recommended)
echo   2. Full System - All Services
echo   3. API Server Only
echo   4. Console Dashboard Only
echo   5. GUI Dashboard Only
echo   6. Enhanced GUI Dashboard (v2)
echo   7. Web Interface Setup
echo   7. Development Mode (All + Logs)
echo   8. System Status Check
echo   9. Install/Update Dependencies
echo   0. Exit
echo.
echo ===============================================

set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto quick_start
if "%choice%"=="2" goto full_system
if "%choice%"=="3" goto api_only
if "%choice%"=="4" goto console_only
if "%choice%"=="5" goto gui_only
if "%choice%"=="6" goto web_setup
if "%choice%"=="7" goto dev_mode
if "%choice%"=="8" goto status_check
if "%choice%"=="9" goto install_deps
if "%choice%"=="0" goto exit
goto main_menu

:quick_start
cls
echo.
echo ===============================================
echo   QUICK START - UNIVERSAL LAUNCHER
echo ===============================================
echo.
echo Starting the Universal Dashboard Launcher...
echo This provides an interactive menu for all options.
echo.
python universal_dashboard_launcher.py
pause
goto main_menu

:full_system
cls
echo.
echo ===============================================
echo   FULL SYSTEM STARTUP
echo ===============================================
echo.
echo Starting all services in separate windows...
echo.

echo 1/4 - Starting API Server...
start "Ultimate Copilot API" cmd /c "python -c \"import uvicorn; from enhanced_dashboard_api import EnhancedDashboardAPI; api = EnhancedDashboardAPI(); uvicorn.run(api.app, host='127.0.0.1', port=8001)\" & pause"

timeout /t 3 /nobreak >nul

echo 2/4 - Starting Console Dashboard...
start "Ultimate Copilot Console" cmd /c "python enhanced_dashboard_integration.py & pause"

timeout /t 2 /nobreak >nul

echo 3/4 - Starting GUI Dashboard...
start "Ultimate Copilot GUI" cmd /c "python consolidated_dashboard.py & pause"

timeout /t 2 /nobreak >nul

echo 4/4 - Opening Web Interface...
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:8001/docs"

echo.
echo ✅ All services started successfully!
echo.
echo Available interfaces:
echo   • API Documentation: http://127.0.0.1:8001/docs
echo   • Web Dashboard: enhanced_dashboard.html
echo   • Console Dashboard: Running in separate window
echo   • GUI Dashboard: Running in separate window
echo.
pause
goto main_menu

:api_only
cls
echo.
echo ===============================================
echo   API SERVER ONLY
echo ===============================================
echo.
echo Starting Enhanced Dashboard API server...
echo Server will be available at: http://127.0.0.1:8001
echo.
python -c "import uvicorn; from enhanced_dashboard_api import EnhancedDashboardAPI; api = EnhancedDashboardAPI(); uvicorn.run(api.app, host='127.0.0.1', port=8001)"
pause
goto main_menu

:console_only
cls
echo.
echo ===============================================
echo   CONSOLE DASHBOARD ONLY
echo ===============================================
echo.
echo Starting Enhanced Console Dashboard...
echo.
python enhanced_dashboard_integration.py
pause
goto main_menu

:gui_only
cls
echo.
echo ===============================================
echo   GUI DASHBOARD ONLY
echo ===============================================
echo.
echo Starting Consolidated GUI Dashboard...
echo.
python consolidated_dashboard.py
pause
goto main_menu

:web_setup
cls
echo.
echo ===============================================
echo   WEB INTERFACE SETUP
echo ===============================================
echo.
echo Setting up web interface...
echo.

echo 1/2 - Starting API Server in background...
start "Ultimate Copilot API" cmd /c "python -c \"import uvicorn; from enhanced_dashboard_api import EnhancedDashboardAPI; api = EnhancedDashboardAPI(); uvicorn.run(api.app, host='127.0.0.1', port=8001)\" & pause"

echo Waiting for server to start...
timeout /t 5 /nobreak >nul

echo 2/2 - Opening web interfaces...
start "" "http://127.0.0.1:8001/docs"
start "" "%~dp0enhanced_dashboard.html"

echo.
echo ✅ Web interface setup complete!
echo.
echo Available URLs:
echo   • API Documentation: http://127.0.0.1:8001/docs
echo   • Enhanced Dashboard: enhanced_dashboard.html
echo   • API Endpoints: http://127.0.0.1:8001/
echo.
pause
goto main_menu

:dev_mode
cls
echo.
echo ===============================================
echo   DEVELOPMENT MODE
echo ===============================================
echo.
echo Starting all services with verbose logging...
echo.

echo 1/5 - Starting API Server with logs...
start "API Server Logs" cmd /c "python enhanced_dashboard_api.py & pause"

timeout /t 3 /nobreak >nul

echo 2/5 - Starting Console Dashboard...
start "Console Dashboard" cmd /c "python enhanced_dashboard_integration.py & pause"

timeout /t 2 /nobreak >nul

echo 3/5 - Starting GUI Dashboard...
start "GUI Dashboard" cmd /c "python consolidated_dashboard.py & pause"

timeout /t 2 /nobreak >nul

echo 4/5 - Starting Universal Launcher...
start "Universal Launcher" cmd /c "python universal_dashboard_launcher.py & pause"

timeout /t 2 /nobreak >nul

echo 5/5 - Running system tests...
start "System Tests" cmd /c "python test_dashboard_integration_complete.py & pause"

echo.
echo ✅ Development mode active!
echo All services started with logging enabled.
echo.
pause
goto main_menu

:status_check
cls
echo.
echo ===============================================
echo   SYSTEM STATUS CHECK
echo ===============================================
echo.
echo Checking system status and dependencies...
echo.

python -c "
import sys
import subprocess
import importlib

print('🐍 Python Version:', sys.version)
print()

# Check required packages
packages = ['fastapi', 'uvicorn', 'pydantic', 'requests', 'tkinter']
print('📦 Package Status:')
for pkg in packages:
    try:
        if pkg == 'tkinter':
            import tkinter
        else:
            importlib.import_module(pkg)
        print(f'  ✅ {pkg} - Available')
    except ImportError:
        print(f'  ❌ {pkg} - Missing')

print()

# Check key files
import os
files = [
    'enhanced_dashboard_api.py',
    'enhanced_dashboard_integration.py', 
    'consolidated_dashboard.py',
    'universal_dashboard_launcher.py',
    'enhanced_dashboard.html',
    'run_swarm.py'
]
print('📁 Key Files:')
for file in files:
    if os.path.exists(file):
        print(f'  ✅ {file} - Present')
    else:
        print(f'  ❌ {file} - Missing')

print()
print('🔧 System Status Check Complete')
"

echo.
pause
goto main_menu

:install_deps
cls
echo.
echo ===============================================
echo   INSTALL/UPDATE DEPENDENCIES
echo ===============================================
echo.
echo Installing and updating required dependencies...
echo.

echo 1/3 - Updating pip...
python -m pip install --upgrade pip

echo.
echo 2/3 - Installing from requirements-dashboard.txt...
if exist "requirements-dashboard.txt" (
    python -m pip install -r requirements-dashboard.txt
) else (
    echo Installing core dependencies manually...
    python -m pip install fastapi uvicorn pydantic requests
)

echo.
echo 3/3 - Installing optional dependencies...
python -m pip install streamlit pandas matplotlib plotly --quiet

echo.
echo ✅ Dependency installation complete!
echo.
pause
goto main_menu

:exit
cls
echo.
echo ===============================================
echo   THANK YOU FOR USING ULTIMATE COPILOT!
echo ===============================================
echo.
echo Enhanced system is ready for use.
echo Run this script anytime to access all features.
echo.
echo Visit the following for more information:
echo   • Console Dashboard: python enhanced_dashboard_integration.py
echo   • API Server: python enhanced_dashboard_api.py
echo   • Universal Launcher: python universal_dashboard_launcher.py
echo.
timeout /t 3 /nobreak >nul
exit /b 0
