#!/usr/bin/env python3
"""
Test script to check LM Studio provider status from the backend
"""
import requests
import json

def test_backend_lmstudio():
    """Test the backend LM Studio provider status"""
    backend_url = "http://127.0.0.1:8003"
    
    print("Testing Model Manager Backend LM Studio connection...")
    
    try:
        # Test general providers endpoint
        print("\n1. Testing /providers endpoint:")
        response = requests.get(f"{backend_url}/providers", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
        # Test specific LM Studio endpoint
        print("\n2. Testing /providers/lmstudio endpoint:")
        response = requests.get(f"{backend_url}/providers/lmstudio", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
        # Test LM Studio models endpoint
        print("\n3. Testing /providers/lmstudio/models endpoint:")
        response = requests.get(f"{backend_url}/providers/lmstudio/models", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
        # Test direct LM Studio API (should work)
        print("\n4. Testing direct LM Studio API:")
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Models count: {len(data.get('data', []))}")
            print(f"First few models: {[m['id'] for m in data.get('data', [])[:3]]}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    test_backend_lmstudio()
