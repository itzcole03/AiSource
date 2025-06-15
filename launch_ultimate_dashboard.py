#!/usr/bin/env python3
"""
Ultimate Copilot Dashboard Auto-Launcher

Standalone launcher that:
- Automatically detects and uses virtual environment
- Finds available ports automatically
- Handles dependency installation
- Works from any directory

Usage: python launch_ultimate_dashboard.py
"""

import subprocess
import sys
import os
import logging
from pathlib import Path
import socket

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("UltimateDashboardLauncher")

class UltimateDashboardLauncher:
    """Standalone launcher for Ultimate Copilot Dashboard"""
    
    def __init__(self):
        # Find project root (where this script is located)
        script_path = Path(__file__).resolve()
        if script_path.name == "launch_ultimate_dashboard.py":
            # Script is in project root
            self.project_root = script_path.parent
        else:
            # Script might be elsewhere, try to find project root
            current = Path.cwd()
            while current.parent != current:
                if (current / "frontend" / "dashboard.py").exists():
                    self.project_root = current
                    break
                current = current.parent
            else:
                raise RuntimeError("Could not find Ultimate Copilot project directory")
        
        self.frontend_dir = self.project_root / "frontend"
        logger.info(f"Project root: {self.project_root}")
        
        # Find Python executable
        self.python_exec = self.find_python_executable()
        logger.info(f"Using Python: {self.python_exec}")
    
    def find_python_executable(self) -> str:
        """Find the best Python executable to use"""
        # Try virtual environment first
        venv_paths = [
            self.project_root / "dashboard_env" / "Scripts" / "python.exe",  # Windows
            self.project_root / "dashboard_env" / "bin" / "python",          # Unix
            self.project_root / "venv" / "Scripts" / "python.exe",
            self.project_root / "venv" / "bin" / "python",
        ]
        
        for path in venv_paths:
            if path.exists():
                return str(path)
        
        # Fallback to system Python
        return sys.executable
    
    def check_dependencies(self) -> bool:
        """Check and install required dependencies"""
        required = ["streamlit", "fastapi", "uvicorn", "pydantic", "plotly", "pandas", "pyyaml", "requests", "psutil"]
        
        logger.info("Checking dependencies...")
        missing = []
        
        for package in required:
            try:
                result = subprocess.run(
                    [self.python_exec, "-c", f"import {package}"],
                    capture_output=True, timeout=10
                )
                if result.returncode != 0:
                    missing.append(package)
            except:
                missing.append(package)
        
        if missing:
            logger.info(f"Installing missing packages: {', '.join(missing)}")
            try:
                # Install compatible versions
                packages = missing.copy()
                if "fastapi" in packages:
                    packages[packages.index("fastapi")] = "fastapi==0.103.0"
                if "pydantic" in packages:
                    packages[packages.index("pydantic")] = "pydantic==2.0.3"
                
                subprocess.run(
                    [self.python_exec, "-m", "pip", "install"] + packages,
                    check=True, timeout=300
                )
                logger.info("✅ Dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to install dependencies: {e}")
                return False
        else:
            logger.info("✅ All dependencies available")
            return True
    
    def find_available_port(self, start_port: int = 8001) -> int:
        """Find an available port"""
        for port in range(start_port, start_port + 20):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex(('127.0.0.1', port))
                    if result != 0:
                        return port
            except:
                continue
        raise RuntimeError(f"No available ports found starting from {start_port}")
    
    def launch(self):
        """Launch the dashboard"""
        try:
            print("🚀 Ultimate Copilot Dashboard Auto-Launcher")
            print("=" * 60)
            
            # Check dependencies
            if not self.check_dependencies():
                print("\n❌ Dependency check failed. Please install manually:")
                print("pip install streamlit fastapi==0.103.0 uvicorn pydantic==2.0.3 plotly pandas pyyaml requests psutil")
                return False
            
            # Find available ports
            backend_port = self.find_available_port(8001)
            frontend_port = self.find_available_port(8501)
            
            print(f"\n🔍 Found available ports:")
            print(f"   Backend API: {backend_port}")
            print(f"   Frontend:    {frontend_port}")
            print(f"\n🌐 Dashboard will be available at: http://localhost:{frontend_port}")
            print(f"🔌 Backend API will be available at: http://localhost:{backend_port}")
            print(f"\n⏳ Starting services...")
            
            # Launch using the auto-port launcher
            launcher_script = self.frontend_dir / "launch_dashboard_auto_port.py"
            
            cmd = [self.python_exec, str(launcher_script)]
            
            # Set environment to pass port information
            env = os.environ.copy()
            env["PREFERRED_BACKEND_PORT"] = str(backend_port)
            env["PREFERRED_FRONTEND_PORT"] = str(frontend_port)
            
            # Execute the launcher
            subprocess.run(cmd, cwd=str(self.project_root), env=env)
            
            return True
            
        except KeyboardInterrupt:
            logger.info("✋ Launcher interrupted by user")
            return True
        except Exception as e:
            logger.error(f"❌ Launch failed: {e}")
            return False

def main():
    """Main entry point"""
    try:
        launcher = UltimateDashboardLauncher()
        success = launcher.launch()
        if not success:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
