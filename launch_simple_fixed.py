#!/usr/bin/env python3
"""
Ultimate Copilot Simple Launcher
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

# Virtual environment Python path
PYTHON_EXE = "C:/Users/bcmad/OneDrive/Desktop/agentarmycompforbolt/ultimate_copilot/.venv/Scripts/python.exe"

def print_status(message, status="info"):
    """Print colored status messages"""
    if status == "success":
        print(f"✅ {message}")
    elif status == "error":
        print(f"❌ {message}")
    elif status == "warning":
        print(f"⚠️ {message}")
    else:
        print(f"ℹ️ {message}")

def start_service(name, script_path, port, timeout=10):
    """Start a service and return process"""
    print_status(f"Starting {name}...")
    
    try:
        # Build command
        cmd = [PYTHON_EXE, str(script_path)]
        if port:
            cmd.extend(["--port", str(port)])
            
        print_status(f"Command: {' '.join(cmd)}")
        
        # Start process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for startup
        time.sleep(timeout)
        
        # Check if still running
        if process.poll() is None:
            print_status(f"{name} started successfully", "success")
            return process
        else:
            print_status(f"{name} failed to start", "error")
            stdout, stderr = process.communicate()
            if stdout:
                print(f"  stdout: {stdout[:200]}...")
            if stderr:
                print(f"  stderr: {stderr[:200]}...")
            return None
            
    except Exception as e:
        print_status(f"Error starting {name}: {e}", "error")
        return None

def start_frontend():
    """Start the Model Manager frontend using npm"""
    print_status("Starting Model Manager frontend...")
    
    frontend_dir = Path("frontend/model manager")
    if not frontend_dir.exists():
        print_status("Model Manager frontend directory not found", "error")
        return None
    
    try:
        # Use relative path to npm from the frontend directory
        npm_cmd = "../../nodejs/npm.cmd"
        
        process = subprocess.Popen(
            [npm_cmd, "run", "dev"],
            cwd=str(frontend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        
        # Wait longer for frontend startup
        time.sleep(15)
        
        if process.poll() is None:
            print_status("Model Manager frontend started successfully", "success")
            return process
        else:
            print_status("Model Manager frontend failed to start", "error")
            stdout, stderr = process.communicate()
            if stdout:
                print(f"  stdout: {stdout[:300]}...")
            if stderr:
                print(f"  stderr: {stderr[:300]}...")
            return None
            
    except Exception as e:
        print_status(f"Error starting frontend: {e}", "error")
        return None

def check_health(url, name):
    """Check service health"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print_status(f"{name} health check passed", "success")
            return True
        else:
            print_status(f"{name} health check failed: HTTP {response.status_code}", "warning")
            return False
    except requests.exceptions.RequestException as e:
        print_status(f"{name} health check failed: {e}", "error")
        return False

def main():
    """Main launcher"""
    print("=" * 60)
    print("🚀 ULTIMATE COPILOT - SIMPLE LAUNCHER")
    print("=" * 60)
    
    processes = []
    services = []
    
    # 1. Start Model Manager Backend
    mm_backend_script = Path("frontend/model manager/backend/server_optimized.py")
    mm_backend = start_service("Model Manager Backend", mm_backend_script, 8002, 8)
    if mm_backend:
        processes.append(("Model Manager Backend", mm_backend))
        services.append(("http://localhost:8002/health", "Model Manager Backend"))
    
    # 2. Start Dashboard Backend
    dash_backend_script = Path("frontend/dashboard_backend_clean.py")
    dash_backend = start_service("Dashboard Backend", dash_backend_script, 8001, 10)
    if dash_backend:
        processes.append(("Dashboard Backend", dash_backend))
        services.append(("http://localhost:8001/health", "Dashboard Backend"))
    
    # 3. Start Dashboard Frontend (Streamlit)
    dash_frontend_script = Path("frontend/dashboard.py")
    if dash_frontend_script.exists():
        print_status("Starting Dashboard Frontend (Streamlit)...")
        try:
            dash_frontend = subprocess.Popen(
                [PYTHON_EXE, "-m", "streamlit", "run", str(dash_frontend_script), "--server.port", "8501"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            time.sleep(10)
            if dash_frontend.poll() is None:
                print_status("Dashboard Frontend started successfully", "success")
                processes.append(("Dashboard Frontend", dash_frontend))
                services.append(("http://localhost:8501", "Dashboard Frontend"))
            else:
                print_status("Dashboard Frontend failed to start", "error")
        except Exception as e:
            print_status(f"Error starting Dashboard Frontend: {e}", "error")
    
    # 4. Start Model Manager Frontend
    mm_frontend = start_frontend()
    if mm_frontend:
        processes.append(("Model Manager Frontend", mm_frontend))
        services.append(("http://localhost:5173", "Model Manager Frontend"))
    
    # Health checks
    print("\n" + "=" * 60)
    print("🏥 HEALTH CHECKS")
    print("=" * 60)
    
    time.sleep(5)  # Give services time to fully start
    
    healthy_count = 0
    for url, name in services:
        if check_health(url, name):
            healthy_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Services started: {len(processes)}")
    print(f"Healthy services: {healthy_count}/{len(services)}")
    
    if healthy_count > 0:
        print("\n🌐 Available URLs:")
        print("  • Dashboard:        http://localhost:8501")
        print("  • Dashboard API:    http://localhost:8001")
        print("  • Model Manager API: http://localhost:8002")
        print("  • Model Manager UI:  http://localhost:5173")
        
        print("\n🎉 Ultimate Copilot is ready!")
        print("💡 Open http://localhost:8501 in your browser")
        
        # Keep services running
        print("\n⏹️ Press Ctrl+C to stop all services...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping all services...")
            for name, process in processes:
                try:
                    process.terminate()
                    print_status(f"Stopped {name}")
                except Exception as e:
                    print_status(f"Error stopping {name}: {e}", "warning")
            print_status("All services stopped!", "success")
    else:
        print_status("No services are healthy. Check the logs above.", "error")
        # Clean up
        for name, process in processes:
            try:
                process.terminate()
            except:
                pass

if __name__ == "__main__":
    main()
