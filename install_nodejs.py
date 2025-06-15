#!/usr/bin/env python3
"""
Node.js installer and setup script for Windows
"""

import subprocess
import sys
import os
import urllib.request
import tempfile
import zipfile
import shutil
from pathlib import Path

def download_nodejs():
    """Download Node.js portable version for Windows"""
    print("Downloading Node.js...")
    
    # Node.js portable download URL for Windows
    node_version = "20.11.0"
    if sys.maxsize > 2**32:  # 64-bit
        url = f"https://nodejs.org/dist/v{node_version}/node-v{node_version}-win-x64.zip"
        folder_name = f"node-v{node_version}-win-x64"
    else:  # 32-bit
        url = f"https://nodejs.org/dist/v{node_version}/node-v{node_version}-win-x86.zip"
        folder_name = f"node-v{node_version}-win-x86"
    
    # Download to temp directory
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "nodejs.zip")
        
        try:
            urllib.request.urlretrieve(url, zip_path)
            print("Download complete!")
            
            # Extract
            print("Extracting Node.js...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Move to local directory
            nodejs_dir = Path("nodejs")
            if nodejs_dir.exists():
                shutil.rmtree(nodejs_dir)
            
            extracted_path = os.path.join(temp_dir, folder_name)
            shutil.move(extracted_path, nodejs_dir)
            
            print(f"Node.js installed to: {nodejs_dir.absolute()}")
            return nodejs_dir.absolute()
            
        except Exception as e:
            print(f"Error downloading Node.js: {e}")
            return None

def setup_environment():
    """Setup Node.js environment"""
    nodejs_dir = Path("nodejs")
    
    if not nodejs_dir.exists():
        print("Node.js not found, downloading...")
        nodejs_path = download_nodejs()
        if not nodejs_path:
            return False
    else:
        nodejs_path = nodejs_dir.absolute()
    
    # Add to PATH for this session
    node_bin = nodejs_path
    current_path = os.environ.get('PATH', '')
    if str(node_bin) not in current_path:
        os.environ['PATH'] = f"{node_bin};{current_path}"
    
    print(f"Node.js setup complete at: {nodejs_path}")
    
    # Test Node.js
    try:
        result = subprocess.run([str(nodejs_path / "node.exe"), "--version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"Node.js version: {result.stdout.strip()}")
            
            # Test npm
            npm_result = subprocess.run([str(nodejs_path / "npm.cmd"), "--version"], 
                                      capture_output=True, text=True, timeout=10)
            if npm_result.returncode == 0:
                print(f"npm version: {npm_result.stdout.strip()}")
                return True
            else:
                print("npm not available")
                return False
        else:
            print("Node.js test failed")
            return False
    except Exception as e:
        print(f"Error testing Node.js: {e}")
        return False

def install_model_manager_deps():
    """Install Model Manager frontend dependencies"""
    nodejs_dir = Path("nodejs")
    if not nodejs_dir.exists():
        if not setup_environment():
            return False
    
    frontend_dir = Path("frontend/model manager")
    if not frontend_dir.exists():
        print("Model Manager frontend directory not found")
        return False
    
    print("Installing Model Manager dependencies...")
    try:
        npm_path = nodejs_dir / "npm.cmd"
        result = subprocess.run([str(npm_path), "install"], 
                              cwd=frontend_dir, 
                              capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("Dependencies installed successfully!")
            return True
        else:
            print(f"npm install failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False

def create_launcher_scripts():
    """Create launcher scripts that use local Node.js"""
    nodejs_dir = Path("nodejs")
    
    # Create Windows batch file for Model Manager frontend
    batch_content = f"""@echo off
cd /d "{Path('frontend/model manager').absolute()}"
"{nodejs_dir.absolute() / 'npm.cmd'}" run dev
pause
"""
    
    with open("launch_model_manager_frontend.bat", "w") as f:
        f.write(batch_content)
    
    print("Created launch_model_manager_frontend.bat")
    
    # Create Python launcher
    launcher_content = f'''#!/usr/bin/env python3
"""
Launch Model Manager frontend with local Node.js
"""

import subprocess
import os
from pathlib import Path

def launch_frontend():
    nodejs_dir = Path("{nodejs_dir}")
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
        print(f"Frontend started with PID: {{process.pid}}")
        print("Frontend should be available at: http://localhost:5173")
        return True
    except Exception as e:
        print(f"Error starting frontend: {{e}}")
        return False

if __name__ == "__main__":
    launch_frontend()
'''
    
    with open("launch_model_manager_frontend.py", "w") as f:
        f.write(launcher_content)
    
    print("Created launch_model_manager_frontend.py")

def main():
    """Main installer function"""
    print("Node.js Installation and Setup")
    print("=" * 40)
    
    if setup_environment():
        print("\nNode.js setup successful!")
        
        # Install dependencies
        if install_model_manager_deps():
            print("\nModel Manager dependencies installed!")
        else:
            print("\nWarning: Could not install Model Manager dependencies")
        
        # Create launcher scripts
        create_launcher_scripts()
        
        print("\nSetup complete! You can now:")
        print("1. Run: launch_model_manager_frontend.bat")
        print("2. Or run: python launch_model_manager_frontend.py")
        
    else:
        print("\nNode.js setup failed. Please install Node.js manually from https://nodejs.org/")

if __name__ == "__main__":
    main()
