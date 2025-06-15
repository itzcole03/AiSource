#!/usr/bin/env python3
"""
Simple vLLM connectivity test
"""
import requests
import json

def test_vllm_connection():
    """Test basic vLLM connection"""
    print("Testing vLLM Server Connection...")
    
    try:
        # Test vLLM server status
        response = requests.get("http://localhost:8000/v1/models", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            models = data.get('data', [])
            
            print(f"✓ vLLM server is running!")
            print(f"✓ Found {len(models)} model(s):")
            
            for model in models:
                model_id = model.get('id', 'unknown')
                print(f"  - {model_id}")
            
            # Test a simple completion
            if models:
                test_model = models[0]['id']
                print(f"\n Testing completion with {test_model}...")
                
                completion_data = {
                    "model": test_model,
                    "messages": [{"role": "user", "content": "Say hello"}],
                    "max_tokens": 10,
                    "temperature": 0
                }
                
                comp_response = requests.post(
                    "http://localhost:8000/v1/chat/completions",
                    json=completion_data,
                    timeout=10
                )
                
                if comp_response.status_code == 200:
                    result = comp_response.json()
                    content = result['choices'][0]['message']['content']
                    print(f"✓ Model responded: {content}")
                    return True
                else:
                    print(f"✗ Completion failed: {comp_response.status_code}")
                    return False
            else:
                print("✗ No models available for testing")
                return False
                
        else:
            print(f"✗ vLLM server returned status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to vLLM server: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_vllm_connection()
    exit(0 if success else 1)
