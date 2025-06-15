@echo off
title Ultimate Copilot - Developer Tools
color 0c

:dev_menu
cls
echo.
echo ===============================================
echo   ULTIMATE COPILOT - DEVELOPER TOOLS
echo ===============================================
echo.
echo 🔧 Development & Testing Tools
echo 🐛 Debugging & Diagnostics
echo 📊 Performance Monitoring
echo 🧪 Integration Testing
echo.
echo ===============================================
echo   DEVELOPER OPTIONS:
echo ===============================================
echo.
echo   1. Start All Services (Dev Mode)
echo   2. Run Integration Tests
echo   3. Check System Health
echo   4. View Logs & Diagnostics
echo   5. Performance Test
echo   6. Reset System State
echo   7. Dependency Analysis
echo   8. Code Quality Check
echo   9. Backup Current State
echo   0. Exit to Main Launcher
echo.
echo ===============================================

set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto dev_services
if "%choice%"=="2" goto integration_tests
if "%choice%"=="3" goto health_check
if "%choice%"=="4" goto view_logs
if "%choice%"=="5" goto performance_test
if "%choice%"=="6" goto reset_state
if "%choice%"=="7" goto dep_analysis
if "%choice%"=="8" goto quality_check
if "%choice%"=="9" goto backup_state
if "%choice%"=="0" goto main_launcher
goto dev_menu

:dev_services
cls
echo.
echo ===============================================
echo   STARTING DEVELOPMENT ENVIRONMENT
echo ===============================================
echo.

echo 1/6 - Starting API with debug mode...
start "API Debug" cmd /c "python -c \"import uvicorn; from enhanced_dashboard_api import EnhancedDashboardAPI; api = EnhancedDashboardAPI(); uvicorn.run(api.app, host='127.0.0.1', port=8001, reload=True, log_level='debug')\" & pause"

timeout /t 3 /nobreak >nul

echo 2/6 - Starting Console Dashboard...
start "Console Debug" cmd /c "python enhanced_dashboard_integration.py & pause"

timeout /t 2 /nobreak >nul

echo 3/6 - Starting GUI Dashboard...
start "GUI Debug" cmd /c "python consolidated_dashboard.py & pause"

timeout /t 2 /nobreak >nul

echo 4/6 - Starting System Monitor...
start "System Monitor" cmd /c "python -c \"
import time
import psutil
import requests
while True:
    try:
        # Check API health
        response = requests.get('http://127.0.0.1:8001/health', timeout=1)
        api_status = '✅' if response.status_code == 200 else '❌'
    except:
        api_status = '❌'
    
    # System stats
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    
    print(f'API: {api_status} | CPU: {cpu:.1f}%% | RAM: {mem:.1f}%%')
    time.sleep(5)
\" & pause"

timeout /t 2 /nobreak >nul

echo 5/6 - Starting Log Monitor...
start "Log Monitor" cmd /c "python -c \"
import os
import time
log_files = ['enhanced_agent_activity.log', 'system.log', 'error.log']
print('📋 Log Monitor Active')
print('Watching for log updates...')
while True:
    for log_file in log_files:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                if lines:
                    print(f'[{log_file}] {lines[-1].strip()}')
    time.sleep(2)
\" & pause"

timeout /t 2 /nobreak >nul

echo 6/6 - Opening development URLs...
start "" "http://127.0.0.1:8001/docs"
start "" "http://127.0.0.1:8001/health"

echo.
echo ✅ Development environment started!
echo.
pause
goto dev_menu

:integration_tests
cls
echo.
echo ===============================================
echo   RUNNING INTEGRATION TESTS
echo ===============================================
echo.

echo Running comprehensive integration tests...
echo.

if exist "test_dashboard_integration_complete.py" (
    python test_dashboard_integration_complete.py
) else (
    echo ❌ Integration test file not found
)

echo.
if exist "test_fixes_validation.py" (
    echo Running fix validation tests...
    python test_fixes_validation.py
) else (
    echo ❌ Fix validation test file not found
)

echo.
pause
goto dev_menu

:health_check
cls
echo.
echo ===============================================
echo   SYSTEM HEALTH CHECK
echo ===============================================
echo.

python -c "
import os
import sys
import importlib
import psutil
import json
from pathlib import Path

print('🏥 SYSTEM HEALTH REPORT')
print('=' * 50)

