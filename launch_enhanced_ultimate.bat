@echo off
title Ultimate Copilot - Enhanced Launcher
color 0A

echo.
echo ========================================
echo  ULTIMATE COPILOT - ENHANCED LAUNCHER
echo ========================================
echo.

echo Starting Ultimate Copilot with enhanced Model Manager integration...
echo.

:: Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python first.
    pause
    exit /b 1
)

:: Change to the script directory
cd /d "%~dp0"

:: Launch the enhanced launcher
echo Launching enhanced system...
python launch_enhanced_ultimate.py

:: If the script exits, pause to show any error messages
if errorlevel 1 (
    echo.
    echo Script ended with error code %errorlevel%
    echo.
    pause
)

exit /b %errorlevel%
