#!/usr/bin/env python3
"""
Ultimate Copilot System - Intelligent Model Manager Integration Test
Tests the full integration of the advanced model manager with real capabilities
"""

import requests
import time
import json

def test_intelligent_model_manager():
    backend_url = "http://localhost:8001"
    model_manager_url = "http://localhost:8002"
    
    print("🚀 Testing Ultimate Copilot + Intelligent Model Manager Integration")
    print("=" * 80)
    
    # Test 1: Dashboard Backend Health
    print("1. Testing Dashboard Backend Health...")
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Dashboard Backend healthy - Version: {data.get('version', 'Unknown')}")
        else:
            print(f"   ❌ Dashboard Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Dashboard Backend not reachable: {e}")
        return
    
    # Test 2: Model Manager Backend Health
    print("2. Testing Model Manager Backend Health...")
    try:
        response = requests.get(f"{model_manager_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Model Manager Backend healthy - Status: {data.get('status', 'Unknown')}")
        else:
            print(f"   ❌ Model Manager Backend health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Model Manager Backend not reachable: {e}")
    
    # Test 3: Integrated Model Status
    print("3. Testing Integrated Model Status...")
    try:
        response = requests.get(f"{backend_url}/models/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Model Status Retrieved")
            print(f"   📊 Manager Type: {data.get('manager', 'Unknown')}")
            print(f"   🌐 Backend URL: {data.get('backend_url', 'Unknown')}")
            
            providers = data.get('providers', {})
            for provider, info in providers.items():
                status = info.get('status', 'unknown')
                running = info.get('running', False)
                print(f"   🔧 {provider.title()}: {status} ({'Running' if running else 'Stopped'})")
            
            system = data.get('system', {})
            if system:
                cpu = system.get('cpu', {})
                ram = system.get('ram', {})
                gpu = system.get('gpu', {})
                
                print(f"   💻 CPU: {cpu.get('cores', 'N/A')} cores, {cpu.get('usage', 'N/A')}% usage")
                print(f"   🧠 RAM: {ram.get('used', 'N/A')}/{ram.get('total', 'N/A')} ({ram.get('percentage', 'N/A')}%)")
                
                if isinstance(gpu, list) and gpu:
                    gpu_info = gpu[0]
                    print(f"   🎮 GPU: {gpu_info.get('name', 'N/A')} ({gpu_info.get('utilization', 'N/A')}% util)")
        else:
            print(f"   ❌ Model status failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Model status error: {e}")
    
    # Test 4: Advanced System Information
    print("4. Testing Advanced System Information...")
    try:
        response = requests.get(f"{model_manager_url}/system/info", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Advanced System Info Retrieved")
            
            platform = data.get('platform', {})
            print(f"   🖥️ Platform: {platform.get('system', 'Unknown')} {platform.get('release', '')}")
            print(f"   🔧 Machine: {platform.get('machine', 'Unknown')}")
            
            disk = data.get('disk', {})
            print(f"   💾 Disk: {disk.get('used', 'N/A')}/{disk.get('total', 'N/A')} ({disk.get('percentage', 0):.1f}%)")
            
        else:
            print(f"   ❌ System info failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ System info error: {e}")
    
    # Test 5: Provider Status Check
    print("5. Testing Provider Status...")
    try:
        response = requests.get(f"{model_manager_url}/providers/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Provider Status Retrieved")
            
            for provider, info in data.items():
                installed = info.get('installed', False)
                running = info.get('running', False)
                path = info.get('path', 'Unknown')
                
                status_icon = "✅" if installed else "❌"
                running_icon = "🟢" if running else "🔴"
                
                print(f"   {status_icon} {provider.title()}: {'Installed' if installed else 'Not Found'} {running_icon} {'Running' if running else 'Stopped'}")
                if installed and path != "Unknown":
                    print(f"      📂 Path: {path}")
        else:
            print(f"   ❌ Provider status failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Provider status error: {e}")
    
    # Test 6: Model Manager Command Integration
    print("6. Testing Model Manager Command Integration...")
    try:
        payload = {
            "provider": "ollama",
            "action": "list_models",
            "model": ""
        }
        response = requests.post(f"{backend_url}/models/control", json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✅ Model command executed successfully")
                print(f"   📝 Message: {data.get('message', 'No message')}")
                
                models = data.get('models', [])
                if models:
                    print(f"   📦 Found {len(models)} models")
                    for model in models[:3]:  # Show first 3 models
                        model_name = model.get('name', 'Unknown')
                        model_size = model.get('size', 'Unknown')
                        print(f"      • {model_name} ({model_size})")
                else:
                    print(f"   📦 No models found (this is normal if provider not running)")
            else:
                print(f"   ⚠️ Command executed but returned error: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ❌ Model command failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Model command error: {e}")
    
    print("\n" + "=" * 80)
    print("🎉 Integration Test Complete!")
    print(f"🌐 Dashboard UI: http://localhost:8502")
    print(f"🔧 Main Backend: {backend_url}")
    print(f"🤖 Model Manager: {model_manager_url}")
    print(f"📊 The Models tab now has REAL system monitoring and provider control!")

if __name__ == "__main__":
    test_intelligent_model_manager()
