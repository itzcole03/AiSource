#!/usr/bin/env python3
"""
Quick dependency test for Ultimate Copilot Dashboard
"""

import sys

def test_imports():
    """Test if all required packages can be imported"""
    packages = [
        ("streamlit", "Streamlit web framework"),
        ("fastapi", "FastAPI backend framework"),
        ("uvicorn", "ASGI server"),
        ("plotly", "Interactive plotting"),
        ("pandas", "Data manipulation"),
        ("yaml", "YAML configuration parsing"),
        ("requests", "HTTP client"),
        ("psutil", "System monitoring")
    ]
    
    print("🔍 Testing Ultimate Copilot Dashboard Dependencies")
    print("=" * 60)
    
    all_good = True
    
    for package, description in packages:
        try:
            module = __import__(package)
            version = getattr(module, "__version__", "unknown")
            print(f"✅ {package:12} {version:10} - {description}")
        except ImportError:
            print(f"❌ {package:12} {'missing':10} - {description}")
            all_good = False
    
    print("\n" + "=" * 60)
    
    if all_good:
        print("🎉 All dependencies are available!")
        print("\nYou can now run the dashboard:")
        print("  Windows: launch_unified_dashboard.bat")
        print("  Cross-platform: python frontend/launch_dashboard.py")
        return True
    else:
        print("❌ Some dependencies are missing!")
        print("\nTo install missing packages:")
        print("  pip install --user streamlit fastapi uvicorn plotly pandas pyyaml requests psutil")
        print("\nOr use the enhanced launcher:")
        print("  launch_dashboard_enhanced.bat")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
