#!/usr/bin/env python3
"""
Optimized Model Manager Launcher
Starts the Model Manager backend and frontend with robust error handling
"""

import asyncio
import subprocess
import time
import logging
import requests
import os
import sys
from pathlib import Path
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OptimizedModelManagerLauncher:
    """Handles startup of Model Manager with optimizations"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.model_manager_path = self.project_root / "frontend" / "model manager"
        self.backend_path = self.model_manager_path / "backend"
        self.backend_port = 8002
        self.frontend_port = 5173
        
        self.backend_process = None
        self.frontend_process = None
        
    def check_dependencies(self):
        """Check if required dependencies are available"""
        logger.info("🔍 Checking dependencies...")
        
        # Check Python
        try:
            import uvicorn
            import fastapi
            logger.info("✅ Python backend dependencies available")
        except ImportError as e:
            logger.error(f"❌ Missing Python dependency: {e}")
            logger.info("📦 Install with: pip install fastapi uvicorn requests psutil")
            return False
          # Check Node.js
        try:
            result = subprocess.run(
                ["node", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10,
                shell=True
            )
            if result.returncode == 0:
                logger.info(f"✅ Node.js available: {result.stdout.strip()}")
            else:
                logger.error("❌ Node.js not found")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.error("❌ Node.js not found or timeout")
            return False
              # Check npm
        try:
            # On Windows, npm might be a .cmd file, so try different approaches
            npm_commands = ["npm", "npm.cmd"]
            npm_found = False
            
            for npm_cmd in npm_commands:
                try:
                    result = subprocess.run(
                        [npm_cmd, "--version"], 
                        capture_output=True, 
                        text=True, 
                        timeout=10,
                        shell=True  # Use shell on Windows for better compatibility
                    )
                    if result.returncode == 0:
                        logger.info(f"✅ npm available: {result.stdout.strip()}")
                        npm_found = True
                        break
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue
            
            if not npm_found:
                logger.error("❌ npm not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ npm check error: {e}")
            return False
            
        return True
      def setup_frontend_dependencies(self):
        """Install frontend dependencies if needed"""
        node_modules_path = self.model_manager_path / "node_modules"
        
        if not node_modules_path.exists():
            logger.info("📦 Installing frontend dependencies...")
            try:
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=self.model_manager_path,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    shell=True    # Use shell for Windows compatibility
                )
                
                if result.returncode == 0:
                    logger.info("✅ Frontend dependencies installed")
                    return True
                else:
                    logger.error(f"❌ npm install failed: {result.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                logger.error("❌ npm install timeout")
                return False
            except Exception as e:
                logger.error(f"❌ npm install error: {e}")
                return False
        else:
            logger.info("✅ Frontend dependencies already installed")
            return True
    
    def start_backend(self):
        """Start the Model Manager backend"""
        logger.info(f"🚀 Starting Model Manager backend on port {self.backend_port}...")
        
        try:
            # Use the optimized server
            server_script = self.backend_path / "server_optimized.py"
            if not server_script.exists():
                server_script = self.backend_path / "server.py"
            
            if not server_script.exists():
                logger.error(f"❌ Backend server not found at {server_script}")
                return False
            
            self.backend_process = subprocess.Popen(
                [sys.executable, str(server_script), "--port", str(self.backend_port)],
                cwd=self.backend_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for backend to start
            for i in range(15):  # 15 second timeout
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
                    stdout, stderr = self.backend_process.communicate()
                    logger.error(f"❌ Backend process failed to start:")
                    logger.error(f"STDOUT: {stdout}")
                    logger.error(f"STDERR: {stderr}")
                    return False
            
            logger.error("❌ Backend failed to respond within timeout")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error starting backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the Vite frontend development server"""
        logger.info(f"🎨 Starting frontend development server on port {self.frontend_port}...")
          try:
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=self.model_manager_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True  # Use shell for Windows compatibility
            )
            
            # Wait for frontend to start
            for i in range(20):  # 20 second timeout
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
                    stdout, stderr = self.frontend_process.communicate()
                    logger.error(f"❌ Frontend process failed to start:")
                    logger.error(f"STDOUT: {stdout}")
                    logger.error(f"STDERR: {stderr}")
                    return False
            
            logger.warning("⚠️ Frontend may still be starting (taking longer than expected)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error starting frontend: {e}")
            return False
    
    def test_integration(self):
        """Test if the Model Manager is working properly"""
        logger.info("🧪 Testing Model Manager integration...")
        
        try:
            # Test backend health
            response = requests.get(f"http://localhost:{self.backend_port}/health", timeout=5)
            if response.status_code != 200:
                logger.error("❌ Backend health check failed")
                return False
            
            # Test marketplace endpoint
            response = requests.get(f"http://localhost:{self.backend_port}/providers/marketplace/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                model_count = len(data.get("models", []))
                logger.info(f"✅ Marketplace loaded {model_count} models")
            else:
                logger.warning(f"⚠️ Marketplace endpoint returned {response.status_code}")
            
            # Test frontend
            response = requests.get(f"http://localhost:{self.frontend_port}", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Frontend is accessible")
            else:
                logger.warning(f"⚠️ Frontend returned {response.status_code}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            return False
    
    def launch(self):
        """Launch the complete Model Manager system"""
        logger.info("🎯 Launching Optimized Model Manager...")
        
        # Check dependencies
        if not self.check_dependencies():
            logger.error("❌ Dependency check failed")
            return False
        
        # Setup frontend dependencies
        if not self.setup_frontend_dependencies():
            logger.error("❌ Frontend setup failed")
            return False
        
        # Start backend
        if not self.start_backend():
            logger.error("❌ Backend startup failed")
            return False
        
        # Start frontend
        if not self.start_frontend():
            logger.error("❌ Frontend startup failed")
            self.cleanup()
            return False
        
        # Test integration
        if not self.test_integration():
            logger.warning("⚠️ Integration tests failed, but services are running")
        
        logger.info("🎉 Model Manager launched successfully!")
        logger.info(f"📊 Backend: http://localhost:{self.backend_port}")
        logger.info(f"🎨 Frontend: http://localhost:{self.frontend_port}")
        logger.info("🛑 Press Ctrl+C to stop")
        
        return True
    
    def cleanup(self):
        """Stop all processes"""
        logger.info("🧹 Cleaning up processes...")
        
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                logger.info("✅ Backend stopped")
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
                logger.info("🔪 Backend force-killed")
            except Exception as e:
                logger.error(f"❌ Error stopping backend: {e}")
        
        if self.frontend_process:
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
    launcher = OptimizedModelManagerLauncher()
    
    try:
        if launcher.launch():
            # Keep running until interrupted
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        logger.info("🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    finally:
        launcher.cleanup()

if __name__ == "__main__":
    main()
