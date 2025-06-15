@echo off
echo Starting Model Manager Backend...
cd /d "C:\Users\bcmad\OneDrive\Desktop\agentarmycompforbolt\ultimate_copilot"
.venv\Scripts\python.exe "frontend\model manager\backend\server_optimized.py" --port 8002
pause
