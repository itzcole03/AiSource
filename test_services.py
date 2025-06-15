#!/usr/bin/env python3
"""
Simple service tester
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def test_model_manager_backend():
    """Test Model Manager backend startup"""
    print("Testing Model Manager backend...")
    
    backend_script = Path("frontend/model manager/backend/server_optimized.py")
    
    try:
        # Use the virtual environment Python
        python_exe = "C:/Users/bcmad/OneDrive/Desktop/agentarmycompforbolt/ultimate_copilot/.venv/Scripts/python.exe"
        
        print(f"Starting: {python_exe} {backend_script} --port 8002")
        
        process = subprocess.Popen(
            [python_exe, str(backend_script), "--port", "8002"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait and check
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Model Manager backend is running")
            
            # Test health endpoint
            try:
                response = requests.get("http://localhost:8002/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Health check passed")
                else:
                    print(f"❌ Health check failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Health check failed: {e}")
            
            return process
        else:
            print("❌ Model Manager backend failed to start")
            stdout, stderr = process.communicate()
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def test_dashboard_backend():
    """Test dashboard backend startup"""
    print("\nTesting Dashboard backend...")
    
    backend_script = Path("frontend/dashboard_backend_clean.py")
    
    try:
        python_exe = "C:/Users/bcmad/OneDrive/Desktop/agentarmycompforbolt/ultimate_copilot/.venv/Scripts/python.exe"
        
        print(f"Starting: {python_exe} {backend_script} --port 8001")
        
        process = subprocess.Popen(
            [python_exe, str(backend_script), "--port", "8001"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Dashboard backend is running")
            
            # Test health endpoint
            try:
                response = requests.get("http://localhost:8001/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Health check passed")
                else:
                    print(f"❌ Health check failed: {response.status_code}")
            except Exception as e:
                print(f"❌ Health check failed: {e}")
            
            return process
        else:
            print("❌ Dashboard backend failed to start")
            stdout, stderr = process.communicate()
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None

def main():
    """Test services"""
    print("=" * 50)
    print("🧪 SERVICE TESTER")
    print("=" * 50)
    
    processes = []
    
    # Test Model Manager backend
    mm_backend = test_model_manager_backend()
    if mm_backend:
        processes.append(mm_backend)
    
    # Test Dashboard backend
    dash_backend = test_dashboard_backend()
    if dash_backend:
        processes.append(dash_backend)
    
    print(f"\n✅ Started {len(processes)} services")
    
    if processes:
        print("Press Ctrl+C to stop all services...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping all services...")
            for process in processes:
                process.terminate()
            print("✅ All services stopped!")

if __name__ == "__main__":
    main()
