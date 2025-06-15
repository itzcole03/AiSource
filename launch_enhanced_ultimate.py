#!/usr/bin/env python3
"""
Enhanced Ultimate Copilot Launcher with Node.js Auto-Setup
"""

import subprocess
import sys
import os
import time
import requests
import shutil
from pathlib import Path

def print_header():
    """Print application header"""
    print("=" * 60)
    print("🚀 ULTIMATE COPILOT - ENHANCED LAUNCHER")
    print("=" * 60)
    print()

def check_node_js():
    """Check if Node.js is available"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Node.js found: {result.stdout.strip()}")
            
            # Check npm
            try:
                npm_result = subprocess.run(["npm", "--version"], capture_output=True, text=True, timeout=5)
                if npm_result.returncode == 0:
                    print(f"✅ npm found: {npm_result.stdout.strip()}")
                    return True
                else:
                    print("❌ npm not found")
                    return False
            except Exception:
                print("❌ npm not accessible")
                return False
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found (command not found)")
        return False
    except Exception as e:
        print(f"❌ Node.js check failed: {e}")
        return False

def check_local_nodejs():
    """Check if local Node.js installation exists"""
    nodejs_dir = Path("nodejs")
    if nodejs_dir.exists():
        node_exe = nodejs_dir / "node.exe"
        if node_exe.exists():
            try:
                result = subprocess.run([str(node_exe), "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ Local Node.js found: {result.stdout.strip()}")
                    return True
            except:
                pass
    
    print("❌ Local Node.js not found")
    return False

def install_nodejs():
    """Install Node.js locally"""
    print("\n🔧 Installing Node.js locally...")
    try:
        result = subprocess.run([sys.executable, "install_nodejs.py"], 
                              capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            print("✅ Node.js installation completed!")
            return True
        else:
            print(f"❌ Node.js installation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Node.js installation error: {e}")
        return False

def setup_model_manager():
    """Setup Model Manager frontend dependencies"""
    print("\n🔧 Setting up Model Manager frontend...")
    
    frontend_dir = Path("frontend/model manager")
    if not frontend_dir.exists():
        print("❌ Model Manager frontend directory not found")
        return False
    
    try:
        # Get npm command - construct path relative to frontend dir
        npm_cmd = None
        
        # First try system npm
        try:
            result = subprocess.run(["npm.cmd", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                npm_cmd = "npm.cmd"
        except:
            pass
        
        # If system npm not found, try local nodejs
        if not npm_cmd:
            # From frontend dir, nodejs is at ../../nodejs/npm.cmd
            local_npm = Path("../../nodejs/npm.cmd")
            if local_npm.exists():
                npm_cmd = str(local_npm)
        
        if not npm_cmd:
            print("❌ No working npm installation found")
            return False
        
        print(f"Using npm: {npm_cmd}")
        
        # Install dependencies
        print("Installing dependencies...")
        result = subprocess.run([npm_cmd, "install"], 
                              cwd=str(frontend_dir), 
                              capture_output=True, text=True, timeout=300,
                              shell=True)
        
        if result.returncode == 0:
            print("✅ Model Manager dependencies installed!")
            return True
        else:
            print(f"❌ npm install failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

def start_model_manager_backend():
    """Start Model Manager backend"""
    print("\n🚀 Starting Model Manager backend...")
    
    backend_script = Path("frontend/model manager/backend/server_optimized.py")
    if not backend_script.exists():
        backend_script = Path("frontend/model manager/backend/server.py")
    
    if not backend_script.exists():
        print("❌ Model Manager backend not found")
        return None
    
    try:
        process = subprocess.Popen(
            [sys.executable, str(backend_script), "--port", "8002"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Model Manager backend started!")
            return process
        else:
            print("❌ Model Manager backend failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Backend start error: {e}")
        return None

def start_model_manager_frontend():
    """Start Model Manager frontend"""
    print("\n🚀 Starting Model Manager frontend...")
    
    frontend_dir = Path("frontend/model manager")
    if not frontend_dir.exists():
        print("❌ Model Manager frontend directory not found")
        return None
    
    # Check if dependencies are installed
    if not (frontend_dir / "node_modules").exists():
        print("📦 Installing frontend dependencies...")
        if not setup_model_manager():
            return None
    
    try:
        # Get npm command - need to construct path relative to frontend dir
        npm_cmd = None
        
        # First try system npm
        try:
            result = subprocess.run(["npm.cmd", "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                npm_cmd = "npm.cmd"
        except:
            pass
        
        # If system npm not found, try local nodejs
        if not npm_cmd:
            # From frontend dir, nodejs is at ../../nodejs/npm.cmd
            local_npm = Path("../../nodejs/npm.cmd")
            if local_npm.exists():
                npm_cmd = str(local_npm)
        
        if not npm_cmd:
            print("❌ No working npm installation found")
            return None
        
        print(f"Using npm: {npm_cmd}")
        
        # Start the process with proper working directory
        process = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=str(frontend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True  # Use shell for Windows compatibility
        )
        
        # Wait for frontend to start
        time.sleep(8)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Model Manager frontend started!")
            print("   Available at: http://localhost:5173")
            return process
        else:
            print("❌ Model Manager frontend failed to start")
            stdout, stderr = process.communicate()
            if stderr:
                print(f"   Error: {stderr.decode()}")
            if stdout:
                print(f"   Output: {stdout.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Frontend start error: {e}")
        return None

def start_dashboard_backend():
    """Start dashboard backend"""
    print("\n🚀 Starting Dashboard backend...")
    
    backend_script = Path("frontend/dashboard_backend_clean.py")
    if not backend_script.exists():
        backend_script = Path("frontend/dashboard_backend.py")
    
    if not backend_script.exists():
        print("❌ Dashboard backend not found")
        return None
    
    try:
        # Start with explicit port and better error handling
        process = subprocess.Popen(
            [sys.executable, str(backend_script), "--port", "8001"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for startup with longer timeout
        time.sleep(5)
          # Check if running
        if process.poll() is None:
            print("✅ Dashboard backend started!")
            return process
        else:
            print("❌ Dashboard backend failed to start")
            stdout, stderr = process.communicate()
            if stderr:
                print(f"   Error: {stderr.decode()}")
            if stdout:
                print(f"   Output: {stdout.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Dashboard backend start error: {e}")
        return None

def start_dashboard_frontend():
    """Start dashboard frontend"""
    print("\n🚀 Starting Dashboard frontend...")
    
    dashboard_script = Path("frontend/dashboard.py")
    if not dashboard_script.exists():
        print("❌ Dashboard frontend not found")
        return None
    
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", str(dashboard_script), "--server.port", "8501"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait for startup
        time.sleep(5)
        
        # Check if running
        if process.poll() is None:
            print("✅ Dashboard frontend started!")
            print("   Available at: http://localhost:8501")
            return process
        else:
            print("❌ Dashboard frontend failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Dashboard frontend start error: {e}")
        return None

def check_service_health(url, name, timeout=5):
    """Check if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name} is healthy")
            return True
        else:
            print(f"⚠️ {name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name} health check failed: {e}")
        return False

