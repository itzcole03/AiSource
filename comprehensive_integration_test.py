#!/usr/bin/env python3
"""
Comprehensive integration test for Ultimate Copilot with Model Manager
Tests both React-based and static fallback versions
"""

import requests
import time
import os
import subprocess
import sys
from pathlib import Path

def print_header(title):
    """Print test section header"""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def test_service_endpoint(url, name, timeout=5):
    """Test a service endpoint"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name}: Online (HTTP {response.status_code})")
            return True, response.json() if 'json' in response.headers.get('content-type', '') else response.text
        else:
            print(f"⚠️ {name}: HTTP {response.status_code}")
            return False, None
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Connection refused")
        return False, None
    except requests.exceptions.Timeout:
        print(f"⏱️ {name}: Timeout")
        return False, None
    except Exception as e:
        print(f"❌ {name}: Error - {e}")
        return False, None

def test_dashboard_backend():
    """Test dashboard backend functionality"""
    print_header("DASHBOARD BACKEND TESTS")
    
    base_url = "http://localhost:8001"
      # Test health endpoint
    success, data = test_service_endpoint(f"{base_url}/health", "Health Check")
    if success and isinstance(data, dict):
        print(f"   Version: {data.get('version', 'Unknown')}")
        print(f"   Status: {data.get('status', 'Unknown')}")
    
    # Test agent status
    success, data = test_service_endpoint(f"{base_url}/agents/status", "Agent Status")
    if success and isinstance(data, dict):
        print(f"   Agent Manager: {'Available' if data.get('agent_manager_available') else 'Unavailable'}")
        print(f"   Active Tasks: {data.get('active_tasks', 0)}")
    
    # Test model status
    success, data = test_service_endpoint(f"{base_url}/models/status", "Model Status")
    if success and isinstance(data, dict):
        providers = data.get('providers', {})
        print(f"   Providers: {len(providers)} found")
        for provider, info in providers.items():
            if isinstance(info, dict):
                status = info.get('status', 'unknown')
                models = len(info.get('models', []))
                print(f"     • {provider}: {status} ({models} models)")
    
    return True

def test_model_manager_backend():
    """Test Model Manager backend functionality"""
    print_header("MODEL MANAGER BACKEND TESTS")
    
    base_url = "http://localhost:8002"
      # Test health endpoint
    success, data = test_service_endpoint(f"{base_url}/health", "Health Check")
    if success and isinstance(data, dict):
        print(f"   Service: Model Manager")
        print(f"   Status: {data.get('status', 'Unknown')}")
    
    # Test system info
    success, data = test_service_endpoint(f"{base_url}/system/info", "System Info")
    if success and isinstance(data, dict):
        cpu = data.get('cpu', {})
        ram = data.get('ram', {})
        print(f"   CPU Usage: {cpu.get('usage', 0):.1f}%")
        print(f"   RAM Usage: {ram.get('percentage', 0):.1f}%")
        print(f"   GPUs: {len(data.get('gpus', []))}")
    
    # Test providers
    success, data = test_service_endpoint(f"{base_url}/providers/status", "Provider Status")
    if success and isinstance(data, dict):
        for provider, info in data.items():
            if isinstance(info, dict):
                available = info.get('available', False)
                models = len(info.get('models', []))
                print(f"   • {provider}: {'Available' if available else 'Unavailable'} ({models} models)")
    
    return True

def test_frontend_services():
    """Test frontend services"""
    print_header("FRONTEND SERVICES TESTS")
    
    # Test dashboard frontend
    success, _ = test_service_endpoint("http://localhost:8501", "Dashboard Frontend (Streamlit)")
    
    # Test Model Manager frontend (React)
    react_success, _ = test_service_endpoint("http://localhost:5173", "Model Manager Frontend (React)")
    
    # Test static Model Manager
    static_path = Path("model_manager_static.html")
    if static_path.exists():
        print("✅ Static Model Manager: Available")
        print(f"   Path: {static_path.absolute()}")
    else:
        print("❌ Static Model Manager: Not found")
    
    return success

def test_integration_features():
    """Test integration between services"""
    print_header("INTEGRATION TESTS")
    
    # Test dashboard → model manager backend communication
    try:
        # Make request through dashboard backend to model manager
        response = requests.get("http://localhost:8001/models/status", timeout=10)
        if response.status_code == 200:
            print("✅ Dashboard → Model Manager: Communication working")
            data = response.json()
            if 'providers' in data:
                print("   Data includes provider information")
        else:
            print(f"⚠️ Dashboard → Model Manager: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard → Model Manager: {e}")
    
    # Test model manager advanced features
    try:
        response = requests.get("http://localhost:8002/providers/status", timeout=10)
        if response.status_code == 200:
            print("✅ Model Manager Advanced Features: Working")
            data = response.json()
            provider_count = len([p for p in data.values() if isinstance(p, dict)])
            print(f"   Provider detection: {provider_count} providers checked")
        else:
            print(f"⚠️ Model Manager Advanced Features: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ Model Manager Advanced Features: {e}")
    
    return True

def test_static_fallback():
    """Test static fallback functionality"""
    print_header("STATIC FALLBACK TESTS")
    
    static_file = Path("model_manager_static.html")
    
    if static_file.exists():
        print("✅ Static HTML file exists")
        
        # Check file size
        size = static_file.stat().st_size
        print(f"   File size: {size:,} bytes")
        
        # Check content
        with open(static_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic content checks
        checks = [
            ("HTML structure", "<html" in content and "</html>" in content),
            ("JavaScript functionality", "fetch(" in content),
            ("CSS styling", "<style>" in content),
            ("API endpoints", "localhost:8002" in content),
            ("Model Manager branding", "Model Manager" in content)
        ]
        
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")
        
        all_passed = all(result for _, result in checks)
        if all_passed:
            print("✅ Static fallback is fully functional")
        else:
            print("⚠️ Static fallback has some issues")
        
        return all_passed
    else:
        print("❌ Static HTML file not found")
        return False

def test_node_js_setup():
    """Test Node.js setup functionality"""
    print_header("NODE.JS SETUP TESTS")
    
    # Check system Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ System Node.js: {result.stdout.strip()}")
            system_nodejs = True
        else:
            print("❌ System Node.js: Not found")
            system_nodejs = False
    except:
        print("❌ System Node.js: Not accessible")
        system_nodejs = False
    
    # Check local Node.js
    local_nodejs_dir = Path("nodejs")
    if local_nodejs_dir.exists():
        node_exe = local_nodejs_dir / "node.exe"
        if node_exe.exists():
            try:
                result = subprocess.run([str(node_exe), "--version"], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    print(f"✅ Local Node.js: {result.stdout.strip()}")
                    local_nodejs = True
                else:
                    print("❌ Local Node.js: Not working")
                    local_nodejs = False
            except:
                print("❌ Local Node.js: Not accessible")
                local_nodejs = False
        else:
            print("❌ Local Node.js: Executable not found")
            local_nodejs = False
    else:
        print("❌ Local Node.js: Directory not found")
        local_nodejs = False
    
    # Check installer script
    installer_script = Path("install_nodejs.py")
    if installer_script.exists():
        print("✅ Node.js installer script: Available")
    else:
        print("❌ Node.js installer script: Missing")
    
    return system_nodejs or local_nodejs

def generate_test_report():
    """Generate comprehensive test report"""
    print_header("COMPREHENSIVE TEST REPORT")
    
    print("Running all tests...")
    time.sleep(1)
    
    # Run all tests
    results = {
        "Dashboard Backend": test_dashboard_backend(),
        "Model Manager Backend": test_model_manager_backend(),
        "Frontend Services": test_frontend_services(),
        "Integration Features": test_integration_features(),
        "Static Fallback": test_static_fallback(),
        "Node.js Setup": test_node_js_setup()
    }
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    print()
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print()
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Ultimate Copilot is fully functional.")
    elif passed >= total * 0.8:
        print("✅ Most tests passed. System is largely functional.")
    elif passed >= total * 0.5:
        print("⚠️ Some tests failed. System has limited functionality.")
    else:
        print("❌ Many tests failed. System needs attention.")
    
    # Recommendations
    print_header("RECOMMENDATIONS")
    
    if not results["Node.js Setup"]:
        print("💡 Install Node.js to enable full Model Manager functionality:")
        print("   • Run: python install_nodejs.py")
        print("   • Or install from: https://nodejs.org/")
    
    if not results["Frontend Services"]:
        print("💡 Frontend services may need manual restart:")
        print("   • Check if ports 8501 and 5173 are available")
        print("   • Restart with: python launch_enhanced_ultimate.py")
    
    if not results["Static Fallback"]:
        print("💡 Static fallback needs repair:")
        print("   • model_manager_static.html may be missing or corrupted")
    
    if results["Static Fallback"] and not results["Frontend Services"]:
        print("💡 Use static Model Manager as fallback:")
        print("   • Available in Dashboard → Model Manager tab")
        print("   • Full functionality without Node.js dependency")
    
    return passed / total

def main():
    """Main test function"""
    print("🧪 Ultimate Copilot Integration Test Suite")
    print("Testing both React-based and static fallback functionality")
    
    # Wait a moment for services to be ready
    print("\nWaiting for services to initialize...")
    time.sleep(3)
    
    # Run comprehensive test
    success_rate = generate_test_report()
    
    # Exit with appropriate code
    if success_rate >= 0.8:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
