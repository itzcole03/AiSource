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
            print(f"✅ Model Manager found at: {self.model_manager_path}")
        else:
            print(f"❌ Model Manager not found at: {self.model_manager_path}")
            return False
        
        return True
    
    def setup_model_manager(self):
        """Setup the model manager dependencies"""
        print("\n📦 Setting up Model Manager...")
        
        os.chdir(self.model_manager_path)
        
        # Install npm dependencies
        if not (self.model_manager_path / "node_modules").exists():
            print("Installing NPM dependencies...")
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
            ], capture_output=True, text=True)            if result.returncode != 0:
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
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for startup
            time.sleep(5)
            
            # Test if it's responding
            try:
                response = requests.get("http://localhost:8080/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Model Manager Backend started successfully on port 8080")
                    return True
                else:
                    print(f"❌ Model Manager Backend not responding: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Model Manager Backend not reachable: {e}")
                
        except Exception as e:
            print(f"❌ Failed to start Model Manager Backend: {e}")
        
        return False
    
    def start_model_manager_frontend(self):
        """Start the model manager React frontend"""
        print("\n🌐 Starting Model Manager Frontend...")
        
        try:
            self.processes['model_manager_frontend'] = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=str(self.model_manager_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for startup
            time.sleep(10)
            
            # Test if it's responding
            try:
                response = requests.get("http://localhost:5173", timeout=5)
                if response.status_code == 200:
                    print("✅ Model Manager Frontend started successfully on port 5173")
                    return True
                else:
                    print(f"❌ Model Manager Frontend not responding: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Model Manager Frontend not reachable: {e}")
                
        except Exception as e:
            print(f"❌ Failed to start Model Manager Frontend: {e}")
        
        return False
    
    def start_dashboard_backend(self):
        """Start the main dashboard backend"""
        print("\n🔧 Starting Dashboard Backend...")
        
        backend_script = self.base_path / "frontend" / "dashboard_backend_clean.py"
        
        try:
            self.processes['dashboard_backend'] = subprocess.Popen(
                [sys.executable, str(backend_script), "--host", "127.0.0.1", "--port", "8001"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for startup
            time.sleep(5)
            
            # Test if it's responding
            try:
                response = requests.get("http://localhost:8001/health", timeout=5)
                if response.status_code == 200:
                    print("✅ Dashboard Backend started successfully on port 8001")
                    return True
                else:
                    print(f"❌ Dashboard Backend not responding: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Dashboard Backend not reachable: {e}")
                
        except Exception as e:
            print(f"❌ Failed to start Dashboard Backend: {e}")
        
        return False
    
    def start_dashboard_frontend(self):
        """Start the main dashboard frontend"""
        print("\n📱 Starting Dashboard Frontend...")
        
        dashboard_script = self.base_path / "frontend" / "dashboard.py"
        
        try:
            self.processes['dashboard_frontend'] = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", str(dashboard_script), 
                 "--server.port=8502", "--server.address=127.0.0.1"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for startup
            time.sleep(10)
            
            # Test if it's responding
            try:
                response = requests.get("http://localhost:8502", timeout=5)
                if response.status_code == 200:
                    print("✅ Dashboard Frontend started successfully on port 8502")
                    return True
                else:
                    print(f"❌ Dashboard Frontend not responding: {response.status_code}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Dashboard Frontend not reachable: {e}")
                
        except Exception as e:
            print(f"❌ Failed to start Dashboard Frontend: {e}")
        
        return False
    
    def test_integration(self):
        """Test the integration between all components"""
        print("\n🔗 Testing Integration...")
        
        tests_passed = 0
        total_tests = 4
        
        # Test 1: Dashboard Backend Health
        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            if response.status_code == 200:
                print("✅ Dashboard Backend health check passed")
                tests_passed += 1
            else:
                print("❌ Dashboard Backend health check failed")
        except:
            print("❌ Dashboard Backend not reachable")
        
        # Test 2: Model Manager Backend Health
        try:
            response = requests.get("http://localhost:8080/health", timeout=5)
            if response.status_code == 200:
                print("✅ Model Manager Backend health check passed")
                tests_passed += 1
            else:
                print("❌ Model Manager Backend health check failed")
        except:
            print("❌ Model Manager Backend not reachable")
        
        # Test 3: Dashboard Model Status (should use Intelligent Model Manager)
        try:
            response = requests.get("http://localhost:8001/models/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("manager") == "IntelligentModelManager":
                    print("✅ Dashboard is using Intelligent Model Manager")
                    tests_passed += 1
                else:
                    print(f"❌ Dashboard using wrong manager: {data.get('manager')}")
            else:
                print("❌ Dashboard model status failed")
        except Exception as e:
            print(f"❌ Dashboard model status error: {e}")
        
        # Test 4: Agent System
        try:
            response = requests.get("http://localhost:8001/agents/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("agent_manager_available"):
                    print("✅ Agent system is available")
                    tests_passed += 1
                else:
                    print("❌ Agent system not available")
            else:
                print("❌ Agent status check failed")
        except:
            print("❌ Agent status not reachable")
        
        print(f"\n📊 Integration Test Results: {tests_passed}/{total_tests} tests passed")
        return tests_passed == total_tests
    
    def display_status(self):
        """Display the current status of all components"""
        print("\n📋 System Status:")
        print("=" * 50)
        
        services = [
            ("Dashboard Frontend", "http://localhost:8502"),
            ("Dashboard Backend", "http://localhost:8001"),
            ("Model Manager Frontend", "http://localhost:5173"),
            ("Model Manager Backend", "http://localhost:8080")
        ]
        
        for name, url in services:
            try:
                response = requests.get(f"{url.replace('localhost:5173', 'localhost:5173')}", timeout=2)
                if response.status_code == 200:
                    print(f"✅ {name}: Running at {url}")
                else:
                    print(f"❌ {name}: Not responding ({response.status_code})")
            except:
                print(f"❌ {name}: Not reachable at {url}")
        
        print("\n🌐 Access URLs:")
        print("• Main Dashboard: http://localhost:8502")
        print("• Model Manager: http://localhost:5173")
        print("• Dashboard API: http://localhost:8001")
        print("• Model Manager API: http://localhost:8080")
    
    def cleanup(self):
        """Stop all started processes"""
        print("\n🧹 Cleaning up processes...")
        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Stopped {name}")
            except:
                try:
                    process.kill()
                    print(f"🔥 Force killed {name}")
                except:
                    print(f"❌ Failed to stop {name}")
    
    def run_full_integration(self):
        """Run the complete integration setup"""
        print("🚀 Ultimate Copilot Dashboard - Full Integration Test")
        print("=" * 60)
        
        try:
            # Step 1: Test dependencies
            if not self.test_dependencies():
                print("❌ Dependency test failed")
                return False
            
            # Step 2: Setup Model Manager
            if not self.setup_model_manager():
                print("❌ Model Manager setup failed")
                return False
            
            # Step 3: Start all services
            services_started = 0
            if self.start_model_manager_backend():
                services_started += 1
            if self.start_dashboard_backend():
                services_started += 1
            if self.start_model_manager_frontend():
                services_started += 1
            if self.start_dashboard_frontend():
                services_started += 1
            
            print(f"\n📊 Started {services_started}/4 services")
            
            # Step 4: Test integration
            if services_started >= 2:  # At least dashboard components
                time.sleep(5)  # Allow services to fully start
                integration_success = self.test_integration()
                
                # Step 5: Display final status
                self.display_status()
                
                if integration_success:
                    print("\n🎉 INTEGRATION SUCCESSFUL!")
                    print("All components are running and properly integrated.")
                    return True
                else:
                    print("\n⚠️ PARTIAL SUCCESS")
                    print("Some components started but integration tests failed.")
                    return False
            else:
                print("\n❌ INTEGRATION FAILED")
                print("Could not start enough services for integration.")
                return False
                
        except KeyboardInterrupt:
            print("\n⚠️ Integration interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Integration failed with error: {e}")
            return False

def main():
    tester = DashboardIntegrationTester()
    
    try:
        success = tester.run_full_integration()
        
        if success:
            print("\n✨ Integration complete! Press Ctrl+C to stop all services.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()
