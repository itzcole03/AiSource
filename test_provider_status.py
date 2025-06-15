#!/usr/bin/env python3
"""Test the provider status to check LM Studio connection"""

import requests
import json

def test_provider_status():
    """Test the provider status endpoint"""
    try:
        print("Testing provider status...")
        response = requests.get("http://127.0.0.1:8002/providers", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(data, indent=2)}")
            
            # Check LM Studio specifically
            lmstudio_found = False
            for provider in data:
                if provider.get('name') == 'lmstudio':
                    lmstudio_found = True
                    print(f"\nLM Studio Status: {provider.get('status')}")
                    print(f"LM Studio Connected: {provider.get('connected')}")
                    print(f"LM Studio Model Count: {provider.get('model_count', 0)}")
                    break
            
            if not lmstudio_found:
                print("\nLM Studio provider not found in response!")
                
        else:
            print(f"Error: Status Code {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def test_lmstudio_specific():
    """Test LM Studio specific endpoint"""
    try:
        print("\nTesting LM Studio specific endpoint...")
        response = requests.get("http://127.0.0.1:8002/providers/lmstudio/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"LM Studio Status: {json.dumps(data, indent=2)}")
        else:
            print(f"Error: Status Code {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_provider_status()
    test_lmstudio_specific()
