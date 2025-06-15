@echo off
REM Advanced vLLM Windows Launcher - Nexus-GUI inspired
REM Place this .bat anywhere on your Windows system and run it

:MENU_LOOP
REM --- Auto-refreshing menu loop ---
cls
:REFRESH_MENU
cls
REM --- Real-time server status ---
echo =============================
echo   vLLM Windows Launcher (Advanced)
echo =============================
echo.
for /f "delims=" %%S in ('wsl bash -c "bash ~/launch_vllm_auto.sh --status"') do set STATUS=%%S
echo %STATUS%
echo.
echo 1. Start vLLM server (select model, advanced options)
echo 2. View running model/process
echo 3. View available models (with size/format)
echo 4. Load/switch model (restart server)
echo 5. Stop server (unload model)
echo 6. Restart server (select model)
echo 7. Tail server log
echo 8. Health check (API ping)
echo 9. Show GPU/CPU/RAM info
echo 10. Open Web UI (if installed)
echo 11. Exit
echo 12. Configure GPU count and vLLM options (global or per-model)
echo 13. View last config/debug log
echo.
echo Press a number (1-12) to select an option, then press Enter...
set /p choice="Select: "
REM --- Handle menu options ---
goto MENU_OPTION

:MENU_OPTION
REM (Copy all existing menu option handlers here, then at the end of each, set choice= and goto MENU_LOOP)

if "%choice%"=="1" goto START_SERVER
if "%choice%"=="2" goto VIEW_RUNNING
if "%choice%"=="3" goto VIEW_MODELS
if "%choice%"=="4" goto LOAD_MODEL
if "%choice%"=="5" goto STOP_SERVER
if "%choice%"=="6" goto RESTART_SERVER
if "%choice%"=="7" goto TAIL_LOG
if "%choice%"=="8" goto HEALTH_CHECK
if "%choice%"=="9" goto SHOW_HW
if "%choice%"=="10" goto OPEN_WEBUI
if "%choice%"=="11" goto EXIT_LAUNCHER
if "%choice%"=="12" goto CONFIGURE_OPTS
if "%choice%"=="13" goto VIEW_LASTLOG

goto MENU

:START_SERVER
echo Start vLLM server.
REM --- Read config for selected model (or global/default) ---
set CONFIG_FILE=%USERPROFILE%\.vllm_launcher_config
set NUM_GPUS=
set CUSTOM_OPTS=
REM Assume model_name is set by previous selection logic (or set to default)
if exist "%CONFIG_FILE%" (
  for /f "tokens=1,2 delims== " %%a in ('findstr /i "%model_name%_NUM_GPUS=" "%CONFIG_FILE%"') do set NUM_GPUS=%%b
  for /f "tokens=1,* delims== " %%a in ('findstr /i "%model_name%_CUSTOM_OPTS=" "%CONFIG_FILE%"') do set CUSTOM_OPTS=%%b
  if "%NUM_GPUS%"=="" for /f "tokens=1,2 delims== " %%a in ('findstr "NUM_GPUS=" "%CONFIG_FILE%"') do set NUM_GPUS=%%b
  if "%CUSTOM_OPTS%"=="" for /f "tokens=1,* delims== " %%a in ('findstr "CUSTOM_OPTS=" "%CONFIG_FILE%"') do set CUSTOM_OPTS=%%b
)
if "%NUM_GPUS%"=="" set NUM_GPUS=1
if "%CUSTOM_OPTS%"=="" set CUSTOM_OPTS=
echo [INFO] Using NUM_GPUS=%NUM_GPUS%, CUSTOM_OPTS=%CUSTOM_OPTS%
REM --- Launch vLLM in WSL with these options ---
REM Pass NUM_GPUS and CUSTOM_OPTS as environment variables using WSLENV for robust cross-WSL transfer
set "WSLENV=NUM_GPUS/u:CUSTOM_OPTS/u"
set "NUM_GPUS=%NUM_GPUS%"
set "CUSTOM_OPTS=%CUSTOM_OPTS%"
wsl bash -c "NUM_GPUS=$NUM_GPUS CUSTOM_OPTS=\"$CUSTOM_OPTS\" bash ~/launch_vllm_auto.sh --model '%model_name%'"
goto MENU_LOOP

