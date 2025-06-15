#!/usr/bin/env python3
"""Simple test for LM Studio connection after backend restart"""

import requests
import json
import os

def read_port_config():
    """Read the current port from config file"""
    locations = [
        "backend_config.json",
        "frontend/model manager/backend_config.json", 
        "frontend/model manager/../backend_config.json"
    ]
    
    print(f"Looking for config files...")
    for location in locations:
        print(f"  Checking: {location}")
        try:
            if os.path.exists(location):
                with open(location, 'r') as f:
                    config = json.load(f)
                print(f"✅ Found config at: {location}")
                print(f"   Config: {config}")
                port = config.get("backend_port")
                url = config.get("backend_url")
                if not url and port:
                    url = f"http://127.0.0.1:{port}"
                print(f"   Port: {port}, URL: {url}")
                return port, url
            else:
                print(f"   File does not exist")
        except Exception as e:
            print(f"❌ Failed to read config from {location}: {e}")
    
    print("❌ No backend config found in any location")
    return None, None

def test_lmstudio_direct():
    """Test LM Studio API directly"""
    try:
        print("Testing LM Studio API directly...")
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        if response.status_code == 200:
            models_data = response.json()
            print(f"✅ LM Studio API accessible")
            print(f"✅ Models found: {len(models_data.get('data', []))}")
            return True
        else:
            print(f"❌ LM Studio API returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ LM Studio API not accessible: {e}")
        return False

def test_backend_connection():
    """Test backend connection"""
    port, url = read_port_config()
    if not port:
        print("❌ No backend config found")
        return False
    
    try:
        print(f"Testing backend at {url}...")
        response = requests.get(f"{url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend accessible at port {port}")
            print(f"✅ Backend version: {data.get('version')}")
            return True
        else:
            print(f"❌ Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not accessible: {e}")
        return False

def test_providers_endpoint():
    """Test the providers endpoint"""
    port, url = read_port_config()
    if not port:
        print("❌ No backend config found")
        return False
    
    try:
        print(f"Testing providers endpoint at {url}/providers...")
        response = requests.get(f"{url}/providers", timeout=15)
        if response.status_code == 200:
            providers = response.json()
            print(f"✅ Providers endpoint accessible")
            
            for provider in providers:
                name = provider.get('name')
                status = provider.get('status')
                connected = provider.get('connected')
                model_count = provider.get('model_count', 0)
                print(f"  {name}: {status} (connected: {connected}, models: {model_count})")
            
            return True
        else:
            print(f"❌ Providers endpoint returned {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Providers endpoint not accessible: {e}")
        return False

if __name__ == "__main__":
    print("=== Model Manager Connection Test ===")
    
    lm_ok = test_lmstudio_direct()
    backend_ok = test_backend_connection()
    
    if backend_ok:
        providers_ok = test_providers_endpoint()
    else:
        print("⚠️  Skipping providers test - backend not accessible")
        providers_ok = False
    
    print("\n=== Summary ===")
    print(f"LM Studio API: {'✅' if lm_ok else '❌'}")
    print(f"Backend: {'✅' if backend_ok else '❌'}")
    print(f"Providers: {'✅' if providers_ok else '❌'}")
    
    if lm_ok and backend_ok and providers_ok:
        print("🎉 All connections working!")
    else:
        print("⚠️  Some connections failed - check backend logs")
