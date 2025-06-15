@echo off
setlocal

:: Stop Ollama silently
taskkill /IM ollama.exe /F >nul 2>&1

:: Verify process stopped
timeout /t 2 >nul
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I /N "ollama.exe" >nul
if "%ERRORLEVEL%"=="1" (
  echo {"status":"success"}
) else (
  echo {"status":"error","message":"Failed to stop Ollama"}
)

exit /b %ERRORLEVEL%
