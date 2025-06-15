import subprocess
import sys
from pathlib import Path

PYTHON_EXE = "C:/Users/bcmad/OneDrive/Desktop/agentarmycompforbolt/ultimate_copilot/.venv/Scripts/python.exe"

print("Testing minimal startup...")

# Test 1: Just check if Python works
print("1. Testing Python executable...")
try:
    result = subprocess.run([PYTHON_EXE, "--version"], capture_output=True, text=True, timeout=10)
    print(f"   Python version: {result.stdout.strip()}")
    print(f"   Return code: {result.returncode}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Try to import basic modules
print("2. Testing basic imports...")
try:
    result = subprocess.run([PYTHON_EXE, "-c", "import sys; print('Python works')"], 
                          capture_output=True, text=True, timeout=10)
    print(f"   Output: {result.stdout.strip()}")
    print(f"   Error: {result.stderr.strip()}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Check file existence
print("3. Checking files...")
files_to_check = [
    "frontend/model manager/backend/server_optimized.py",
    "frontend/dashboard_backend_clean.py",
    "frontend/dashboard.py"
]

for file_path in files_to_check:
    exists = Path(file_path).exists()
    print(f"   {file_path}: {'✅' if exists else '❌'}")

print("Test complete!")
