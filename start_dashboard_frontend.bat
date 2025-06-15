@echo off
echo Starting Dashboard Frontend...
cd /d "C:\Users\bcmad\OneDrive\Desktop\agentarmycompforbolt\ultimate_copilot"
.venv\Scripts\python.exe -m streamlit run "frontend\dashboard.py" --server.port 8501
pause