:CONFIGURE_MODEL_OPTS
REM --- Persistent debug log marker ---
set LOG_FILE=%USERPROFILE%\.vllm_launcher_lastlog.txt
echo [DEBUG] Entered CONFIGURE_MODEL_OPTS > "%LOG_FILE%"
REM --- Per-model configuration ---
set CONFIG_FILE=%USERPROFILE%\.vllm_launcher_config
REM List available models (names only)
echo Available models:
setlocal enabledelayedexpansion
set idx=0
echo [DEBUG] After entering CONFIGURE_MODEL_OPTS prompt >> "%LOG_FILE%"
for /f "delims=" %%M in ('wsl bash -c "~/launch_vllm_auto.sh --list-models --names-only"') do (
  set /a idx+=1
  set MODEL!idx!=%%~M
  echo   %%M
)
echo [DEBUG] After model list >> "%LOG_FILE%"
endlocal
set /p model_name=Enter model name exactly as shown above: 
echo [DEBUG] After set /p model_name: %model_name% >> "%LOG_FILE%"
set "CONF_PREFIX=%model_name%"
echo [DEBUG] Model selected: %model_name% >> "%LOG_FILE%"
REM Read current values
set NUM_GPUS=
set CUSTOM_OPTS=
if exist "%CONFIG_FILE%" (
  for /f "tokens=1,2 delims== " %%a in ('findstr /i "%CONF_PREFIX%_NUM_GPUS=" "%CONFIG_FILE%"') do set NUM_GPUS=%%b
  for /f "tokens=1,* delims== " %%a in ('findstr /i "%CONF_PREFIX%_CUSTOM_OPTS=" "%CONFIG_FILE%"') do set CUSTOM_OPTS=%%b
)
echo Configuring [%CONF_LABEL%] settings.
set /p NUM_GPUS=Enter number of GPUs [current: %NUM_GPUS%]: 
if "%NUM_GPUS%"=="" set NUM_GPUS=1
:VALIDATE_MODEL_GPU
set /a testgpu=%NUM_GPUS%+0 2>nul
if errorlevel 1 (
  echo Invalid GPU count. Enter a positive integer.
  set /p NUM_GPUS=Enter number of GPUs [current: %NUM_GPUS%]: 
  goto VALIDATE_MODEL_GPU
)
set /p CUSTOM_OPTS=Enter custom vLLM options [current: %CUSTOM_OPTS%]: 
if "%CUSTOM_OPTS%"=="" set CUSTOM_OPTS=
pause
REM Write config
findstr /v /i "%CONF_PREFIX%_NUM_GPUS=" "%CONFIG_FILE%" > "%CONFIG_FILE%.tmp"
findstr /v /i "%CONF_PREFIX%_CUSTOM_OPTS=" "%CONFIG_FILE%.tmp" > "%CONFIG_FILE%.tmp2"
move /y "%CONFIG_FILE%.tmp2" "%CONFIG_FILE%" >nul
echo %CONF_PREFIX%_NUM_GPUS=%NUM_GPUS%>> "%CONFIG_FILE%"
echo %CONF_PREFIX%_CUSTOM_OPTS=%CUSTOM_OPTS%>> "%CONFIG_FILE%"
REM --- Begin persistent debug log block ---
set LOG_FILE=%USERPROFILE%\.vllm_launcher_lastlog.txt
echo [DEBUG] --- BEGIN CONFIG COPY --- > "%LOG_FILE%"
if exist "%CONFIG_FILE%" (
  echo [DEBUG] CONFIG_FILE is: %CONFIG_FILE%>> "%LOG_FILE%"
  setlocal enabledelayedexpansion
  set WSL_CONFIG_FILE=
  for /f %%P in ('wsl wslpath "%CONFIG_FILE%"') do (
    set WSL_CONFIG_FILE=%%P
    echo [DEBUG] WSL_CONFIG_FILE is: !WSL_CONFIG_FILE!>> "%LOG_FILE%"
  )
  endlocal & set WSL_CONFIG_FILE=%WSL_CONFIG_FILE%
  if not defined WSL_CONFIG_FILE (
    echo [ERROR] Could not translate config file path to WSL. Skipping copy.>> "%LOG_FILE%"
  ) else (
    echo [DEBUG] Will run: wsl bash -c "cp %WSL_CONFIG_FILE% ~" >> "%LOG_FILE%"
    wsl bash -c "cp %WSL_CONFIG_FILE% ~" >> "%LOG_FILE%" 2>&1
    echo [DEBUG] WSL cp exit code: %ERRORLEVEL%>> "%LOG_FILE%"
  )
) else (
  echo [ERROR] Config file does not exist: %CONFIG_FILE%>> "%LOG_FILE%"
)
echo [DEBUG] --- END CONFIG COPY --- >> "%LOG_FILE%"
echo See menu option 13 for debug log.
REM --- End persistent debug log block ---
pause

echo.
echo [Options saved for %CONF_LABEL%.]
pause
goto MENU_LOOP

