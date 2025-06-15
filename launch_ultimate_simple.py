#!/usr/bin/env python3
"""
Ultimate Copilot Dashboard Simple Launcher
Starts all components in the correct order
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def main():
    print("🚀 Ultimate Copilot Dashboard Launcher")
    print("=" * 50)
    
    base_path = Path(__file__).parent
    venv_python = base_path / ".venv" / "Scripts" / "python.exe"
    
    # Use virtual environment Python if available, otherwise system Python
    python_exe = str(venv_python) if venv_python.exists() else sys.executable
    
    processes = []
    
    try:        # 1. Start Model Manager Backend (Optimized)
        print("\n[1/4] Starting Optimized Model Manager Backend...")
        backend_cmd = [
            python_exe, 
            "backend/server_optimized.py", 
            "--host", "127.0.0.1", 
            "--port", "8080"
        ]
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=str(base_path / "frontend" / "model manager"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(("Model Manager Backend", backend_process))
        time.sleep(3)
        
        # 2. Start Model Manager Frontend
        print("[2/4] Starting Model Manager Frontend...")
        frontend_cmd = ["npm", "run", "dev"]
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=str(base_path / "frontend" / "model manager"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(("Model Manager Frontend", frontend_process))
        time.sleep(5)
          # 3. Start Dashboard Backend
        print("[3/4] Starting Dashboard Backend...")
        dashboard_backend_cmd = [python_exe, "dashboard_backend_clean.py"]
        dashboard_backend_process = subprocess.Popen(
            dashboard_backend_cmd,
            cwd=str(base_path / "frontend"),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT  # Combine stderr with stdout
        )
        processes.append(("Dashboard Backend", dashboard_backend_process))
        
        # Check if backend started successfully
        time.sleep(2)
        if dashboard_backend_process.poll() is not None:
            print("❌ Dashboard Backend failed to start!")
            output, _ = dashboard_backend_process.communicate()
            if output:
                print(f"Error output: {output.decode()}")
        else:
            print("✅ Dashboard Backend starting...")
        time.sleep(1)
        
        # 4. Start Dashboard Frontend
        print("[4/4] Starting Dashboard Frontend...")
        streamlit_cmd = [python_exe, "-m", "streamlit", "run", "dashboard.py", "--server.port", "8501"]
        streamlit_process = subprocess.Popen(
            streamlit_cmd,
            cwd=str(base_path / "frontend"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(("Dashboard Frontend", streamlit_process))
        
        print("\n✅ All components started!")
        print("=" * 50)
        print("🌐 Access Points:")
        print("  • Main Dashboard:       http://localhost:8501")
        print("  • Model Manager:        http://localhost:5173")
        print("  • Backend API:          http://localhost:8080")
        print("  • Dashboard API:        http://localhost:8001")
        print("\n💡 Press Ctrl+C to stop all services")
        
        # Keep running
        while True:
            time.sleep(1)
            
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
