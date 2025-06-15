#!/usr/bin/env python3
"""
Simple Model Manager Backend Launcher with Enhanced Port Detection
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🚀 Starting Model Manager Backend with Auto Port Detection")
    print("=" * 60)
    
    # Navigate to backend directory
    backend_path = Path(__file__).parent / "frontend" / "model manager" / "backend"
    server_script = backend_path / "server.py"
    
    if not server_script.exists():
        print(f"❌ Backend script not found: {server_script}")
        return False
    
    print(f"📁 Backend path: {backend_path}")
    print(f"🐍 Python: {sys.executable}")
    print("🔄 Starting server...")
    
    # Start the server
    try:
        result = subprocess.run([
            sys.executable, str(server_script), 
            "--host", "127.0.0.1", 
            "--port", "8080"
        ], cwd=str(backend_path), capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ Server started successfully!")
        else:
            print(f"❌ Server failed with return code: {result.returncode}")
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
