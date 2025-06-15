#!/usr/bin/env python3
"""
Ultimate Copilot Dashboard - Integration Verification
Quick check to ensure all components are properly integrated
"""

import requests
import time
from pathlib import Path

def check_component(name, url, timeout=5):
    """Check if a component is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name}: ONLINE ({url})")
            return True
        else:
            print(f"⚠️ {name}: Response {response.status_code} ({url})")
            return False
    except requests.RequestException:
        print(f"❌ {name}: OFFLINE ({url})")
        return False

def verify_files():
    """Verify key integration files exist"""
    base_path = Path(__file__).parent
    files_to_check = [
        "frontend/dashboard.py",
        "frontend/dashboard_backend_clean.py", 
        "intelligent_model_manager.py",
        "frontend/model manager/backend/server.py",
        "frontend/model manager/vite.config.ts",
        "frontend/model manager/package.json",
        "launch_ultimate_dashboard.bat",
        "launch_ultimate_simple.py"
    ]
    
    print("📁 Checking integration files...")
    all_good = True
    for file_path in files_to_check:
        full_path = base_path / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_good = False
    
    return all_good

def main():
    print("🔍 Ultimate Copilot Dashboard - Integration Verification")
    print("=" * 60)
    
    # Check files
    files_ok = verify_files()
    
    print("\n🌐 Checking service availability...")
    
    # Check services
    services = [
        ("Main Dashboard", "http://localhost:8501"),
        ("Model Manager Frontend", "http://localhost:5173"),
        ("Model Manager Backend", "http://localhost:8080/health"),
        ("Dashboard Backend", "http://localhost:8001/system/status")
    ]
    
    online_services = 0
    for name, url in services:
        if check_component(name, url):
            online_services += 1
    
    print(f"\n📊 Status Summary:")
    print(f"   Files: {'✅ OK' if files_ok else '❌ ISSUES'}")
    print(f"   Services: {online_services}/{len(services)} online")
    
    if files_ok and online_services > 0:
        print("\n🎉 Integration Status: ✅ VERIFIED")
        print("\n🚀 To start all services, run:")
        print("   • launch_ultimate_dashboard.bat (Windows)")
        print("   • python launch_ultimate_simple.py (Cross-platform)")
    else:
        print("\n⚠️ Integration Status: ❌ NEEDS ATTENTION")
        if not files_ok:
            print("   → Some integration files are missing")
        if online_services == 0:
            print("   → No services are currently running")
            print("   → Start services with the launchers provided")

if __name__ == "__main__":
    main()
