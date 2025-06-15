#!/usr/bin/env python3
"""
Ultimate Safe Dashboard Launcher

This launcher creates a temporary script in a completely safe directory
to avoid any potential numpy import conflicts.
"""

import subprocess
import sys
import os
import socket
import tempfile
import shutil
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

def test_backend(port):
    """Test if backend is responding"""
    try:
        import urllib.request
        import json
        
        response = urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=5)
        data = json.loads(response.read())
        return data.get("status") == "healthy"
    except:
        return False

def create_safe_launcher_script(temp_dir, project_root, dashboard_script, backend_port, frontend_port, python_exec):
    """Create a temporary launcher script in safe directory"""
    
    script_content = f'''#!/usr/bin/env python3
"""Temporary safe launcher script"""

import sys
import os
import subprocess

# Add project root to Python path
sys.path.insert(0, r"{project_root}")

# Set environment variables
os.environ["STREAMLIT_SERVER_PORT"] = "{frontend_port}"
os.environ["DASHBOARD_BACKEND_URL"] = "http://127.0.0.1:{backend_port}"

# Launch Streamlit
cmd = [
    r"{python_exec}", "-m", "streamlit", "run",
    r"{dashboard_script}",
    "--server.port={frontend_port}",
    "--server.address=127.0.0.1",
    "--server.headless=true"
]

print("Launching frontend from safe directory...")
print(f"Command: {{' '.join(cmd)}}")
print(f"Working directory: {{os.getcwd()}}")

try:
    subprocess.run(cmd, check=True)
except KeyboardInterrupt:
    print("\\nFrontend stopped by user")
except Exception as e:
    print(f"ERROR launching frontend: {{e}}")
    sys.exit(1)
'''
    
    script_path = temp_dir / "safe_launcher.py"
    script_path.write_text(script_content)
    return script_path

def main():
    """Main launcher"""
    try:
        print("=" * 60)
        print("   Ultimate Copilot Dashboard - Safe Launcher")
        print("=" * 60)
        print()
        
        # Find project and Python
        project_root = find_project_root()
        python_exec = find_python()
        
        print(f"Project root: {project_root}")
        print(f"Python executable: {python_exec}")
        print()
        
        # Find free ports
        backend_port = find_free_port(8001)
        frontend_port = find_free_port(8501)
        
        if not backend_port or not frontend_port:
            print("ERROR: Could not find free ports")
            return False
        
        print(f"Backend port: {backend_port}")
        print(f"Frontend port: {frontend_port}")
        print()
        
        # Start backend
        backend_script = project_root / "frontend" / "dashboard_backend_clean.py"
        backend_cmd = [python_exec, str(backend_script), "--port", str(backend_port)]
        
        print("Starting backend...")
        print(f"Command: {' '.join(backend_cmd)}")
        
        backend_proc = subprocess.Popen(
            backend_cmd,
            cwd=str(project_root / "frontend")
        )
        
        # Wait for backend to start
        print("Waiting for backend to start...")
        import time
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            if test_backend(backend_port):
                print("Backend is ready!")
                break
            print(f"  Waiting... ({i+1}/30)")
        else:
            print("WARNING: Backend may not be ready, continuing anyway...")
        
        print()
        
        # Create temporary directory for safe launching
        with tempfile.TemporaryDirectory(prefix="dashboard_safe_") as temp_dir:
            temp_path = Path(temp_dir)
            dashboard_script = project_root / "frontend" / "dashboard.py"
            
            print(f"Creating safe launcher in: {temp_path}")
            
            # Create safe launcher script
            safe_script = create_safe_launcher_script(
                temp_path, project_root, dashboard_script, 
                backend_port, frontend_port, python_exec
            )
            
            print(f"Safe script created: {safe_script}")
            print()
            
            # Launch frontend from safe directory
            print("Starting frontend from safe directory...")
            
            frontend_proc = subprocess.Popen(
                [python_exec, str(safe_script)],
                cwd=str(temp_path)
            )
            
            print()
            print("Dashboard started successfully!")
            print(f"Frontend URL: http://localhost:{frontend_port}")
            print(f"Backend API:  http://localhost:{backend_port}")
            print()
            print("Press Ctrl+C to stop the dashboard")
            print()
            
            # Wait for processes
            try:
                frontend_proc.wait()
            except KeyboardInterrupt:
                print("\nStopping dashboard...")
                try:
                    backend_proc.terminate()
                    frontend_proc.terminate()
                    
                    # Wait a bit for graceful shutdown
                    time.sleep(2)
                    
                    # Force kill if needed
                    try:
                        backend_proc.kill()
                        frontend_proc.kill()
                    except:
                        pass
                        
                except:
                    pass
        
        print("Dashboard stopped.")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print()
        input("Press Enter to exit...")
        sys.exit(1)
