@echo off
cls
echo.
echo ===============================================
echo   ULTIMATE COPILOT SYSTEM - QUICK TEST
echo ===============================================
echo.
echo Testing the reorganized system structure...
echo.

REM Check if we're in the right directory
if not exist "main.py" (
    echo ERROR: main.py not found. Please run this from the ultimate_copilot directory.
    pause
    exit /b 1
)

echo ✓ Found main.py
if exist "requirements.txt" echo ✓ Found requirements.txt
if exist "config\" echo ✓ Found config directory
if exist "core\" echo ✓ Found core directory
if exist "agents\" echo ✓ Found agents directory
if exist "integrations\" echo ✓ Found integrations directory

echo.
echo Testing Python imports...
python -c "
import sys
print('Python version:', sys.version)
print()

# Test core imports
try:
    import yaml
    print('✓ YAML support available')
except ImportError:
    print('⚠ YAML not available (optional)')

# Test required packages
packages = ['asyncio', 'logging', 'pathlib', 'json', 'datetime']
for pkg in packages:
    try:
        __import__(pkg)
        print(f'✓ {pkg} - available')
    except ImportError:
        print(f'✗ {pkg} - missing')

print()
print('System structure test completed!')
"

echo.
echo Structure verification complete!
echo.
echo To start the system:
echo   1. Run: pip install -r requirements.txt
echo   2. Run: start.bat (for menu) or python main.py (direct)
echo   3. Access dashboard at http://localhost:8501 (if started)
echo.
echo For help, see INSTALL_GUIDE.md
echo.
pause
