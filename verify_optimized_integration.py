#!/usr/bin/env python3
"""
Quick System Verification Script
Tests the optimized integration and network performance
"""

import requests
import time
import json

def test_endpoint(url: str, name: str, timeout: int = 3) -> dict:
    """Test an endpoint and measure response time"""
    start_time = time.time()
    try:
        response = requests.get(url, timeout=timeout)
        elapsed = (time.time() - start_time) * 1000  # Convert to ms
        
        if response.status_code == 200:
            return {
                "status": "✅ OK",
                "response_time": f"{elapsed:.0f}ms",
                "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else "Non-JSON"
            }
        else:
            return {
                "status": f"❌ HTTP {response.status_code}",
                "response_time": f"{elapsed:.0f}ms",
                "data": None
            }
    except requests.exceptions.Timeout:
        elapsed = (time.time() - start_time) * 1000
        return {"status": "⏱️ TIMEOUT", "response_time": f"{elapsed:.0f}ms", "data": None}
    except requests.exceptions.ConnectionError:
        return {"status": "❌ NO CONNECTION", "response_time": "N/A", "data": None}
    except Exception as e:
        return {"status": f"❌ ERROR: {str(e)[:50]}", "response_time": "N/A", "data": None}

def main():
    print("🔍 Ultimate Copilot Integration Verification")
    print("=" * 50)
    
    endpoints = [
        ("http://localhost:8080/health", "Model Manager Backend Health"),
        ("http://localhost:8080/system/info", "Model Manager System Info"),
        ("http://localhost:8080/providers/status", "Model Manager Providers"),
        ("http://localhost:8001/system/status", "Dashboard Backend Status"),
        ("http://localhost:8001/models/status", "Dashboard Models Status"),
        ("http://localhost:5173", "Model Manager Frontend"),
        ("http://localhost:8501", "Dashboard Frontend"),
    ]
    
    print("\n📊 Testing Endpoints:")
    print("-" * 50)
    
    all_good = True
    
    for url, name in endpoints:
        result = test_endpoint(url, name)
        status = result["status"]
        response_time = result["response_time"]
        
        print(f"{name:<30} {status:<15} {response_time}")
        
        if not status.startswith("✅"):
            all_good = False
    
    print("-" * 50)
    
    if all_good:
        print("🎉 All services are responding correctly!")
        print("\n🚀 Integration Status: ✅ FULLY OPERATIONAL")
        
        # Test Model Manager integration
        print("\n🔗 Testing Model Manager Integration:")
        mm_info = test_endpoint("http://localhost:8080/system/info", "System Info")
        if mm_info["status"].startswith("✅") and mm_info["data"]:
            data = mm_info["data"]
            print(f"   CPU Usage: {data.get('cpu', {}).get('usage', 'N/A')}%")
            print(f"   RAM Usage: {data.get('ram', {}).get('percentage', 'N/A')}%")
            print(f"   GPUs: {len(data.get('gpus', []))}")
        
        print("\n🌐 Access your dashboard:")
        print("   Main Dashboard: http://localhost:8501")
        print("   Model Manager:  http://localhost:5173")
        
    else:
        print("⚠️ Some services are not responding.")
        print("\n🔧 Troubleshooting:")
        print("   1. Check if all services started properly")
        print("   2. Run: python launch_optimized.py")
        print("   3. Wait for all services to initialize")
        
    print("\n📈 Performance Notes:")
    print("   • Model Manager backend optimized with 2s timeouts")
    print("   • System info cached for 5 seconds")
    print("   • Provider status uses process checks")
    print("   • Automatic port detection enabled")

if __name__ == "__main__":
    main()
