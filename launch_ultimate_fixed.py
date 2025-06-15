#!/usr/bin/env python3
"""
Fixed Ultimate Copilot Launcher
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

def print_header():
    """Print application header"""
    print("=" * 60)
    print("🚀 ULTIMATE COPILOT - FIXED LAUNCHER")
    print("=" * 60)
    print()

def start_model_manager_backend():
    """Start Model Manager backend"""
    print("🚀 Starting Model Manager backend...")
    
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
        
        time.sleep(3)
        
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
    """Start Model Manager frontend with fixed npm path"""
    print("🚀 Starting Model Manager frontend...")
    
    frontend_dir = Path("frontend/model manager")
    if not frontend_dir.exists():
        print("❌ Model Manager frontend directory not found")
        return None
    
    try:
        # Use absolute path to npm
        npm_cmd = str(Path("nodejs/npm.cmd").resolve())
        print(f"Using npm: {npm_cmd}")
        
        # Start with proper working directory
        process = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=str(frontend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
        
        time.sleep(8)
        
        if process.poll() is None:
            print("✅ Model Manager frontend started!")
            return process
        else:
            print("❌ Model Manager frontend failed to start")
            stdout, stderr = process.communicate()
            if stderr:
                print(f"   Error: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Frontend start error: {e}")
        return None

def start_dashboard_backend():
    """Start dashboard backend"""
    print("🚀 Starting Dashboard backend...")
    
    backend_script = Path("frontend/dashboard_backend_clean.py")
    if not backend_script.exists():
        print("❌ Dashboard backend not found")
        return None
    
    try:
        process = subprocess.Popen(
            [sys.executable, str(backend_script), "--port", "8001"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Dashboard backend started!")
            return process
        else:
            print("❌ Dashboard backend failed to start")
            stdout, stderr = process.communicate()
            if stderr:
                print(f"   Error: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Backend start error: {e}")
        return None

def start_dashboard_frontend():
    """Start dashboard frontend"""
    print("🚀 Starting Dashboard frontend...")
    
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
        
        time.sleep(5)
        
        if process.poll() is None:
            print("✅ Dashboard frontend started!")
            return process
        else:
            print("❌ Dashboard frontend failed to start")
            return None
            
    except Exception as e:
        print(f"❌ Frontend start error: {e}")
        return None

def check_health(url, name):
    """Check service health"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name} is healthy")
            return True
        else:
            print(f"⚠️ {name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name} health check failed: {e}")
        return False

def main():
    """Main launcher function"""
    print_header()
    
    processes = []
    
    # Start Model Manager backend
    print("1️⃣ Starting Model Manager backend...")
    mm_backend = start_model_manager_backend()
    if mm_backend:
        processes.append(("Model Manager Backend", mm_backend))
    
    # Start Model Manager frontend
    print("\n2️⃣ Starting Model Manager frontend...")
    mm_frontend = start_model_manager_frontend()
    if mm_frontend:
        processes.append(("Model Manager Frontend", mm_frontend))
    
    # Start Dashboard backend
    print("\n3️⃣ Starting Dashboard backend...")
    dash_backend = start_dashboard_backend()
    if dash_backend:
        processes.append(("Dashboard Backend", dash_backend))
    
    # Start Dashboard frontend
    print("\n4️⃣ Starting Dashboard frontend...")
    dash_frontend = start_dashboard_frontend()
    if dash_frontend:
        processes.append(("Dashboard Frontend", dash_frontend))
    
    # Health checks
    print("\n5️⃣ Performing health checks...")
    time.sleep(3)
    
    services = [
        ("http://localhost:8002/health", "Model Manager Backend"),
        ("http://localhost:8001/health", "Dashboard Backend"),
        ("http://localhost:8501", "Dashboard Frontend"),
        ("http://localhost:5173", "Model Manager Frontend")
    ]
    
    healthy_count = 0
    for url, name in services:
        if check_health(url, name):
            healthy_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 LAUNCH SUMMARY")
    print("=" * 60)
    print(f"✅ Services started: {len(processes)}")
    print(f"✅ Healthy services: {healthy_count}/{len(services)}")
    
    if healthy_count > 0:
        print("\n🌐 Available URLs:")
        print("   • Dashboard: http://localhost:8501")
        print("   • Dashboard API: http://localhost:8001")
        print("   • Model Manager API: http://localhost:8002")
        print("   • Model Manager UI: http://localhost:5173")
        print("\n🚀 Ultimate Copilot is ready!")
        
        # Keep running
        print("\n⏹️ Press Ctrl+C to stop all services...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping all services...")
            for name, process in processes:
                try:
                    process.terminate()
                    print(f"   Stopped {name}")
                except:
                    pass
            print("✅ All services stopped!")
    else:
        print("❌ No services are healthy. Stopping...")
        for name, process in processes:
            try:
                process.terminate()
            except:
                pass

if __name__ == "__main__":
    main()
