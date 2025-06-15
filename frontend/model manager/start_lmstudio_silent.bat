@echo off
setlocal

:: Run LM Studio from AppData location
start /B "" "%LOCALAPPDATA%\Programs\LM Studio\lm-studio.exe" --silent > "%TEMP%\lmstudio_start.log" 2>&1

:: Verify process started
timeout /t 5 >nul
tasklist /FI "IMAGENAME eq lm-studio.exe" 2>nul | find /I /N "lm-studio.exe" >nul
if "%ERRORLEVEL%"=="0" (
  echo {"status":"success","pid":%ERRORLEVEL%}
) else (
  echo {"status":"error","message":"Failed to start LM Studio"}
)

exit /b %ERRORLEVEL%
