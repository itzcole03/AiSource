#!/usr/bin/env python3
"""Test LM Studio provider status via Model Manager backend"""

import requests
import time
import json

def test_lmstudio_status():
    """Test LM Studio provider status"""
    print("Testing LM Studio provider status via Model Manager backend...")
    
    try:
        # Test backend health first
        response = requests.get("http://localhost:8003/health", timeout=5)
        print(f"Backend health: {response.status_code}")
        
        # Test LM Studio provider status
        response = requests.get("http://localhost:8003/providers/status/lmstudio", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test LM Studio model listing
        response = requests.get("http://localhost:8003/models/list/lmstudio", timeout=5)
        print(f"Models Status Code: {response.status_code}")
        print(f"Models Response: {json.dumps(response.json(), indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    test_lmstudio_status()
