import requests
import json

try:
    response = requests.get('http://localhost:8080/providers/status')
    data = response.json()
    print('Backend status response:')
    print(json.dumps(data, indent=2))
    
    # Check LM Studio specifically
    if data.get('lmstudio', {}).get('running'):
        print('\n✅ LM Studio detected as running!')
    else:
        print('\n❌ LM Studio not detected as running')
        print(f"LM Studio status: {data.get('lmstudio', {})}")
        
except Exception as e:
    print(f'Error: {e}')
