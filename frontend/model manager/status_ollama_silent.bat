@echo off
REM status_ollama_silent.bat
REM Checks if Ollama server is running
findstr /i "ollama.exe" <(tasklist) >nul 2>&1
if %errorlevel%==0 (
  echo Ollama server is running.
  exit /b 0
) else (
  echo Ollama server is NOT running.
  exit /b 1
)
