@echo off
echo Testing port detection...
python test_port_detection.py
echo.
echo Starting Model Manager Backend with auto port detection...
python "frontend/model manager/backend/server.py" --host 127.0.0.1 --port 8080
pause
