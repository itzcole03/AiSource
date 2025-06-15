@echo off
echo ========================================
echo Ultimate Copilot Dashboard Launcher
echo ========================================
echo.

echo [1/4] Starting Model Manager Backend...
cd "frontend\model manager\backend"
start "Model Manager Backend" python server.py --host 127.0.0.1 --port 8080
cd ..\..\..
timeout /t 3

echo [2/4] Starting Model Manager Frontend...
cd "frontend\model manager"
start "Model Manager Frontend" npm run dev
cd ..\..
timeout /t 5

echo [3/4] Starting Dashboard Backend...
cd frontend
start "Dashboard Backend" python dashboard_backend_clean.py
cd ..
timeout /t 3

echo [4/4] Starting Dashboard Frontend...
cd frontend
start "Dashboard Frontend" streamlit run dashboard.py --server.port 8501
cd ..

echo.
echo ========================================
echo All components starting...
echo ========================================
echo.
echo Access Points:
echo   Dashboard:              http://localhost:8501
echo   Model Manager:          http://localhost:5173
echo   Model Manager Backend:  http://localhost:8080
echo   Dashboard Backend:      http://localhost:8001
echo.
echo Press any key to close this launcher...
pause > nul
