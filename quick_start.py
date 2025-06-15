#!/usr/bin/env python3
"""
Quick Start Ultimate Copilot Dashboard

Simple launcher that works from anywhere and handles everything automatically.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Quick start the dashboard"""
    try:
        # Find the Ultimate Copilot project directory
        script_dir = Path(__file__).parent
        project_root = None
        
        # Check if we're already in the project root
        if (script_dir / "frontend" / "dashboard.py").exists():
            project_root = script_dir
        else:
            # Look for the project directory
            current = Path.cwd()
            while current.parent != current:
                if (current / "frontend" / "dashboard.py").exists():
                    project_root = current
                    break
                current = current.parent
        
        if not project_root:
            print("❌ Could not find Ultimate Copilot project directory")
            print("Please run this script from the project directory or ensure")
            print("the 'frontend/dashboard.py' file exists in the project.")
            return False
        
        print("🚀 Quick Start Ultimate Copilot Dashboard")
        print("=" * 50)
        print(f"📁 Project: {project_root}")
        
        # Launch the main launcher
        launcher_script = project_root / "launch_ultimate_dashboard.py"
        
        if launcher_script.exists():
            print("🎯 Using full auto-launcher...")
            subprocess.run([sys.executable, str(launcher_script)], cwd=str(project_root))
        else:
            # Fallback to batch file if available
            batch_launcher = project_root / "launch_dashboard_enhanced.bat"
            if batch_launcher.exists() and os.name == 'nt':
                print("🎯 Using batch launcher...")
                subprocess.run([str(batch_launcher)], cwd=str(project_root), shell=True)
            else:
                print("❌ No suitable launcher found")
                print("Expected files:")
                print(f"  - {launcher_script}")
                print(f"  - {batch_launcher}")
                return False
        
        return True
        
    except KeyboardInterrupt:
        print("\n✋ Interrupted by user")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        input("\nPress Enter to exit...")
        sys.exit(1)
