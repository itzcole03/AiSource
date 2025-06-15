#!/usr/bin/env python3
"""
Minimal Dashboard Launcher

Basic launcher without any special characters or complex features.
Just starts the dashboard with automatic port detection.
"""

import subprocess
import sys
import os
import socket
from pathlib import Path

def find_project_root():
    """Find the project root directory"""
    current = Path.cwd()
    while current.parent != current:
        if (current / "frontend" / "dashboard.py").exists():
            return current
        current = current.parent
    
    # If not found from cwd, try script location
    script_dir = Path(__file__).parent
    if (script_dir / "frontend" / "dashboard.py").exists():
        return script_dir
    
    raise RuntimeError("Could not find project directory")

def find_python():
    """Find Python executable"""
    project_root = find_project_root()
    
    # Try virtual environment first
    venv_python = project_root / "dashboard_env" / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)
    
    return sys.executable

def find_free_port(start_port=8001):
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + 10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                if result != 0:  # Port is free
                    return port
        except:
            continue
    return None

def main():
    """Main launcher"""
    try:
        print("Starting Ultimate Copilot Dashboard...")
        
        # Find project and Python
        project_root = find_project_root()
        python_exec = find_python()
        
        print(f"Project: {project_root}")
        print(f"Python: {python_exec}")
        
        # Find free ports
        backend_port = find_free_port(8001)
        frontend_port = find_free_port(8501)
        
        if not backend_port or not frontend_port:
            print("ERROR: Could not find free ports")
            return False
        
        print(f"Backend port: {backend_port}")
        print(f"Frontend port: {frontend_port}")
        
        # Start backend
        backend_script = project_root / "frontend" / "dashboard_backend.py"
        backend_cmd = [python_exec, str(backend_script), "--port", str(backend_port)]
        
        print("Starting backend...")
        backend_proc = subprocess.Popen(
            backend_cmd,
            cwd=str(project_root / "frontend")
        )
        
        # Wait a bit
        import time
        time.sleep(2)
        
        # Start frontend
        dashboard_script = project_root / "frontend" / "dashboard.py"
        
        # Set environment
        env = os.environ.copy()
        env["STREAMLIT_SERVER_PORT"] = str(frontend_port)
        env["DASHBOARD_BACKEND_URL"] = f"http://127.0.0.1:{backend_port}"
        
        frontend_cmd = [
            python_exec, "-m", "streamlit", "run",
            str(dashboard_script),
            f"--server.port={frontend_port}",
            "--server.address=127.0.0.1"        ]
        
        print("Starting frontend...")
        frontend_proc = subprocess.Popen(
            frontend_cmd,
            cwd=str(project_root.parent),  # Run from parent directory to avoid numpy conflicts
            env=env
        )
        
        print("Dashboard started!")
        print(f"URL: http://localhost:{frontend_port}")
        print(f"API: http://localhost:{backend_port}")
        print("Press Ctrl+C to stop")
        
        # Wait
        try:
            frontend_proc.wait()
        except KeyboardInterrupt:
            print("\nStopping...")
            try:
                backend_proc.terminate()
                frontend_proc.terminate()
            except:
                pass
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("Press Enter to exit...")
        sys.exit(1)
