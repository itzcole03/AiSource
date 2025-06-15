#!/usr/bin/env python3
"""
Test LM Studio API connection
"""
import requests
import json

def test_lmstudio_connection():
    """Test if LM Studio API is accessible"""
    try:
        # Test the models endpoint
        response = requests.get("http://localhost:1234/v1/models", timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print(f"Models found: {len(data.get('data', []))}")
            return True
        else:
            print(f"Error: Status {response.status_code}")
            print(f"Response text: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("Connection failed: LM Studio is not running or API not accessible on port 1234")
        return False
    except requests.exceptions.Timeout:
        print("Connection timeout: LM Studio took too long to respond")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("Testing LM Studio API connection...")
    success = test_lmstudio_connection()
    print(f"Connection test: {'PASSED' if success else 'FAILED'}")
