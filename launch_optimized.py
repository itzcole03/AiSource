#!/usr/bin/env python3
"""
Enhanced Ultimate Copilot Dashboard Launcher
Optimized version with better error handling and network optimization
"""

import subprocess
import time
import sys
import os
import requests
from pathlib import Path

def check_service(url: str, name: str, timeout: int = 3) -> bool:
    """Check if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name} is responding")
            return True
        else:
            print(f"⚠️ {name} returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name} is not reachable")
        return False
    except requests.exceptions.Timeout:
        print(f"⏱️ {name} timed out")
        return False
    except Exception as e:
        print(f"❌ {name} error: {e}")
        return False

def start_service(cmd: list, cwd: str, name: str, check_url: str = None) -> subprocess.Popen:
    """Start a service and optionally check if it's responding"""
    print(f"\n🚀 Starting {name}...")
    print(f"Command: {' '.join(cmd)}")
    print(f"Working directory: {cwd}")
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait a moment for startup
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is not None:
            print(f"❌ {name} process terminated unexpectedly!")
            stdout, stderr = process.communicate()
            if stdout:
                print(f"Output: {stdout}")
            return None
        
        # If check_url provided, test the service
        if check_url:
            time.sleep(3)  # Additional wait for service to be ready
            if check_service(check_url, name):
                print(f"✅ {name} started successfully")
            else:
                print(f"⚠️ {name} process running but not responding to HTTP")
        else:
            print(f"✅ {name} process started")
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

def main():
    print("🚀 Enhanced Ultimate Copilot Dashboard Launcher")
    print("=" * 60)
    
    base_path = Path(__file__).parent
    venv_python = base_path / ".venv" / "Scripts" / "python.exe"
    
    # Use virtual environment Python if available, otherwise system Python
    python_exe = str(venv_python) if venv_python.exists() else sys.executable
    print(f"🐍 Using Python: {python_exe}")
    
    processes = []
    
    try:
        # 1. Start Optimized Model Manager Backend
        backend_cmd = [
            python_exe, 
            "backend/server_optimized.py", 
            "--host", "127.0.0.1", 
            "--port", "8080"
        ]
        backend_cwd = str(base_path / "frontend" / "model manager")
        backend_process = start_service(
            backend_cmd, 
            backend_cwd, 
            "Model Manager Backend",
            "http://localhost:8080/health"
        )
        if backend_process:
            processes.append(("Model Manager Backend", backend_process))
        
        # 2. Start Dashboard Backend
        dashboard_backend_cmd = [python_exe, "dashboard_backend_clean.py"]
        dashboard_backend_cwd = str(base_path / "frontend")
        dashboard_backend_process = start_service(
            dashboard_backend_cmd,
            dashboard_backend_cwd,
            "Dashboard Backend",
            "http://localhost:8001/system/status"
        )
        if dashboard_backend_process:
            processes.append(("Dashboard Backend", dashboard_backend_process))
          # 3. Start Model Manager Frontend (React) - Optional
        print("\n🚀 Starting Model Manager Frontend...")
        try:
            frontend_cmd = ["npm", "run", "dev"]
            frontend_cwd = str(base_path / "frontend" / "model manager")
            frontend_process = subprocess.Popen(
                frontend_cmd,
                cwd=frontend_cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            processes.append(("Model Manager Frontend", frontend_process))
            print("✅ Model Manager Frontend starting (React/Vite)...")
            time.sleep(5)
        except FileNotFoundError:
            print("⚠️ npm not found - Model Manager Frontend (React) not started")
            print("   The main dashboard will still work with backend integration")
        except Exception as e:
            print(f"⚠️ Could not start Model Manager Frontend: {e}")
        
        # 4. Start Dashboard Frontend (Streamlit)
        streamlit_cmd = [python_exe, "-m", "streamlit", "run", "dashboard.py", "--server.port", "8501"]
        streamlit_cwd = str(base_path / "frontend")
        streamlit_process = start_service(
            streamlit_cmd,
            streamlit_cwd,
            "Dashboard Frontend",
            "http://localhost:8501"
        )
        if streamlit_process:
            processes.append(("Dashboard Frontend", streamlit_process))
        
        print("\n" + "=" * 60)
        print("🎉 Startup Complete!")
        print("=" * 60)
        print("🌐 Access Points:")
        print("  • Main Dashboard:       http://localhost:8501")
        print("  • Model Manager:        http://localhost:5173")
        print("  • Backend API:          http://localhost:8080")
        print("  • Dashboard API:        http://localhost:8001")
        
        print("\n🔍 Service Status Check:")
        check_service("http://localhost:8080/health", "Model Manager Backend")
        check_service("http://localhost:8001/system/status", "Dashboard Backend")
        check_service("http://localhost:5173", "Model Manager Frontend")
        check_service("http://localhost:8501", "Dashboard Frontend")
        
        print("\n💡 Press Ctrl+C to stop all services")
        print("📊 Services will continue running in background...")
        
        # Keep running
        while True:
            time.sleep(5)
            # Periodically check if processes are still running
            for name, process in processes[:]:  # Copy list to avoid modification during iteration
                if process.poll() is not None:
                    print(f"⚠️ {name} process terminated")
                    processes.remove((name, process))
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Stopped {name}")
            except:
                try:
                    process.kill()
                    print(f"⚠️ Force killed {name}")
                except:
                    print(f"❌ Could not stop {name}")
        
        print("🧹 Cleanup complete. Goodbye!")

if __name__ == "__main__":
    main()
