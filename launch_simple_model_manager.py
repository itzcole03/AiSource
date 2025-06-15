#!/usr/bin/env python3
"""
Simple Model Manager Launcher for Windows
Fixed version that handles Windows subprocess issues properly
"""

import subprocess
import time
import logging
import requests
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleModelManagerLauncher:
    """Simple launcher that works reliably on Windows"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.model_manager_path = self.project_root / "frontend" / "model manager"
        self.backend_path = self.model_manager_path / "backend"
        self.backend_port = 8002
        self.frontend_port = 5173
        
        self.backend_process = None
        self.frontend_process = None
    
    def check_basic_requirements(self):
        """Basic check without subprocess timeouts"""
        logger.info("🔍 Checking basic requirements...")
        
        # Check if paths exist
        if not self.model_manager_path.exists():
            logger.error(f"❌ Model Manager directory not found: {self.model_manager_path}")
            return False
        
        if not self.backend_path.exists():
            logger.error(f"❌ Backend directory not found: {self.backend_path}")
            return False
        
        # Check backend server file
        server_script = self.backend_path / "server_optimized.py"
        if not server_script.exists():
            server_script = self.backend_path / "server.py"
        
        if not server_script.exists():
            logger.error(f"❌ Backend server not found at {server_script}")
            return False
        
        logger.info("✅ Basic file structure verified")
        return True
    
    def install_python_dependencies(self):
        """Install Python dependencies if needed"""
        logger.info("📦 Checking Python dependencies...")
        
        try:
            import fastapi
            import uvicorn
            import requests
            logger.info("✅ Python dependencies available")
            return True
        except ImportError as e:
            logger.info(f"📦 Installing missing Python dependency: {e}")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn", "requests", "psutil"], 
                             check=True, capture_output=True)
                logger.info("✅ Python dependencies installed")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to install Python dependencies: {e}")
                return False
    
    def setup_frontend_if_needed(self):
        """Setup frontend dependencies if needed"""
        node_modules_path = self.model_manager_path / "node_modules"
        
        if not node_modules_path.exists():
            logger.info("📦 Installing Node.js dependencies...")
            logger.info("⏳ This may take a few minutes...")
            
            try:
                # Change to the model manager directory and run npm install
                os.chdir(self.model_manager_path)
                result = subprocess.run("npm install", shell=True, check=True)
                logger.info("✅ Node.js dependencies installed")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to install Node.js dependencies: {e}")
                return False
            finally:
                # Change back to project root
                os.chdir(self.project_root)
        else:
            logger.info("✅ Node.js dependencies already installed")
            return True
    
    def start_backend(self):
        """Start the backend server"""
        logger.info(f"🚀 Starting backend on port {self.backend_port}...")
        
        try:
            # Use the optimized server if available
            server_script = self.backend_path / "server_optimized.py"
            if not server_script.exists():
                server_script = self.backend_path / "server.py"
            
            # Start the backend process
            self.backend_process = subprocess.Popen(
                [sys.executable, str(server_script), "--port", str(self.backend_port)],
                cwd=self.backend_path,
                shell=True
            )
            
            # Wait for backend to start
            logger.info("⏳ Waiting for backend to start...")
            for i in range(15):
                try:
                    response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=2)
                    if response.status_code == 200:
                        logger.info(f"✅ Backend started successfully on port {self.backend_port}")
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(1)
                
                # Check if process is still running
                if self.backend_process.poll() is not None:
                    logger.error("❌ Backend process exited unexpectedly")
                    return False
            
            logger.error("❌ Backend failed to start within timeout")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error starting backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the frontend development server"""
        logger.info(f"🎨 Starting frontend on port {self.frontend_port}...")
        
        try:
            # Change to model manager directory and start frontend
            os.chdir(self.model_manager_path)
            
            self.frontend_process = subprocess.Popen(
                "npm run dev",
                shell=True
            )
            
            # Wait for frontend to start
            logger.info("⏳ Waiting for frontend to start...")
            for i in range(30):  # 30 second timeout for frontend
                try:
                    response = requests.get(f"http://localhost:{self.frontend_port}", timeout=2)
                    if response.status_code == 200:
                        logger.info(f"✅ Frontend started successfully on port {self.frontend_port}")
                        return True
                except requests.exceptions.RequestException:
                    pass
                
                time.sleep(1)
                
                # Check if process is still running
                if self.frontend_process.poll() is not None:
                    logger.error("❌ Frontend process exited unexpectedly")
                    return False
            
            logger.warning("⚠️ Frontend taking longer than expected to start")
            logger.info(f"📝 Check manually at: http://localhost:{self.frontend_port}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting frontend: {e}")
            return False
        finally:
            # Change back to project root
            os.chdir(self.project_root)
    
    def test_integration(self):
        """Quick integration test"""
        logger.info("🧪 Testing integration...")
        
        try:
            # Test backend health
            response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Backend health check passed")
            else:
                logger.warning(f"⚠️ Backend health check returned {response.status_code}")
            
            # Test marketplace endpoint
            try:
                response = requests.get(f"http://localhost:{self.backend_port}/providers/marketplace/models", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    model_count = len(data.get("models", []))
                    logger.info(f"✅ Marketplace loaded {model_count} models")
                else:
                    logger.warning(f"⚠️ Marketplace endpoint returned {response.status_code}")
            except Exception as e:
                logger.warning(f"⚠️ Marketplace test failed: {e}")
            
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Integration test failed: {e}")
            return False
    
    def launch(self):
        """Launch the Model Manager"""
        logger.info("🎯 Launching Simple Model Manager...")
        
        # Basic checks
        if not self.check_basic_requirements():
            return False
        
        # Install Python dependencies
        if not self.install_python_dependencies():
            return False
        
        # Setup frontend if needed
        if not self.setup_frontend_if_needed():
            return False
        
        # Start backend
        if not self.start_backend():
            return False
        
        # Start frontend
        if not self.start_frontend():
            logger.warning("⚠️ Frontend startup had issues, but backend is running")
        
        # Test integration
        self.test_integration()
        
        logger.info("🎉 Model Manager launched!")
        logger.info(f"📊 Backend: http://localhost:{self.backend_port}")
        logger.info(f"🎨 Frontend: http://localhost:{self.frontend_port}")
        logger.info("🛑 Press Ctrl+C to stop")
        
        return True
    
    def cleanup(self):
        """Stop all processes"""
        logger.info("🧹 Stopping services...")
        
        if self.backend_process and self.backend_process.poll() is None:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                logger.info("✅ Backend stopped")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                logger.info("🔪 Backend force-killed")
            except Exception as e:
                logger.error(f"❌ Error stopping backend: {e}")
        
        if self.frontend_process and self.frontend_process.poll() is None:
            try:
                self.frontend_process.terminate()
                self.frontend_process.wait(timeout=5)
                logger.info("✅ Frontend stopped")
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
                logger.info("🔪 Frontend force-killed")
            except Exception as e:
                logger.error(f"❌ Error stopping frontend: {e}")

def main():
    """Main entry point"""
    launcher = SimpleModelManagerLauncher()
    
    try:
        if launcher.launch():
            # Keep running until interrupted
            while True:
                time.sleep(1)
                
                # Check if processes are still running
                if launcher.backend_process and launcher.backend_process.poll() is not None:
                    logger.error("❌ Backend process died unexpectedly")
                    break
                    
                if launcher.frontend_process and launcher.frontend_process.poll() is not None:
                    logger.warning("⚠️ Frontend process died unexpectedly")
                    # Frontend dying is not critical, continue
                    
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    finally:
        launcher.cleanup()

if __name__ == "__main__":
    main()
