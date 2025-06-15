@echo off
title Ultimate Copilot - Integration Tests
color 0B

echo.
echo =============================================
echo  ULTIMATE COPILOT - INTEGRATION TEST SUITE
echo =============================================
echo.

echo Running comprehensive integration tests...
echo This will test all components and integrations.
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

:: Run the comprehensive test
echo Starting test suite...
python comprehensive_integration_test.py

:: Show results
echo.
echo =============================================
echo  TEST SUITE COMPLETED
echo =============================================
echo.

:: Pause to show results
pause

exit /b %errorlevel%
