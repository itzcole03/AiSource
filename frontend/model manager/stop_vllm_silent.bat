@echo off
setlocal

:: Stop VLLM in WSL
wsl -d Ubuntu -u root -- bash -c "pkill -f 'launch_vllm_auto.sh'" >nul 2>&1

:: Verify process stopped
timeout /t 5 >nul
wsl -d Ubuntu -u root -- bash -c "pgrep -f 'launch_vllm_auto.sh'" >nul
if "%ERRORLEVEL%"=="1" (
  echo {"status":"success"}
) else (
  echo {"status":"error","message":"Failed to stop VLLM"}
)

exit /b %ERRORLEVEL%
