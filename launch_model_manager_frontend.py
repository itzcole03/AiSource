#!/usr/bin/env python3
"""
Launch Model Manager frontend with local Node.js
"""

import subprocess
import os
from pathlib import Path

def launch_frontend():
    nodejs_dir = Path("nodejs")
    frontend_dir = Path("frontend/model manager")
    
    if not nodejs_dir.exists():
        print("Node.js not found. Run install_nodejs.py first.")
        return False
    
    if not frontend_dir.exists():
        print("Model Manager frontend not found.")
        return False
    
    print("Starting Model Manager frontend...")
    try:
        npm_path = nodejs_dir / "npm.cmd"
        process = subprocess.Popen([str(npm_path), "run", "dev"], 
                                 cwd=frontend_dir)
        print(f"Frontend started with PID: {process.pid}")
        print("Frontend should be available at: http://localhost:5173")
        return True
    except Exception as e:
        print(f"Error starting frontend: {e}")
        return False

if __name__ == "__main__":
    launch_frontend()
