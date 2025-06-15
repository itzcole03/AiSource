import requests
import json

def test_lmstudio_models():
    print("Testing LM Studio models endpoint...")
    
    try:
        # Test the backend models endpoint
        response = requests.get('http://localhost:8080/providers/lmstudio/models', timeout=10)
        print(f"Backend models endpoint: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"Found {len(models)} models via backend")
            for model in models[:3]:  # Show first 3
                print(f"  - {model.get('name', 'Unknown')}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Backend endpoint failed: {e}")
        
    try:
        # Test direct LM Studio API
        print("\nTesting direct LM Studio API...")
        response = requests.get('http://localhost:1234/v1/models', timeout=5)
        print(f"Direct LM Studio API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('data', [])
            print(f"Found {len(models)} models via direct API")
            for model in models[:3]:  # Show first 3
                print(f"  - {model.get('id', 'Unknown')}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Direct API failed: {e}")

if __name__ == "__main__":
    test_lmstudio_models()
