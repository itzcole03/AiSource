@echo off
setlocal

:: Check if LM Studio process is running
tasklist /FI "IMAGENAME eq lm-studio.exe" 2>nul | find /I /N "lm-studio.exe" >nul
if "%ERRORLEVEL%"=="0" (
  :: Verify executable path matches expected location
  wmic process where "name='lm-studio.exe'" get ExecutablePath | find "%LOCALAPPDATA%\Programs\LM Studio" >nul
  if "%ERRORLEVEL%"=="0" (
    echo {"status":"success","running":true}
  ) else (
    echo {"status":"success","running":false}
  )
) else (
  echo {"status":"success","running":false}
)

exit /b %ERRORLEVEL%
