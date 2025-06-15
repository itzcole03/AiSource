#!/usr/bin/env python3
"""
Dashboard Launcher

Launches both the backend API server and the Streamlit dashboard.
Enhanced with better dependency management and error handling.
"""

import subprocess
import time
import sys
import logging
from pathlib import Path
import threading
import signal
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DashboardLauncher")

class DashboardLauncher:
    """Launches and manages dashboard components"""
    
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.project_root = Path(__file__).parent.parent
        self.frontend_dir = Path(__file__).parent
        
    def check_dependencies(self):
        """Check if required dependencies are available and install if needed"""
        required_packages = ["streamlit", "fastapi", "uvicorn", "plotly", "pandas", "pyyaml", "requests", "psutil"]
        missing_deps = []
        
        logger.info("Checking dependencies...")
        
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✅ {package} available")
            except ImportError:
                missing_deps.append(package)
                logger.warning(f"❌ {package} missing")
        
        if missing_deps:
            logger.info(f"Installing missing dependencies: {', '.join(missing_deps)}")
            
            # Try user installation first (safer, no admin required)
            try:
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", "--user"
                ] + missing_deps, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    logger.info("✅ Dependencies installed successfully with --user")
                    return True
                else:
                    logger.warning("User installation failed, trying system installation...")
                    logger.warning(f"Error: {result.stderr}")
                    
                    # Try regular installation (might need admin)
                    result = subprocess.run([
                        sys.executable, "-m", "pip", "install"
                    ] + missing_deps, capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        logger.info("✅ Dependencies installed successfully")
                        return True
                    else:
                        logger.error("❌ Failed to install dependencies")
                        logger.error(f"Error: {result.stderr}")
                        logger.error("\nPlease try one of these solutions:")
                        logger.error("1. Run as administrator")
                        logger.error("2. Install manually:")
                        logger.error(f"   pip install --user {' '.join(missing_deps)}")
                        logger.error("3. Use virtual environment:")
                        logger.error("   python -m venv dashboard_env")
                        logger.error("   dashboard_env\\Scripts\\activate")
                        logger.error(f"   pip install {' '.join(missing_deps)}")
                        return False
                        
            except subprocess.TimeoutExpired:
                logger.error("❌ Installation timed out")
                return False
            except Exception as e:
                logger.error(f"❌ Installation failed: {e}")
                return False
        else:
            logger.info("✅ All required dependencies are available")
            return True
    
    def start_backend(self):
        """Start the backend API server"""
        try:
            logger.info("Starting dashboard backend...")
            backend_script = self.frontend_dir / "dashboard_backend.py"
            
            if not backend_script.exists():
                logger.error(f"Backend script not found: {backend_script}")
                return False
            
            self.backend_process = subprocess.Popen(
                [sys.executable, str(backend_script)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Give backend time to start
            time.sleep(3)
            
            # Check if backend started successfully
            if self.backend_process.poll() is None:
                logger.info("✅ Backend server started successfully")
                return True
            else:
                logger.error("❌ Backend server failed to start")
                stdout, stderr = self.backend_process.communicate()
                if stderr:
                    logger.error(f"Backend error: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the Streamlit frontend"""
        try:
            logger.info("Starting dashboard frontend...")
            frontend_script = self.frontend_dir / "unified_dashboard.py"
            
            if not frontend_script.exists():
                logger.error(f"Frontend script not found: {frontend_script}")
                return False
            
            # Check if streamlit is available
            try:
                result = subprocess.run([sys.executable, "-m", "streamlit", "--version"], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    logger.error("Streamlit is not properly installed")
                    return False
            except Exception as e:
                logger.error(f"Failed to check Streamlit: {e}")
                return False
            
            self.frontend_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", str(frontend_script),
                "--server.port", "8501",
                "--server.address", "127.0.0.1",
                "--server.headless", "false",
                "--browser.gatherUsageStats", "false"
            ], cwd=str(self.project_root))
            
            logger.info("✅ Frontend dashboard started successfully")
            logger.info("🌐 Dashboard available at: http://localhost:8501")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start frontend: {e}")
            return False
    
    def stop_processes(self):
        """Stop all dashboard processes"""
        logger.info("Stopping dashboard processes...")
        
        if self.backend_process and self.backend_process.poll() is None:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                logger.info("✅ Backend stopped")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                logger.info("✅ Backend force stopped")
            except Exception as e:
                logger.warning(f"Error stopping backend: {e}")
        
        if self.frontend_process and self.frontend_process.poll() is None:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                logger.info("✅ Frontend stopped")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                logger.info("✅ Frontend force stopped")
            except Exception as e:
                logger.warning(f"Error stopping frontend: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Received shutdown signal, stopping dashboard...")
        self.stop_processes()
        sys.exit(0)
    
    def run(self):
        """Run the complete dashboard system"""
        logger.info("🚀 Ultimate Copilot Dashboard Launcher")
        logger.info("="*50)
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Check dependencies
        if not self.check_dependencies():
            logger.error("Cannot continue without required dependencies")
            return False
        
        # Verify file structure
        if not self.frontend_dir.exists():
            logger.error(f"Frontend directory not found: {self.frontend_dir}")
            return False
        
        try:
            # Start backend
            if not self.start_backend():
                logger.error("Failed to start backend, continuing with frontend only...")
                logger.warning("Some dashboard features may not work without backend")
            
            # Start frontend
            if not self.start_frontend():
                logger.error("Failed to start frontend")
                self.stop_processes()
                return False
            
            logger.info("🎉 Dashboard launched successfully!")
            logger.info("📊 Backend API: http://localhost:8001")
            logger.info("🌐 Dashboard UI: http://localhost:8501")
            logger.info("")
            logger.info("Press Ctrl+C to stop the dashboard")
            
            # Wait for processes
            try:
                while True:
                    # Check if processes are still running
                    if self.backend_process and self.backend_process.poll() is not None:
                        logger.warning("Backend process died unexpectedly")
                        # Don't exit, frontend can still work
                    
                    if self.frontend_process and self.frontend_process.poll() is not None:
                        logger.error("Frontend process died unexpectedly")
                        break
                    
                    time.sleep(5)
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
            
        except Exception as e:
            logger.error(f"Error running dashboard: {e}")
        finally:
            self.stop_processes()
        
        return True

if __name__ == "__main__":
    launcher = DashboardLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)