# Python environment
print(f'🐍 Python: {sys.version.split()[0]}')
print(f'📁 Working Directory: {os.getcwd()}')
print()

# System resources
print('💻 SYSTEM RESOURCES:')
print(f'  CPU Usage: {psutil.cpu_percent()}%%')
print(f'  Memory Usage: {psutil.virtual_memory().percent}%%')
print(f'  Disk Usage: {psutil.disk_usage(\".\").percent}%%')
print()

# Dependencies
print('📦 DEPENDENCIES:')
deps = ['fastapi', 'uvicorn', 'pydantic', 'requests', 'tkinter']
for dep in deps:
    try:
        if dep == 'tkinter':
            import tkinter
        else:
            importlib.import_module(dep)
        print(f'  ✅ {dep}')
    except ImportError:
        print(f'  ❌ {dep}')
print()

# Key files
print('📂 KEY FILES:')
files = [
    'enhanced_dashboard_api.py',
    'enhanced_dashboard_integration.py',
    'consolidated_dashboard.py',
    'universal_dashboard_launcher.py',
    'run_swarm.py'
]
for file in files:
    status = '✅' if Path(file).exists() else '❌'
    print(f'  {status} {file}')
print()

# Configuration files
print('⚙️ CONFIGURATION:')
configs = [
    'prompt_profiles/agent_prompt_profiles.json',
    'data/memory/agent_memory.json',
    'requirements-dashboard.txt'
]
for config in configs:
    status = '✅' if Path(config).exists() else '❌'
    print(f'  {status} {config}')

print()
print('🏥 Health check complete!')
"

echo.
pause
goto dev_menu

:view_logs
cls
echo.
echo ===============================================
echo   LOG VIEWER
echo ===============================================
echo.

echo Available log files:
echo.

if exist "enhanced_agent_activity.log" (
    echo 📋 Enhanced Agent Activity Log:
    echo ----------------------------------------
    type enhanced_agent_activity.log | more
    echo.
)

if exist "system.log" (
    echo 📋 System Log:
    echo ----------------------------------------
    type system.log | more
    echo.
)

if exist "error.log" (
    echo 📋 Error Log:
    echo ----------------------------------------
    type error.log | more
    echo.
)

echo 📋 Recent Python errors (if any):
echo ----------------------------------------
python -c "
import sys
import traceback
try:
    # Try importing main modules to catch any import errors
    import enhanced_dashboard_api
    import enhanced_dashboard_integration
    print('✅ No import errors detected')
except Exception as e:
    print(f'❌ Import error: {e}')
    traceback.print_exc()
"

echo.
pause
goto dev_menu

:performance_test
cls
echo.
echo ===============================================
echo   PERFORMANCE TEST
echo ===============================================
echo.

echo Running performance benchmarks...
echo.

python -c "
import time
import requests
import concurrent.futures
import statistics

def test_api_endpoint():
    try:
        start_time = time.time()
        response = requests.get('http://127.0.0.1:8001/health', timeout=5)
        end_time = time.time()
        return end_time - start_time if response.status_code == 200 else None
    except:
        return None

print('🚀 Starting API performance test...')
print('Testing response times for 10 concurrent requests...')

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(test_api_endpoint) for _ in range(10)]
    results = [future.result() for future in concurrent.futures.as_completed(futures)]

valid_results = [r for r in results if r is not None]
if valid_results:
    avg_time = statistics.mean(valid_results)
    min_time = min(valid_results)
    max_time = max(valid_results)
    
    print(f'✅ API Performance Results:')
    print(f'  Average Response Time: {avg_time:.3f}s')
    print(f'  Fastest Response: {min_time:.3f}s')
    print(f'  Slowest Response: {max_time:.3f}s')
    print(f'  Success Rate: {len(valid_results)}/10')
else:
    print('❌ API not available for testing')

print()
print('📊 Memory usage test...')
import psutil
process = psutil.Process()
print(f'Current Memory Usage: {process.memory_info().rss / 1024 / 1024:.1f} MB')
"

echo.
pause
goto dev_menu

:reset_state
cls
echo.
echo ===============================================
echo   RESET SYSTEM STATE
echo ===============================================
echo.

echo ⚠️  WARNING: This will reset system state and logs
set /p confirm="Are you sure? (y/n): "

