@echo off
echo ========================================
echo  ULTIMATE COPILOT - BATCH LAUNCHER
echo ========================================

set PYTHON_EXE=C:\Users\bcmad\OneDrive\Desktop\agentarmycompforbolt\ultimate_copilot\.venv\Scripts\python.exe

echo Testing Python executable...
"%PYTHON_EXE%" --version

echo.
echo Starting Model Manager Backend...
start "Model Manager Backend" cmd /k "%PYTHON_EXE%" "frontend\model manager\backend\server_optimized.py" --port 8002

echo Waiting 5 seconds...
timeout /t 5 /nobreak > nul

echo.
echo Starting Dashboard Backend...
start "Dashboard Backend" cmd /k "%PYTHON_EXE%" "frontend\dashboard_backend_clean.py" --port 8001

echo Waiting 5 seconds...
timeout /t 5 /nobreak > nul

echo.
echo Starting Dashboard Frontend...
start "Dashboard Frontend" cmd /k "%PYTHON_EXE%" -m streamlit run "frontend\dashboard.py" --server.port 8501

echo Waiting 10 seconds...
timeout /t 10 /nobreak > nul

echo.
echo Starting Model Manager Frontend...
cd "frontend\model manager"
start "Model Manager Frontend" cmd /k "..\..\nodejs\npm.cmd" run dev
cd ..\..

echo.
echo ========================================
echo  Services started in separate windows
echo ========================================
echo  Dashboard:         http://localhost:8501
echo  Dashboard API:     http://localhost:8001
echo  Model Manager API: http://localhost:8002
echo  Model Manager UI:  http://localhost:5173
echo ========================================

pause
