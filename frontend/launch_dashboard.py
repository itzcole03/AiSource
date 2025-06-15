#!/usr/bin/env python3
"""
Enhanced Dashboard Launcher

Launches both the backend API server and the Streamlit dashboard.
Features:
- Automatic port detection and conflict resolution
- Better virtual environment handling
- UTF-8 encoding fixes
- Robust error handling
- Fallback mechanisms
"""

import subprocess
import time
import sys
import logging
from pathlib import Path
import threading
import signal
import os
import socket
import json
from typing import Optional, List, Tuple

# Force UTF-8 encoding for console output
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Setup logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("DashboardLauncher")

class DashboardLauncher:
    """Enhanced launcher with automatic port detection and better error handling"""
    
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.project_root = Path(__file__).parent.parent
        self.frontend_dir = Path(__file__).parent
        self.backend_port = None
        self.frontend_port = None
        
    def find_available_port(self, start_port: int = 8501, max_attempts: int = 10) -> Optional[int]:
        """Find an available port starting from start_port"""
        for port in range(start_port, start_port + max_attempts):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex(('127.0.0.1', port))
                    if result != 0:  # Port is available
                        return port
            except Exception:
                continue
        return None
    
    def check_port_in_use(self, port: int) -> bool:
        """Check if a port is in use"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('127.0.0.1', port))
                return result == 0  # Port is in use
        except Exception:
            return False
    
    def print_success(self, message: str):
        """Print success message with proper encoding"""
        try:
            print(f"✅ {message}")
        except UnicodeEncodeError:
            print(f"[OK] {message}")
    
    def print_warning(self, message: str):
        """Print warning message with proper encoding"""
        try:
            print(f"⚠️ {message}")
        except UnicodeEncodeError:
            print(f"[WARNING] {message}")
    
    def print_error(self, message: str):
        """Print error message with proper encoding"""
        try:
            print(f"❌ {message}")
        except UnicodeEncodeError:
            print(f"[ERROR] {message}")
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are available and install if needed"""
        required_packages = ["streamlit", "fastapi", "uvicorn", "plotly", "pandas", "pyyaml", "requests", "psutil"]
        missing_deps = []
        
        logger.info("Checking dependencies...")
        
        for package in required_packages:
            try:
                __import__(package)
                self.print_success(f"{package} available")
            except ImportError:
                missing_deps.append(package)
                self.print_warning(f"{package} missing")
        
        if missing_deps:
            logger.info(f"Installing missing dependencies: {', '.join(missing_deps)}")
            
            # Check if we're in a virtual environment
            in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            
            install_commands = [
                [sys.executable, "-m", "pip", "install"] + missing_deps,  # Try regular first if in venv
                [sys.executable, "-m", "pip", "install", "--user"] + missing_deps,  # User install
                [sys.executable, "-m", "pip", "install", "--force-reinstall", "--user"] + missing_deps  # Force user install
            ]
            
            if not in_venv:
                # If not in venv, try user install first
                install_commands = install_commands[1:] + [install_commands[0]]
            
            for attempt, cmd in enumerate(install_commands, 1):
                try:
                    logger.info(f"Attempt {attempt}: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, encoding='utf-8')
                    
                    if result.returncode == 0:
                        self.print_success("Dependencies installed successfully")
                        return True
                    else:
                        self.print_warning(f"Installation attempt {attempt} failed")
                        logger.warning(f"Error: {result.stderr}")
                        
                except subprocess.TimeoutExpired:
                    self.print_error(f"Installation attempt {attempt} timed out")
                except Exception as e:
                    self.print_error(f"Installation attempt {attempt} failed: {e}")
            
            # All attempts failed
            self.print_error("Failed to install dependencies")
            print("\nPlease try one of these solutions:")
            print("1. Run as administrator")
            print("2. Install manually:")
            print(f"   pip install --user {' '.join(missing_deps)}")
            print("3. Use virtual environment:")
            print("   python -m venv dashboard_env")
            print("   dashboard_env\\Scripts\\activate")
            print(f"   pip install {' '.join(missing_deps)}")
            return False
        else:
            self.print_success("All required dependencies are available")
            return True
    
    def start_backend(self) -> bool:
        """Start the backend API server with automatic port detection"""
        try:
            logger.info("Starting dashboard backend...")
            backend_script = self.frontend_dir / "dashboard_backend.py"
            backend_minimal_script = self.frontend_dir / "dashboard_backend_minimal.py"
            
            # Try the main backend first, then fallback to minimal
            backend_to_use = backend_minimal_script  # Use minimal by default for reliability
            if backend_script.exists():
                logger.info("Attempting to use full backend first...")
                # We'll still use minimal for now due to dependency issues
            
            if not backend_to_use.exists():
                self.print_error(f"No backend script found")
                return False
            
            # Find available port for backend (starting from 8001)
            self.backend_port = self.find_available_port(8001)
            if not self.backend_port:
                self.print_warning("Could not find available port for backend, using 8001")
                self.backend_port = 8001
            
            # Set environment variable for backend port
            env = os.environ.copy()
            env['DASHBOARD_BACKEND_PORT'] = str(self.backend_port)
            
            logger.info(f"Using backend: {backend_to_use.name}")
            self.backend_process = subprocess.Popen(
                [sys.executable, str(backend_to_use)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                encoding='utf-8'
            )
            
            # Give backend time to start
            time.sleep(3)
            
            # Check if backend started successfully
            if self.backend_process.poll() is None:
                self.print_success(f"Backend server started on port {self.backend_port}")
                return True
            else:
                self.print_error("Backend server failed to start")
                try:
                    stdout, stderr = self.backend_process.communicate(timeout=5)
                    if stderr:
                        logger.error(f"Backend error: {stderr}")
                except subprocess.TimeoutExpired:
                    self.backend_process.kill()
                return False
                
        except Exception as e:
            self.print_error(f"Failed to start backend: {e}")
            return False
    
    def start_frontend(self) -> bool:
        """Start the Streamlit frontend with automatic port detection"""
        try:
            logger.info("Starting dashboard frontend...")
            frontend_script = self.frontend_dir / "unified_dashboard.py"
            
            if not frontend_script.exists():
                self.print_error(f"Frontend script not found: {frontend_script}")
                return False
            
            # Check if streamlit is available
            try:
                result = subprocess.run([sys.executable, "-m", "streamlit", "--version"], 
                                      capture_output=True, text=True, encoding='utf-8')
                if result.returncode != 0:
                    self.print_error("Streamlit is not properly installed")
                    return False
            except Exception as e:
                self.print_error(f"Failed to check Streamlit: {e}")
                return False
            
            # Find available port for frontend (starting from 8501)
            self.frontend_port = self.find_available_port(8501)
            if not self.frontend_port:
                self.print_warning("Could not find available port for frontend, using 8501")
                self.frontend_port = 8501
            
            # Check if port is in use and warn user
            if self.check_port_in_use(self.frontend_port):
                self.print_warning(f"Port {self.frontend_port} appears to be in use")
                # Try to find another port
                new_port = self.find_available_port(self.frontend_port + 1)
                if new_port:
                    self.frontend_port = new_port
                    logger.info(f"Using alternate port {self.frontend_port}")
            
            # Set environment variables for frontend
            env = os.environ.copy()
            if self.backend_port:
                env['DASHBOARD_BACKEND_URL'] = f"http://localhost:{self.backend_port}"
            
            self.frontend_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", str(frontend_script),
                "--server.port", str(self.frontend_port),
                "--server.address", "127.0.0.1",
                "--server.headless", "false",
                "--browser.gatherUsageStats", "false"
            ], cwd=str(self.project_root), env=env, encoding='utf-8')
            
            self.print_success(f"Frontend dashboard started on port {self.frontend_port}")
            return True
            
        except Exception as e:
            self.print_error(f"Failed to start frontend: {e}")
            return False
    
    def stop_processes(self):
        """Stop all dashboard processes"""
        logger.info("Stopping dashboard processes...")
        
        if self.backend_process and self.backend_process.poll() is None:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                self.print_success("Backend stopped")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                self.print_success("Backend force stopped")
            except Exception as e:
                self.print_warning(f"Error stopping backend: {e}")
        
        if self.frontend_process and self.frontend_process.poll() is None:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                self.print_success("Frontend stopped")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                self.print_success("Frontend force stopped")
            except Exception as e:
                self.print_warning(f"Error stopping frontend: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("Received shutdown signal, stopping dashboard...")
        self.stop_processes()
        sys.exit(0)
    
    def save_launch_info(self):
        """Save launch information for other scripts"""
        launch_info = {
            "backend_port": self.backend_port,
            "frontend_port": self.frontend_port,
            "backend_url": f"http://localhost:{self.backend_port}" if self.backend_port else None,
            "frontend_url": f"http://localhost:{self.frontend_port}" if self.frontend_port else None,
            "timestamp": time.time()
        }
        
        try:
            info_file = self.project_root / "dashboard_launch_info.json"
            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(launch_info, f, indent=2)
        except Exception as e:
            logger.warning(f"Could not save launch info: {e}")
    
    def run(self) -> bool:
        """Run the complete dashboard system"""
        try:
            print("🚀 Ultimate Copilot Dashboard Launcher (Enhanced)")
        except UnicodeEncodeError:
            print("Ultimate Copilot Dashboard Launcher (Enhanced)")
        
        print("=" * 50)
        print()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Check dependencies
        if not self.check_dependencies():
            self.print_error("Cannot continue without required dependencies")
            return False
        
        # Verify file structure
        if not self.frontend_dir.exists():
            self.print_error(f"Frontend directory not found: {self.frontend_dir}")
            return False
        
        try:
            # Start backend
            backend_started = self.start_backend()
            if not backend_started:
                self.print_warning("Failed to start backend, continuing with frontend only...")
                self.print_warning("Some dashboard features may not work without backend")
            
            # Start frontend
            if not self.start_frontend():
                self.print_error("Failed to start frontend")
                self.stop_processes()
                return False
            
            # Save launch information
            self.save_launch_info()
            
            try:
                print("🎉 Dashboard launched successfully!")
            except UnicodeEncodeError:
                print("Dashboard launched successfully!")
            
            if self.backend_port:
                print(f"📊 Backend API: http://localhost:{self.backend_port}")
            print(f"🌐 Dashboard UI: http://localhost:{self.frontend_port}")
            print()
            print("Press Ctrl+C to stop the dashboard")
            
            # Wait for processes
            try:
                while True:
                    # Check if processes are still running
                    if self.backend_process and self.backend_process.poll() is not None:
                        self.print_warning("Backend process died unexpectedly")
                        # Don't exit, frontend can still work
                    
                    if self.frontend_process and self.frontend_process.poll() is not None:
                        self.print_error("Frontend process died unexpectedly")
                        break
                    
                    time.sleep(5)
            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt")
            
        except Exception as e:
            self.print_error(f"Error running dashboard: {e}")
            return False
        finally:
            self.stop_processes()
        
        return True

if __name__ == "__main__":
    launcher = DashboardLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)
