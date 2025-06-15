#!/usr/bin/env python3
"""
Simple Enhanced Dashboard Launcher

Launches the dashboard using the virtual environment with fixed dependencies.
Automatically finds available ports if default ports are in use.
"""

import subprocess
import time
import sys
import logging
from pathlib import Path
import signal
import os
import socket

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DashboardLauncher")

class SimpleDashboardLauncher:
    """Simple launcher that uses the virtual environment with automatic port detection"""
    
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.project_root = Path(__file__).parent.parent
        self.frontend_dir = Path(__file__).parent
        
        # Port configuration
        self.backend_port = None
        self.frontend_port = None
        
        # Find virtual environment Python
        self.venv_python = self.find_venv_python()
        if not self.venv_python:
            logger.error("Virtual environment not found!")
            sys.exit(1)
        
        logger.info(f"Using Python: {self.venv_python}")
      def find_available_port(self, start_port: int = 8001, max_attempts: int = 10) -> int:
        """Find an available port starting from start_port"""
        # Check if a preferred port is set via environment
        if start_port == 8001:
            preferred = os.environ.get('PREFERRED_BACKEND_PORT')
            if preferred and preferred.isdigit():
                pref_port = int(preferred)
                if not self.check_port_in_use(pref_port):
                    logger.info(f"Using preferred backend port: {pref_port}")
                    return pref_port
        elif start_port == 8501:
            preferred = os.environ.get('PREFERRED_FRONTEND_PORT')
            if preferred and preferred.isdigit():
                pref_port = int(preferred)
                if not self.check_port_in_use(pref_port):
                    logger.info(f"Using preferred frontend port: {pref_port}")
                    return pref_port
        
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex(('127.0.0.1', port))
                    if result != 0:  # Port is available
                        logger.info(f"Found available port: {port}")
                        return port
            except Exception:
                continue
        
        raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts - 1}")
    
    def check_port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                return result == 0  # Port is in use
        except Exception:
            return False
    
    def find_venv_python(self) -> str:
        """Find the Python executable in virtual environment"""
        venv_path = self.project_root / "dashboard_env" / "Scripts" / "python.exe"
        if venv_path.exists():
            return str(venv_path)
        return sys.executable  # Fallback to system Python
    
    def start_backend(self) -> bool:
        """Start the backend server on an available port"""
        try:
            # Find available port for backend
            self.backend_port = self.find_available_port(start_port=8001)
            logger.info(f"Starting backend server on port {self.backend_port}...")
            
            backend_script = self.frontend_dir / "dashboard_backend.py"
            
            cmd = [self.venv_python, str(backend_script), "--port", str(self.backend_port)]
            
            self.backend_process = subprocess.Popen(
                cmd,
                cwd=str(self.frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit to see if it starts successfully
            time.sleep(3)
            
            if self.backend_process.poll() is None:
                logger.info(f"✅ Backend server started successfully on port {self.backend_port}")
                return True
            else:
                stdout, stderr = self.backend_process.communicate()
                logger.error(f"❌ Backend failed to start:")
                logger.error(f"STDOUT: {stdout}")
                logger.error(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error starting backend: {e}")
            return False
    
    def start_frontend(self) -> bool:
        """Start the frontend dashboard on an available port"""
        try:
            # Find available port for frontend
            self.frontend_port = self.find_available_port(start_port=8501)
            logger.info(f"Starting frontend dashboard on port {self.frontend_port}...")
            
            dashboard_script = self.frontend_dir / "dashboard.py"
            
            # Set environment variables
            env = os.environ.copy()
            env["STREAMLIT_SERVER_PORT"] = str(self.frontend_port)
            env["STREAMLIT_SERVER_ADDRESS"] = "127.0.0.1"
            env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
            env["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
            
            # Set backend URL for frontend to use
            if self.backend_port:
                env["DASHBOARD_BACKEND_URL"] = f"http://127.0.0.1:{self.backend_port}"
            
            # Change to project root to avoid numpy conflicts
            working_dir = str(self.project_root)
            
            cmd = [
                self.venv_python, "-m", "streamlit", "run", 
                str(dashboard_script),
                f"--server.port={self.frontend_port}",
                "--server.address=127.0.0.1",
                "--browser.gatherUsageStats=false",
                "--global.developmentMode=false"
            ]
            
            self.frontend_process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                env=env
            )
            
            logger.info(f"✅ Frontend dashboard started on port {self.frontend_port}")
            logger.info(f"🌐 Dashboard URL: http://localhost:{self.frontend_port}")
            if self.backend_port:
                logger.info(f"🔌 Backend API: http://localhost:{self.backend_port}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting frontend: {e}")
            return False
    
    def cleanup(self):
        """Clean up processes"""
        logger.info("Shutting down...")
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
            except:
                self.backend_process.kill()
        
        if self.frontend_process:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
            except:
                self.frontend_process.kill()
    
    def launch(self):
        """Launch both backend and frontend"""
        try:
            print("🚀 Ultimate Copilot Dashboard Launcher")
            print("=" * 50)
            
            # Start backend
            if not self.start_backend():
                logger.warning("⚠️ Backend failed to start, continuing with frontend only")
                logger.warning("Some dashboard features may not work without backend")
            
            # Start frontend
            if not self.start_frontend():
                logger.error("❌ Failed to start frontend")
                self.cleanup()
                return False
            
            # Wait for frontend process
            try:
                if self.frontend_process:
                    self.frontend_process.wait()
            except KeyboardInterrupt:
                logger.info("Received Ctrl+C, shutting down...")
            
            self.cleanup()
            return True
            
        except Exception as e:
            logger.error(f"Error during launch: {e}")
            self.cleanup()
            return False

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    logger.info("Received interrupt signal")
    sys.exit(0)

def main():
    """Main entry point"""
    signal.signal(signal.SIGINT, signal_handler)
    
    launcher = SimpleDashboardLauncher()
    success = launcher.launch()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
