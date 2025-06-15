"""
Dashboard Launcher for Ultimate Copilot System
Starts the Streamlit dashboard on port 8501
"""
import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def start_dashboard():
    """Start the Streamlit dashboard"""
    print("[DASHBOARD] Starting Ultimate Copilot System Dashboard...")
    
    # Change to the project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Dashboard file path
    dashboard_path = project_dir / "frontend" / "dashboard.py"
    
    if not dashboard_path.exists():
        print(f"[ERROR] Dashboard file not found: {dashboard_path}")
        return False
    
    try:
        # Start Streamlit dashboard
        print(f"[INFO] Starting dashboard from: {dashboard_path}")
        print("[INFO] Dashboard will be available at: http://localhost:8501")
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(3)
            webbrowser.open("http://localhost:8501")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_path),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false",
            "--server.headless", "false"
        ])
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to start dashboard: {e}")
        return False

if __name__ == "__main__":
    start_dashboard()