def get_npm_command():
    """Get the appropriate npm command to use"""
    # Check system npm first
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return "npm"
    except:
        pass
    
    # Check local npm
    nodejs_dir = Path("nodejs")
    npm_cmd = nodejs_dir / "npm.cmd"
    if npm_cmd.exists():
        try:
            result = subprocess.run([str(npm_cmd), "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return str(npm_cmd)
        except:
            pass
    
    return None

def main():
    """Main launcher function"""
    print_header()
    
    processes = []
      # Step 1: Check Node.js
    print("1️⃣ Checking Node.js installation...")
    system_nodejs = check_node_js()
    local_nodejs = check_local_nodejs()
    has_nodejs = system_nodejs or local_nodejs
    
    # Check if we can actually use npm
    npm_cmd = get_npm_command()
    has_working_npm = npm_cmd is not None
    
    if has_nodejs and has_working_npm:
        print(f"✅ Node.js ecosystem ready (using: {npm_cmd})")
    elif has_nodejs and not has_working_npm:
        print("⚠️ Node.js found but npm not working properly")
        has_nodejs = False
    elif not has_nodejs:
        print("❌ No Node.js installation found")
    
    if not has_nodejs:
        print("\n🔧 Node.js not found. Would you like to install it?")
        print("   This will download and install Node.js locally (no system changes)")
        
        choice = input("Install Node.js locally? (y/n): ").lower().strip()
        if choice in ['y', 'yes']:
            if install_nodejs():
                has_nodejs = check_local_nodejs()
            
        if not has_nodejs:
            print("\n⚠️ Continuing without Node.js - Model Manager frontend will use static version")
    
    # Step 2: Start Model Manager backend
    print("\n2️⃣ Starting Model Manager backend...")
    mm_backend = start_model_manager_backend()
    if mm_backend:
        processes.append(("Model Manager Backend", mm_backend))
    
    # Step 3: Start Model Manager frontend (if Node.js available)
    if has_nodejs:
        print("\n3️⃣ Starting Model Manager frontend...")
        mm_frontend = start_model_manager_frontend()
        if mm_frontend:
            processes.append(("Model Manager Frontend", mm_frontend))
    else:
        print("\n3️⃣ Skipping Model Manager frontend (Node.js not available)")
        print("   ℹ️ Static Model Manager will be available in dashboard")
    
    # Step 4: Start Dashboard backend
    print("\n4️⃣ Starting Dashboard backend...")
    dash_backend = start_dashboard_backend()
    if dash_backend:
        processes.append(("Dashboard Backend", dash_backend))
    
    # Step 5: Start Dashboard frontend
    print("\n5️⃣ Starting Dashboard frontend...")
    dash_frontend = start_dashboard_frontend()
    if dash_frontend:
        processes.append(("Dashboard Frontend", dash_frontend))
    
    # Step 6: Health checks
    print("\n6️⃣ Performing health checks...")
    time.sleep(3)
    
    services = [
        ("http://localhost:8002/health", "Model Manager Backend"),
        ("http://localhost:8001/health", "Dashboard Backend"),
        ("http://localhost:8501", "Dashboard Frontend")
    ]
    
    if has_nodejs:
        services.append(("http://localhost:5173", "Model Manager Frontend"))
    
    healthy_services = 0
    for url, name in services:
        if check_service_health(url, name):
            healthy_services += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 LAUNCH SUMMARY")
    print("=" * 60)
    print(f"✅ Services started: {len(processes)}")
    print(f"✅ Healthy services: {healthy_services}/{len(services)}")
    print()
    
    if healthy_services > 0:
        print("🌐 Available URLs:")
        print("   • Dashboard: http://localhost:8501")
        print("   • Dashboard API: http://localhost:8001")
        print("   • Model Manager API: http://localhost:8002")
        if has_nodejs:
            print("   • Model Manager UI: http://localhost:5173")
        else:
            print("   • Static Model Manager: Available in Dashboard tab")
        print()
        
        print("🚀 Ultimate Copilot is ready! Open http://localhost:8501 in your browser.")
        
        # Keep processes running
        print("\n⏹️ Press Ctrl+C to stop all services...")
        try:
            while True:
                time.sleep(1)
                # Check if any process died
                for name, process in processes:
                    if process.poll() is not None:
                        print(f"⚠️ {name} process ended unexpectedly")
        except KeyboardInterrupt:
            print("\n🛑 Stopping all services...")
            for name, process in processes:
                try:
                    process.terminate()
                    print(f"   Stopped {name}")
                except:
                    pass
            print("✅ All services stopped. Goodbye!")
    else:
        print("❌ No services are healthy. Please check the logs and try again.")
        for name, process in processes:
            try:
                process.terminate()
            except:
                pass

if __name__ == "__main__":
    main()
