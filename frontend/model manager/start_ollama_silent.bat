@echo off
setlocal

:: Run Ollama silently in background with logging
start /B "" "C:\Program Files\Ollama\ollama.exe" serve > "%TEMP%\ollama_start.log" 2>&1

:: Verify process started
timeout /t 5 >nul
tasklist /FI "IMAGENAME eq ollama.exe" 2>nul | find /I /N "ollama.exe" >nul
if "%ERRORLEVEL%"=="0" (
  echo {"status":"success","pid":%ERRORLEVEL%}
) else (
  echo {"status":"error","message":"Failed to start Ollama"}
)

exit /b %ERRORLEVEL%