if /i "%confirm%"=="y" (
    echo.
    echo Resetting system state...
    
    if exist "enhanced_agent_activity.log" del "enhanced_agent_activity.log"
    if exist "system.log" del "system.log"
    if exist "error.log" del "error.log"
    if exist "data\memory\agent_memory.json" (
        echo {"agents": {}, "tasks": [], "system_state": {"last_update": ""}} > "data\memory\agent_memory.json"
    )
    
    echo ✅ System state reset complete!
) else (
    echo Reset cancelled.
)

echo.
pause
goto dev_menu

:dep_analysis
cls
echo.
echo ===============================================
echo   DEPENDENCY ANALYSIS
echo ===============================================
echo.

echo Analyzing dependencies and versions...
echo.

python -c "
import pkg_resources
import subprocess
import sys

print('📦 INSTALLED PACKAGES:')
print('=' * 40)

# Get installed packages
installed_packages = [d for d in pkg_resources.working_set]
installed_packages.sort(key=lambda x: x.key)

for package in installed_packages:
    print(f'{package.key}: {package.version}')

print()
print('🔍 CHECKING FOR UPDATES:')
print('=' * 40)

# Check for outdated packages
try:
    result = subprocess.run([sys.executable, '-m', 'pip', 'list', '--outdated'], 
                          capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    else:
        print('✅ All packages are up to date!')
except:
    print('❌ Could not check for updates')
"

echo.
pause
goto dev_menu

:quality_check
cls
echo.
echo ===============================================
echo   CODE QUALITY CHECK
echo ===============================================
echo.

echo Running code quality checks...
echo.

echo 1/3 - Checking Python syntax...
python -m py_compile enhanced_dashboard_api.py
python -m py_compile enhanced_dashboard_integration.py
python -m py_compile universal_dashboard_launcher.py

echo.
echo 2/3 - Checking import structure...
python -c "
import ast
import os

def check_imports(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append(f'{module}.{alias.name}')
        
        print(f'✅ {filename}: {len(imports)} imports found')
        return True
    except Exception as e:
        print(f'❌ {filename}: {e}')
        return False

files = ['enhanced_dashboard_api.py', 'enhanced_dashboard_integration.py', 'universal_dashboard_launcher.py']
for file in files:
    if os.path.exists(file):
        check_imports(file)
"

echo.
echo 3/3 - File structure check...
python -c "
import os
from pathlib import Path

required_structure = {
    'prompt_profiles': ['agent_prompt_profiles.json'],
    'data/memory': ['agent_memory.json'],
    'core': ['simple_agents_fixed.py']
}

print('📁 DIRECTORY STRUCTURE:')
for dir_name, files in required_structure.items():
    dir_path = Path(dir_name)
    if dir_path.exists():
        print(f'✅ {dir_name}/')
        for file in files:
            file_path = dir_path / file
            status = '✅' if file_path.exists() else '❌'
            print(f'  {status} {file}')
    else:
        print(f'❌ {dir_name}/ (missing)')
"

echo.
echo ✅ Code quality check complete!
echo.
pause
goto dev_menu

:backup_state
cls
echo.
echo ===============================================
echo   BACKUP CURRENT STATE
echo ===============================================
echo.

echo Creating backup of current system state...
echo.

set backup_name=backup_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set backup_name=%backup_name: =0%

echo Creating backup directory: %backup_name%
mkdir "%backup_name%" 2>nul

echo Copying configuration files...
xcopy "prompt_profiles" "%backup_name%\prompt_profiles\" /E /I /Q
xcopy "data" "%backup_name%\data\" /E /I /Q

echo Copying dashboard files...
copy "enhanced_dashboard_*.py" "%backup_name%\" >nul 2>&1
copy "consolidated_dashboard.py" "%backup_name%\" >nul 2>&1
copy "universal_dashboard_launcher.py" "%backup_name%\" >nul 2>&1
copy "enhanced_dashboard.html" "%backup_name%\" >nul 2>&1

echo Copying core files...
copy "run_swarm.py" "%backup_name%\" >nul 2>&1
copy "core\simple_agents_fixed.py" "%backup_name%\" >nul 2>&1

echo Creating backup info...
echo Backup created on %date% at %time% > "%backup_name%\backup_info.txt"

echo.
echo ✅ Backup created successfully in: %backup_name%
echo.
pause
goto dev_menu

:main_launcher
start "" "start_enhanced_system.bat"
goto :eof

echo.
echo ===============================================
echo   DEVELOPER TOOLS SESSION ENDED
echo ===============================================
echo.
timeout /t 2 /nobreak >nul
exit /b 0