:CONFIGURE_OPTS
REM --- Persistent debug log marker ---
set LOG_FILE=%USERPROFILE%\.vllm_launcher_lastlog.txt
echo [DEBUG] Entered CONFIGURE_OPTS > "%LOG_FILE%"
REM --- Configuration UX: choose global or per-model ---
echo.
echo Configure which settings?
echo   1. Global defaults (used if no per-model setting)
echo   2. Per-model settings
set /p conf_scope=Enter 1 or 2: 
if "%conf_scope%"=="2" goto CONFIGURE_MODEL_OPTS
REM Global config
set CONFIG_FILE=%USERPROFILE%\.vllm_launcher_config
set NUM_GPUS=
set CUSTOM_OPTS=
if exist "%CONFIG_FILE%" (
  for /f "tokens=1,2 delims== " %%a in ('findstr "NUM_GPUS=" "%CONFIG_FILE%"') do set NUM_GPUS=%%b
  for /f "tokens=1,* delims== " %%a in ('findstr "CUSTOM_OPTS=" "%CONFIG_FILE%"') do set CUSTOM_OPTS=%%b
)
echo Configuring [Global] settings.
set /p NUM_GPUS=Enter number of GPUs [current: %NUM_GPUS%]: 
if "%NUM_GPUS%"=="" set NUM_GPUS=1
:VALIDATE_GLOBAL_GPU
set /a testgpu=%NUM_GPUS%+0 2>nul
if errorlevel 1 (
  echo Invalid GPU count. Enter a positive integer.
  set /p NUM_GPUS=Enter number of GPUs [current: %NUM_GPUS%]: 
  goto VALIDATE_GLOBAL_GPU
)
set /p CUSTOM_OPTS=Enter custom vLLM options [current: %CUSTOM_OPTS%]: 
if "%CUSTOM_OPTS%"=="" set CUSTOM_OPTS=
echo NUM_GPUS=%NUM_GPUS%> "%CONFIG_FILE%"
echo CUSTOM_OPTS=%CUSTOM_OPTS%>> "%CONFIG_FILE%"
wsl bash -c "cp /mnt/c/Users/$(wslvar USERNAME)/.vllm_launcher_config ~"
echo.
echo [Global options saved.]
timeout /t 1 >nul
goto MENU_LOOP

:VIEW_RUNNING
echo Checking running vLLM process and model...
wsl bash -c "ps aux | grep vllm.entrypoints.openai.api_server | grep -v grep || echo 'No vLLM server running.'"
echo.
echo (Check the log for the model path: ~/vllm_server.log)
pause
set choice=
goto MENU_LOOP

:VIEW_MODELS
echo Available vLLM-loadable models in WSL:
wsl bash -c "bash -c 'source ~/anaconda3/etc/profile.d/conda.sh; conda activate vllm; bash ~/launch_vllm_auto.sh --list-models'"
echo.
set /p selectmodel="Would you like to load a model now? (y/n): "
if /I "%selectmodel%"=="y" wsl bash -c "bash ~/launch_vllm_auto.sh"
set choice=
goto MENU_LOOP

:LOAD_MODEL
echo You are about to switch the model (restart server).
set /p loadmodel="Would you like to load a model now? (y/n): "
if /I "%loadmodel%"=="y" wsl bash -c "bash ~/stop_vllm.sh; bash ~/launch_vllm_auto.sh"
pause
set choice=
goto MENU_LOOP

:STOP_SERVER
echo Stopping vLLM server...
wsl bash -c "bash ~/stop_vllm.sh"
pause
set choice=
goto MENU_LOOP

:RESTART_SERVER
echo Restart vLLM server.
set /p loadmodel="Would you like to load a model now? (y/n): "
if /I "%loadmodel%"=="y" wsl bash -c "bash ~/stop_vllm.sh; bash ~/launch_vllm_auto.sh"
pause
set choice=
goto MENU_LOOP

:TAIL_LOG
echo Last 40 lines of vLLM log:
wsl bash -c "tail -40 ~/vllm_server.log"
pause
set choice=
goto MENU_LOOP

:HEALTH_CHECK
echo Pinging vLLM API at http://localhost:8000/v1/models ...
wsl bash -c "curl -s http://localhost:8000/v1/models || echo 'No response - server may be down.'"
pause
set choice=
goto MENU_LOOP

:SHOW_HW
echo GPU/CPU/RAM info:
wsl bash -c "bash -c 'source ~/anaconda3/etc/profile.d/conda.sh; conda activate vllm; bash ~/launch_vllm_auto.sh --hw-info'"
pause
set choice=
goto MENU_LOOP

:VIEW_LASTLOG
REM --- View the last config/debug log ---
echo Last config/debug log:
type "%USERPROFILE%\.vllm_launcher_lastlog.txt"
pause
goto MENU_LOOP

:OPEN_WEBUI
echo Attempting to open Web UI at http://localhost:3000 ...
start http://localhost:3000
pause
set choice=
goto MENU_LOOP
