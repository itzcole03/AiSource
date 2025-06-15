import requests
import json

def test_lmstudio_models():
    print("Testing LM Studio models endpoint...")
    
    # Test direct LM Studio API
    try:
        print("\n1. Testing direct LM Studio API (should work from backend):")
        response = requests.get('http://localhost:1234/v1/models', timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Raw response: {json.dumps(data, indent=2)}")
            models = data.get('data', [])
            print(f"   Found {len(models)} models directly from LM Studio")
            for model in models:
                print(f"   - {model.get('id', 'Unknown')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error connecting to LM Studio: {e}")
    
    # Test backend proxy
    try:
        print("\n2. Testing backend proxy endpoint:")
        response = requests.get('http://localhost:8080/providers/lmstudio/models', timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Backend response: {json.dumps(data, indent=2)}")
            models = data.get('models', [])
            print(f"   Found {len(models)} models via backend proxy")
            for model in models:
                print(f"   - {model.get('name', 'Unknown')}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error connecting to backend: {e}")

if __name__ == "__main__":
    test_lmstudio_models()
