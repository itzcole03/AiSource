#!/usr/bin/env python3
"""
Ultimate Copilot Dashboard Launcher (No Emoji Version)

Stable launcher that:
- Automatically detects and uses virtual environment
- Finds available ports automatically
- Handles dependency installation
- Works from any directory
- No emoji characters to avoid encoding issues
"""

import subprocess
import sys
import os
import logging
from pathlib import Path
import socket

# Setup logging with ASCII-safe format
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("DashboardLauncher")

class CleanDashboardLauncher:
    """Clean launcher without emoji characters"""
    
    def __init__(self):
        # Find project root
        script_path = Path(__file__).resolve()
        if script_path.name == "launch_clean_dashboard.py":
            self.project_root = script_path.parent
        else:
            current = Path.cwd()
            while current.parent != current:
                if (current / "frontend" / "dashboard.py").exists():
                    self.project_root = current
                    break
                current = current.parent
            else:
                raise RuntimeError("Could not find Ultimate Copilot project directory")
        
        self.frontend_dir = self.project_root / "frontend"
        print(f"[INFO] Project root: {self.project_root}")
        
        # Find Python executable
        self.python_exec = self.find_python_executable()
        print(f"[INFO] Using Python: {self.python_exec}")
    
    def find_python_executable(self) -> str:
        """Find the best Python executable to use"""
        venv_paths = [
            self.project_root / "dashboard_env" / "Scripts" / "python.exe",
            self.project_root / "dashboard_env" / "bin" / "python",
            self.project_root / "venv" / "Scripts" / "python.exe",
            self.project_root / "venv" / "bin" / "python",
        ]
        
        for path in venv_paths:
            if path.exists():
                return str(path)
        
        return sys.executable
    
    def check_dependencies(self) -> bool:
        """Check and install required dependencies"""
        required = ["streamlit", "fastapi", "uvicorn", "pydantic", "plotly", "pandas", "yaml", "requests", "psutil"]
        
        print("[INFO] Checking dependencies...")
        missing = []
        
        for package in required:
            try:
                result = subprocess.run(
                    [self.python_exec, "-c", f"import {package}"],
                    capture_output=True, timeout=10
                )
                if result.returncode != 0:
                    missing.append(package)
                    print(f"[WARN] Missing: {package}")
                else:
                    print(f"[OK] Available: {package}")
            except:
                missing.append(package)
                print(f"[WARN] Missing: {package}")
        
        if missing:
            print(f"[INFO] Installing missing packages: {', '.join(missing)}")
            try:
                packages = missing.copy()
                # Use compatible versions
                if "fastapi" in packages:
                    packages[packages.index("fastapi")] = "fastapi==0.103.0"
                if "pydantic" in packages:
                    packages[packages.index("pydantic")] = "pydantic==2.0.3"
                if "yaml" in packages:
                    packages[packages.index("yaml")] = "pyyaml"
                
                subprocess.run(
                    [self.python_exec, "-m", "pip", "install"] + packages,
                    check=True, timeout=300
                )
                print("[OK] Dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Failed to install dependencies: {e}")
                return False
        else:
            print("[OK] All dependencies available")
            return True
    
    def find_available_port(self, start_port: int = 8001) -> int:
        """Find an available port"""
        for port in range(start_port, start_port + 20):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex(('127.0.0.1', port))
                    if result != 0:
                        print(f"[INFO] Found available port: {port}")
                        return port
            except:
                continue
        raise RuntimeError(f"No available ports found starting from {start_port}")
    
    def start_backend(self, port: int) -> subprocess.Popen:
        """Start the backend server"""
        print(f"[INFO] Starting backend server on port {port}...")
        
        backend_script = self.frontend_dir / "dashboard_backend.py"
        cmd = [self.python_exec, str(backend_script), "--port", str(port)]
        
        process = subprocess.Popen(
            cmd,
            cwd=str(self.frontend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        return process
    
    def start_frontend(self, port: int, backend_port: int) -> subprocess.Popen:
        """Start the frontend dashboard"""
        print(f"[INFO] Starting frontend dashboard on port {port}...")
        
        dashboard_script = self.frontend_dir / "dashboard.py"
        
        # Set environment variables
        env = os.environ.copy()
        env["STREAMLIT_SERVER_PORT"] = str(port)
        env["STREAMLIT_SERVER_ADDRESS"] = "127.0.0.1"
        env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
        env["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
        env["DASHBOARD_BACKEND_URL"] = f"http://127.0.0.1:{backend_port}"
        
        cmd = [
            self.python_exec, "-m", "streamlit", "run", 
            str(dashboard_script),
            f"--server.port={port}",
            "--server.address=127.0.0.1",
            "--browser.gatherUsageStats=false",
            "--global.developmentMode=false"
        ]
        
        process = subprocess.Popen(
            cmd,
            cwd=str(self.project_root),  # Run from project root to avoid numpy issues
            env=env
        )
        
        return process
    
    def launch(self):
        """Launch the dashboard"""
        backend_process = None
        frontend_process = None
        
        try:
            print("=" * 60)
            print("Ultimate Copilot Dashboard Launcher")
            print("=" * 60)
            
            # Check dependencies
            if not self.check_dependencies():
                print("[ERROR] Dependency check failed")
                return False
            
            # Find available ports
            backend_port = self.find_available_port(8001)
            frontend_port = self.find_available_port(8501)
            
            print(f"\n[INFO] Using ports:")
            print(f"   Backend API: {backend_port}")
            print(f"   Frontend:    {frontend_port}")
            
            # Start backend
            backend_process = self.start_backend(backend_port)
            
            # Wait a moment for backend to start
            import time
            time.sleep(3)
            
            if backend_process.poll() is None:
                print("[OK] Backend server started successfully")
            else:
                stdout, stderr = backend_process.communicate()
                print(f"[WARN] Backend failed to start: {stderr}")
                print("[INFO] Continuing with frontend only...")
            
            # Start frontend
            frontend_process = self.start_frontend(frontend_port, backend_port)
            
            print(f"\n[SUCCESS] Dashboard launching...")
            print(f"[INFO] Dashboard URL: http://localhost:{frontend_port}")
            print(f"[INFO] Backend API URL: http://localhost:{backend_port}")
            print(f"[INFO] Press Ctrl+C to stop")
            print("=" * 60)
            
            # Wait for frontend
            if frontend_process:
                frontend_process.wait()
            
            return True
            
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down...")
            
            if backend_process:
                try:
                    backend_process.terminate()
                    backend_process.wait(timeout=5)
                except:
                    backend_process.kill()
            
            if frontend_process:
                try:
                    frontend_process.terminate()
                    frontend_process.wait(timeout=5)
                except:
                    frontend_process.kill()
            
            print("[INFO] Shutdown complete")
            return True
            
        except Exception as e:
            print(f"[ERROR] Launch failed: {e}")
            
            if backend_process:
                try:
                    backend_process.terminate()
                except:
                    pass
            
            if frontend_process:
                try:
                    frontend_process.terminate()
                except:
                    pass
            
            return False

def main():
    """Main entry point"""
    try:
        launcher = CleanDashboardLauncher()
        success = launcher.launch()
        if not success:
            print("[ERROR] Launch failed")
            input("Press Enter to exit...")
            sys.exit(1)
    except Exception as e:
        print(f"[FATAL] Error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
