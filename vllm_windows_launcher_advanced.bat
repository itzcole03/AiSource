@echo off
REM Advanced vLLM Windows Launcher - Nexus-GUI inspired
REM Place this .bat anywhere on your Windows system and run it

:MENU
cls
REM --- Real-time server status ---
echo =============================
echo   vLLM Windows Launcher (Advanced)
echo =============================
echo.
for /f "delims=" %%S in ('wsl bash -c "bash -c 'source ~/anaconda3/etc/profile.d/conda.sh; conda activate vllm; bash ~/launch_vllm_auto.sh --status'"') do set STATUS=%%S
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
echo.
set /p choice="Select an option (1-11): "

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
if "%choice%"=="11" exit

goto MENU

:START_SERVER
echo Start vLLM server.
set /p loadmodel="Would you like to load a model now? (y/n): "
if /I "%loadmodel%"=="y" wsl bash -c "bash ~/launch_vllm_auto.sh"
pause
goto MENU

:VIEW_RUNNING
echo Checking running vLLM process and model...
wsl bash -c "ps aux | grep vllm.entrypoints.openai.api_server | grep -v grep || echo 'No vLLM server running.'"
echo.
echo (Check the log for the model path: ~/vllm_server.log)
pause
goto MENU

:VIEW_MODELS
echo Available vLLM-loadable models in WSL:
wsl bash -c "bash -c 'source ~/anaconda3/etc/profile.d/conda.sh; conda activate vllm; bash ~/launch_vllm_auto.sh --list-models'"
echo.
set /p selectmodel="Would you like to load a model now? (y/n): "
if /I "%selectmodel%"=="y" wsl bash -c "bash ~/launch_vllm_auto.sh"
goto MENU

:LOAD_MODEL
echo You are about to switch the model (restart server).
set /p loadmodel="Would you like to load a model now? (y/n): "
if /I "%loadmodel%"=="y" wsl bash -c "bash ~/stop_vllm.sh; bash ~/launch_vllm_auto.sh"
pause
goto MENU

:STOP_SERVER
echo Stopping vLLM server...
wsl bash -c "bash ~/stop_vllm.sh"
pause
goto MENU

:RESTART_SERVER
echo Restart vLLM server.
set /p loadmodel="Would you like to load a model now? (y/n): "
if /I "%loadmodel%"=="y" wsl bash -c "bash ~/stop_vllm.sh; bash ~/launch_vllm_auto.sh"
pause
goto MENU

:TAIL_LOG
echo Last 40 lines of vLLM log:
wsl bash -c "tail -40 ~/vllm_server.log"
pause
goto MENU

:HEALTH_CHECK
echo Pinging vLLM API at http://localhost:8000/v1/models ...
wsl bash -c "curl -s http://localhost:8000/v1/models || echo 'No response - server may be down.'"
pause
goto MENU

:SHOW_HW
echo GPU/CPU/RAM info:
wsl bash -c "bash -c 'source ~/anaconda3/etc/profile.d/conda.sh; conda activate vllm; bash ~/launch_vllm_auto.sh --hw-info'"
pause
goto MENU

:OPEN_WEBUI
echo Attempting to open Web UI at http://localhost:3000 ...
start http://localhost:3000
pause
goto MENU
