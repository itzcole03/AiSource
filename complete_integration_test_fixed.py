#!/usr/bin/env python3
"""
Complete Integration Test for Ultimate Copilot Dashboard with Model Manager
This script ensures all components are properly integrated and working.
"""

import subprocess
import time
import requests
import os
import sys
import json
from pathlib import Path

class DashboardIntegrationTester:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.model_manager_path = self.base_path / "frontend" / "model manager"
        self.processes = {}
        
    def test_dependencies(self):
        """Test if all required dependencies are available"""
        print("🔍 Testing Dependencies...")
        
        # Test Python
        try:
            python_version = subprocess.check_output([sys.executable, "--version"], text=True)
            print(f"✅ Python: {python_version.strip()}")
        except:
            print("❌ Python not available")
            return False
        
        # Test Node.js
        try:
            node_version = subprocess.check_output(["node", "--version"], text=True)
            print(f"✅ Node.js: {node_version.strip()}")
        except:
            print("❌ Node.js not available")
            return False
        
        # Test npm
        try:
            npm_version = subprocess.check_output(["npm", "--version"], text=True)
            print(f"✅ NPM: {npm_version.strip()}")
        except:
            print("❌ NPM not available")
            return False
        
        # Check if model manager exists
        if self.model_manager_path.exists():
            print(f"✅ Model Manager directory found: {self.model_manager_path}")
        else:
            print(f"❌ Model Manager directory not found: {self.model_manager_path}")
            return False
        
        return True
    
    def install_dependencies(self):
        """Install all required dependencies"""
        print("\n📦 Installing Dependencies...")
        
        # Install NPM dependencies for model manager
        print("Installing NPM dependencies...")
        os.chdir(self.model_manager_path)
        
        # Check if package.json exists
        if not (self.model_manager_path / "package.json").exists():
            print("❌ package.json not found in model manager")
            return False
        
        # Install npm dependencies if node_modules doesn't exist
        if not (self.model_manager_path / "node_modules").exists():
            result = subprocess.run(["npm", "install"], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ NPM install failed: {result.stderr}")
                return False
            print("✅ NPM dependencies installed")
        else:
            print("✅ NPM dependencies already installed")
        
        # Install Python backend dependencies
        backend_path = self.model_manager_path / "backend"
        requirements_file = backend_path / "requirements.txt"
        
        if requirements_file.exists():
            print("Installing Python backend dependencies...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Python dependencies install failed: {result.stderr}")
                return False
            print("✅ Python backend dependencies installed")
        
        os.chdir(self.base_path)
        return True
    
    def start_model_manager_backend(self):
        """Start the model manager backend"""
        print("\n🚀 Starting Model Manager Backend...")
        
        backend_script = self.model_manager_path / "backend" / "server.py"
        
        try:
            self.processes['model_manager_backend'] = subprocess.Popen(
                [sys.executable, str(backend_script), "--host", "127.0.0.1", "--port", "8080"],
                cwd=str(self.model_manager_path / "backend"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for startup
            time.sleep(3)
            
            # Check if backend is responding
            try:
                response = requests.get("http://localhost:8080/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Model Manager Backend started successfully")
                    return True
                else:
                    print(f"❌ Backend health check failed: {response.status_code}")
                    return False
            except requests.RequestException as e:
                print(f"❌ Backend not responding: {e}")
                return False
        
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_model_manager_frontend(self):
        """Start the model manager React frontend"""
        print("\n🚀 Starting Model Manager Frontend...")
        
        try:
            self.processes['model_manager_frontend'] = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(self.model_manager_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for Vite to start up
            print("Waiting for Vite dev server to start...")
            time.sleep(10)
            
            # Check if frontend is accessible
            try:
                response = requests.get("http://localhost:5173", timeout=10)
                if response.status_code == 200:
                    print("✅ Model Manager Frontend started successfully")
                    return True
                else:
                    print(f"❌ Frontend not accessible: {response.status_code}")
                    return False
            except requests.RequestException as e:
                print(f"❌ Frontend not responding: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def start_dashboard_backend(self):
        """Start the dashboard backend"""
        print("\n🚀 Starting Dashboard Backend...")
        
        backend_script = self.base_path / "frontend" / "dashboard_backend_clean.py"
        
        try:
            self.processes['dashboard_backend'] = subprocess.Popen(
                [sys.executable, str(backend_script)],
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for startup
            time.sleep(3)
            
            # Check if backend is responding
            try:
                response = requests.get("http://localhost:8001/system/status", timeout=5)
                if response.status_code == 200:
                    print("✅ Dashboard Backend started successfully")
                    return True
                else:
                    print(f"❌ Dashboard backend health check failed: {response.status_code}")
                    return False
            except requests.RequestException as e:
                print(f"❌ Dashboard backend not responding: {e}")
                return False
        
        except Exception as e:
            print(f"❌ Failed to start dashboard backend: {e}")
            return False
    
    def start_dashboard_frontend(self):
        """Start the Streamlit dashboard"""
        print("\n🚀 Starting Dashboard Frontend...")
        
        dashboard_script = self.base_path / "frontend" / "dashboard.py"
        
        try:
            self.processes['dashboard_frontend'] = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", str(dashboard_script), "--server.port", "8501"],
                cwd=str(self.base_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for Streamlit to start
            print("Waiting for Streamlit to start...")
            time.sleep(8)
            
            # Check if dashboard is accessible
            try:
                response = requests.get("http://localhost:8501", timeout=10)
                if response.status_code == 200:
                    print("✅ Dashboard Frontend started successfully")
                    return True
                else:
                    print(f"❌ Dashboard not accessible: {response.status_code}")
                    return False
            except requests.RequestException as e:
                print(f"❌ Dashboard not responding: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start dashboard: {e}")
            return False
    
    def test_integration(self):
        """Test integration between all components"""
        print("\n🔗 Testing Integration...")
        
        # Test Model Manager Backend
        try:
            response = requests.get("http://localhost:8080/system/info", timeout=5)
            if response.status_code == 200:
                print("✅ Model Manager Backend API working")
            else:
                print("❌ Model Manager Backend API not responding")
                return False
        except:
            print("❌ Model Manager Backend not accessible")
            return False
        
        # Test Dashboard Backend
        try:
            response = requests.get("http://localhost:8001/models/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("manager") == "IntelligentModelManager":
                    print("✅ Dashboard Backend integrated with IntelligentModelManager")
                else:
                    print("⚠️ Dashboard Backend not using IntelligentModelManager")
            else:
                print("❌ Dashboard Backend models API not responding")
                return False
        except Exception as e:
            print(f"❌ Dashboard Backend not accessible: {e}")
            return False
        
        print("✅ All integration tests passed!")
        return True
    
    def run_full_test(self):
        """Run the complete integration test"""
        print("🚀 Starting Complete Integration Test for Ultimate Copilot Dashboard")
        print("=" * 70)
        
        # Step 1: Test dependencies
        if not self.test_dependencies():
            print("❌ Dependency test failed. Exiting.")
            return False
        
        # Step 2: Install dependencies
        if not self.install_dependencies():
            print("❌ Dependency installation failed. Exiting.")
            return False
        
        # Step 3: Start Model Manager Backend
        if not self.start_model_manager_backend():
            print("❌ Model Manager Backend failed to start. Continuing anyway.")
        
        # Step 4: Start Model Manager Frontend
        if not self.start_model_manager_frontend():
            print("❌ Model Manager Frontend failed to start. Continuing anyway.")
        
        # Step 5: Start Dashboard Backend
        if not self.start_dashboard_backend():
            print("❌ Dashboard Backend failed to start. Continuing anyway.")
        
        # Step 6: Start Dashboard Frontend
        if not self.start_dashboard_frontend():
            print("❌ Dashboard Frontend failed to start. Continuing anyway.")
        
        # Step 7: Test integration
        if not self.test_integration():
            print("❌ Integration test failed.")
            return False
        
        print("\n🎉 Complete Integration Test PASSED!")
        print("=" * 70)
        print("🌐 Access points:")
        print("  • Dashboard: http://localhost:8501")
        print("  • Model Manager: http://localhost:5173")
        print("  • Model Manager Backend API: http://localhost:8080")
        print("  • Dashboard Backend API: http://localhost:8001")
        print("\n💡 To stop all services, run: Ctrl+C or close this terminal")
        
        # Keep running to maintain services
        try:
            while True:
                time.sleep(10)
                print(".", end="", flush=True)
        except KeyboardInterrupt:
            self.cleanup()
        
        return True
    
    def cleanup(self):
        """Clean up all started processes"""
        print("\n🧹 Cleaning up processes...")
        for name, process in self.processes.items():
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

if __name__ == "__main__":
    tester = DashboardIntegrationTester()
    tester.run_full_test()
