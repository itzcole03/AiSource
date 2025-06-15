@echo off
setlocal

:: Forcefully terminate all LM Studio processes
taskkill /IM lm-studio.exe /F /T >nul 2>&1

:: Verify process stopped - wait longer and check multiple times
timeout /t 3 >nul
tasklist /FI "IMAGENAME eq lm-studio.exe" 2>nul | find /I /N "lm-studio.exe" >nul
if "%ERRORLEVEL%"=="1" (
  echo {"status":"success"}
) else (
  :: If still running, try alternative kill method
  wmic process where "name='lm-studio.exe'" delete >nul 2>&1
  timeout /t 2 >nul
  tasklist /FI "IMAGENAME eq lm-studio.exe" 2>nul | find /I /N "lm-studio.exe" >nul
  if "%ERRORLEVEL%"=="1" (
    echo {"status":"success"}
  ) else (
    echo {"status":"error","message":"Failed to stop LM Studio"}
  )
)

exit /b %ERRORLEVEL%
