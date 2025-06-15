#!/usr/bin/env python3
"""
Start the Model Manager React frontend
"""

import subprocess
import os
import sys
import time

def start_model_manager():
    """Start the React frontend for model manager"""
    model_manager_path = r"c:\Users\bcmad\OneDrive\Desktop\agentarmycompforbolt\ultimate_copilot\frontend\model manager"
    
    if not os.path.exists(model_manager_path):
        print(f"❌ Model manager path not found: {model_manager_path}")
        return False
    
    print(f"📂 Changing to: {model_manager_path}")
    os.chdir(model_manager_path)
    
    # Check if node_modules exists
    if not os.path.exists("node_modules"):
        print("📦 Installing dependencies...")
        subprocess.run(["npm", "install"], check=True)
    
    print("🚀 Starting React development server...")
    
    # Start the development server
    process = subprocess.Popen(
        ["npm", "run", "dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print(f"✅ Started React server with PID: {process.pid}")
    print("🌐 Model Manager should be available at: http://localhost:5173")
    print("⏳ Waiting for server to start...")
    
    # Wait a bit for startup
    time.sleep(5)
    
    # Check if process is still running
    if process.poll() is None:
        print("✅ React server is running successfully!")
        return True
    else:
        stdout, stderr = process.communicate()
        print(f"❌ React server failed to start:")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
        return False

if __name__ == "__main__":
    success = start_model_manager()
    if success:
        print("\n🎉 Model Manager is now running!")
        print("📖 You can now access it from the dashboard's Model Manager tab")
        input("Press Enter to stop the server...")
    else:
        print("\n❌ Failed to start Model Manager")
        sys.exit(1)
