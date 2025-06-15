#!/usr/bin/env python3
"""
Quick test for the enhanced launcher fixes
"""

import subprocess
import sys
import time

def test_dashboard_syntax():
    """Test if dashboard.py has syntax errors"""
    print("🧪 Testing dashboard.py syntax...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "py_compile", 
            "frontend/dashboard.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ dashboard.py syntax is valid")
            return True
        else:
            print(f"❌ dashboard.py syntax error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error testing syntax: {e}")
        return False

def test_services_startup():
    """Test a quick service startup"""
    print("\n🧪 Testing service startup...")
    
    # Try to start just the dashboard backend
    try:
        import requests
        
        # Check if dashboard backend is already running
        try:
            response = requests.get("http://localhost:8001/health", timeout=2)
            if response.status_code == 200:
                print("✅ Dashboard backend already running")
                return True
        except:
            pass
        
        print("Starting dashboard backend for test...")
        process = subprocess.Popen([
            sys.executable, "frontend/dashboard_backend_clean.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment
        time.sleep(3)
        
        # Test health
        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            if response.status_code == 200:
                print("✅ Dashboard backend test successful")
                process.terminate()
                return True
            else:
                print(f"⚠️ Dashboard backend returned status {response.status_code}")
                process.terminate()
                return False
        except Exception as e:
            print(f"❌ Dashboard backend test failed: {e}")
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ Service test error: {e}")
        return False

def main():
    """Run quick tests"""
    print("🚀 ULTIMATE COPILOT - QUICK TESTS")
    print("=" * 50)
    
    tests = [
        ("Dashboard Syntax", test_dashboard_syntax),
        ("Service Startup", test_services_startup)
    ]
    
    passed = 0
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} test failed")
    
    print(f"\n📊 Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! System is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
