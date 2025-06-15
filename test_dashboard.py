#!/usr/bin/env python3
"""
Test Ultimate Copilot Dashboard Launch

Simple test to verify the dashboard can start without issues.
"""

import subprocess
import sys
import socket
from pathlib import Path

def test_port_detection():
    """Test port detection"""
    print("Testing port detection...")
    
    def is_port_free(port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                return result != 0
        except:
            return False
    
    # Test backend ports
    for port in [8001, 8002, 8003]:
        status = "FREE" if is_port_free(port) else "BUSY"
        print(f"  Port {port}: {status}")
    
    # Test frontend ports  
    for port in [8501, 8502, 8503]:
        status = "FREE" if is_port_free(port) else "BUSY"
        print(f"  Port {port}: {status}")

def test_python_detection():
    """Test Python executable detection"""
    print("Testing Python detection...")
    
    project_root = Path.cwd()
    venv_python = project_root / "dashboard_env" / "Scripts" / "python.exe"
    
    if venv_python.exists():
        print(f"  Virtual env Python: {venv_python}")
        try:
            result = subprocess.run([str(venv_python), "--version"], capture_output=True, text=True)
            print(f"  Version: {result.stdout.strip()}")
        except:
            print("  ERROR: Could not run venv Python")
    else:
        print("  Virtual env Python: NOT FOUND")
    
    print(f"  System Python: {sys.executable}")
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"  Version: {result.stdout.strip()}")
    except:
        print("  ERROR: Could not run system Python")

def test_dependencies():
    """Test if required dependencies are available"""
    print("Testing dependencies...")
    
    required = ["streamlit", "fastapi", "uvicorn", "pydantic"]
    
    for package in required:
        try:
            result = subprocess.run(
                [sys.executable, "-c", f"import {package}; print({package}.__version__)"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"  {package}: OK ({version})")
            else:
                print(f"  {package}: MISSING")
        except:
            print(f"  {package}: ERROR")

def main():
    """Run all tests"""
    print("Ultimate Copilot Dashboard - System Test")
    print("=" * 50)
    
    try:
        test_python_detection()
        print()
        test_port_detection()
        print()
        test_dependencies()
        print()
        print("Test completed!")
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
