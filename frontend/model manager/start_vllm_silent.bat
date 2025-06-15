@echo off
setlocal

:: Run VLLM silently in WSL background
wsl -d Ubuntu -u root -- bash -c "nohup /usr/local/bin/launch_vllm_auto.sh > /tmp/vllm_start.log 2>&1 &"

:: Verify process started
timeout /t 10 >nul
wsl -d Ubuntu -u root -- bash -c "pgrep -f 'launch_vllm_auto.sh'" >nul
if "%ERRORLEVEL%"=="0" (
  echo {"status":"success"}
) else (
  echo {"status":"error","message":"Failed to start VLLM"}
)

exit /b %ERRORLEVEL%
