#!/usr/bin/env python3
"""
Ultimate Copilot Status Report and Manual Setup Guide
"""

from pathlib import Path
import json

def check_file_structure():
    """Check if all required files exist"""
    print("🔍 CHECKING FILE STRUCTURE")
    print("=" * 50)
    
    required_files = [
        "frontend/model manager/backend/server_optimized.py",
        "frontend/model manager/backend/server.py", 
        "frontend/dashboard_backend_clean.py",
        "frontend/dashboard.py",
        "frontend/model manager/package.json",
        "frontend/model manager/vite.config.ts",
        "nodejs/npm.cmd",
        "intelligent_model_manager.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    return missing_files

def check_python_environment():
    """Check Python environment"""
    print("\n🐍 PYTHON ENVIRONMENT")
    print("=" * 50)
    
    venv_python = Path(".venv/Scripts/python.exe")
    if venv_python.exists():
        print(f"✅ Virtual environment Python: {venv_python.resolve()}")
    else:
        print("❌ Virtual environment not found")
    
    # Check if packages are installed
    try:
        import fastapi
        print(f"✅ FastAPI: {fastapi.__version__}")
    except ImportError:
        print("❌ FastAPI not installed")
    
    try:
        import uvicorn
        print(f"✅ Uvicorn: {uvicorn.__version__}")
    except ImportError:
        print("❌ Uvicorn not installed")
    
    try:
        import streamlit
        print(f"✅ Streamlit: {streamlit.__version__}")
    except ImportError:
        print("❌ Streamlit not installed")

def check_nodejs():
    """Check Node.js setup"""
    print("\n🟢 NODE.JS SETUP")
    print("=" * 50)
    
    nodejs_dir = Path("nodejs")
    if nodejs_dir.exists():
        print(f"✅ Node.js directory: {nodejs_dir.resolve()}")
        
        npm_cmd = nodejs_dir / "npm.cmd"
        if npm_cmd.exists():
            print(f"✅ npm command: {npm_cmd.resolve()}")
        else:
            print("❌ npm.cmd not found")
    else:
        print("❌ Node.js directory not found")
    
    # Check Model Manager frontend
    frontend_dir = Path("frontend/model manager")
    if frontend_dir.exists():
        print(f"✅ Model Manager frontend: {frontend_dir.resolve()}")
        
        node_modules = frontend_dir / "node_modules"
        if node_modules.exists():
            print("✅ Dependencies installed (node_modules exists)")
        else:
            print("⚠️ Dependencies not installed (run npm install)")
    else:
        print("❌ Model Manager frontend not found")

def create_manual_instructions():
    """Create manual setup instructions"""
    print("\n📋 MANUAL SETUP INSTRUCTIONS")
    print("=" * 50)
    
    instructions = """
To manually start Ultimate Copilot, follow these steps:

1. 🚀 START MODEL MANAGER BACKEND:
   Open Command Prompt #1 and run:
   cd C:\\Users\\bcmad\\OneDrive\\Desktop\\agentarmycompforbolt\\ultimate_copilot
   .venv\\Scripts\\python.exe "frontend\\model manager\\backend\\server_optimized.py" --port 8002

2. 🚀 START DASHBOARD BACKEND:
   Open Command Prompt #2 and run:
   cd C:\\Users\\bcmad\\OneDrive\\Desktop\\agentarmycompforbolt\\ultimate_copilot
   .venv\\Scripts\\python.exe "frontend\\dashboard_backend_clean.py" --port 8001

3. 🚀 START DASHBOARD FRONTEND:
   Open Command Prompt #3 and run:
   cd C:\\Users\\bcmad\\OneDrive\\Desktop\\agentarmycompforbolt\\ultimate_copilot
   .venv\\Scripts\\python.exe -m streamlit run "frontend\\dashboard.py" --server.port 8501

4. 🚀 START MODEL MANAGER FRONTEND:
   Open Command Prompt #4 and run:
   cd C:\\Users\\bcmad\\OneDrive\\Desktop\\agentarmycompforbolt\\ultimate_copilot\\frontend\\model manager
   ..\\..\\nodejs\\npm.cmd run dev

5. 🌐 ACCESS THE SYSTEM:
   Open your browser and go to: http://localhost:8501
   
   Available URLs:
   • Dashboard:          http://localhost:8501
   • Dashboard API:      http://localhost:8001/docs  
   • Model Manager API:  http://localhost:8002/docs
   • Model Manager UI:   http://localhost:5173

6. 🔍 TROUBLESHOOTING:
   - If npm install is needed: cd "frontend\\model manager" && ..\\..\\nodejs\\npm.cmd install
   - Check if ports are free: netstat -an | findstr :8001
   - View service logs in the command prompt windows
   """
    
    print(instructions)
    
    # Save to file
    with open("MANUAL_STARTUP_INSTRUCTIONS.txt", "w") as f:
        f.write(instructions)
    print("💾 Instructions saved to: MANUAL_STARTUP_INSTRUCTIONS.txt")

def create_batch_files():
    """Create individual batch files for each service"""
    print("\n📂 CREATING INDIVIDUAL BATCH FILES")
    print("=" * 50)
    
    batch_files = {
        "start_model_manager_backend.bat": '''@echo off
echo Starting Model Manager Backend...
cd /d "C:\\Users\\bcmad\\OneDrive\\Desktop\\agentarmycompforbolt\\ultimate_copilot"
.venv\\Scripts\\python.exe "frontend\\model manager\\backend\\server_optimized.py" --port 8002
pause''',
        
        "start_dashboard_backend.bat": '''@echo off
echo Starting Dashboard Backend...
cd /d "C:\\Users\\bcmad\\OneDrive\\Desktop\\agentarmycompforbolt\\ultimate_copilot"
.venv\\Scripts\\python.exe "frontend\\dashboard_backend_clean.py" --port 8001
pause''',
        
        "start_dashboard_frontend.bat": '''@echo off
echo Starting Dashboard Frontend...
cd /d "C:\\Users\\bcmad\\OneDrive\\Desktop\\agentarmycompforbolt\\ultimate_copilot"
.venv\\Scripts\\python.exe -m streamlit run "frontend\\dashboard.py" --server.port 8501
pause''',
        
        "start_model_manager_frontend.bat": '''@echo off
echo Starting Model Manager Frontend...
cd /d "C:\\Users\\bcmad\\OneDrive\\Desktop\\agentarmycompforbolt\\ultimate_copilot\\frontend\\model manager"
..\\..\\nodejs\\npm.cmd run dev
pause''',
        
        "install_frontend_deps.bat": '''@echo off
echo Installing Model Manager Frontend Dependencies...
cd /d "C:\\Users\\bcmad\\OneDrive\\Desktop\\agentarmycompforbolt\\ultimate_copilot\\frontend\\model manager"
..\\..\\nodejs\\npm.cmd install
pause'''
    }
    
    for filename, content in batch_files.items():
        with open(filename, "w") as f:
            f.write(content)
        print(f"✅ Created: {filename}")

def main():
    """Main status check"""
    print("🎯 ULTIMATE COPILOT STATUS REPORT")
    print("=" * 60)
    
    missing_files = check_file_structure()
    check_python_environment()
    check_nodejs()
    
    print(f"\n📊 SUMMARY")
    print("=" * 50)
    if missing_files:
        print(f"❌ Missing {len(missing_files)} required files")
        for file in missing_files:
            print(f"   - {file}")
    else:
        print("✅ All required files present")
    
    create_manual_instructions()
    create_batch_files()
    
    print(f"\n🎉 STATUS REPORT COMPLETE!")
    print("=" * 50)
    print("📁 Created files:")
    print("   • MANUAL_STARTUP_INSTRUCTIONS.txt")
    print("   • start_model_manager_backend.bat")
    print("   • start_dashboard_backend.bat") 
    print("   • start_dashboard_frontend.bat")
    print("   • start_model_manager_frontend.bat")
    print("   • install_frontend_deps.bat")
    print("\n💡 You can now manually start services using the batch files!")

if __name__ == "__main__":
    main()
