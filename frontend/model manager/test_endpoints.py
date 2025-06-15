import requests
import json

def test_endpoints():
    print("Testing backend endpoints...")
    
    # Test providers status
    try:
        response = requests.get('http://localhost:8080/providers/status', timeout=5)
        print(f"✅ /providers/status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   LM Studio running: {data.get('lmstudio', {}).get('running', False)}")
    except Exception as e:
        print(f"❌ /providers/status failed: {e}")
    
    # Test LM Studio models
    try:
        response = requests.get('http://localhost:8080/providers/lmstudio/models', timeout=5)
        print(f"✅ /providers/lmstudio/models: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data.get('models', []))} models")
            for model in data.get('models', [])[:3]:  # Show first 3
                print(f"   - {model.get('name', 'Unknown')}")
    except Exception as e:
        print(f"❌ /providers/lmstudio/models failed: {e}")

if __name__ == "__main__":
    test_endpoints()
