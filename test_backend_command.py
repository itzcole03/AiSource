#!/usr/bin/env python3
"""
Test backend agent command handling with debug
"""
import requests
import json

def test_backend_agent_command():
    backend_url = "http://127.0.0.1:8002"
    
    # Test the exact payload the frontend sends
    instruction_payload = {
        "agent_id": "swarm",
        "action": "send_instruction",
        "instruction": "create a file called backend_test.txt with content Hello from backend",
        "workspace": "C:\\Users\\bcmad\\OneDrive\\Desktop\\agenttest"
    }
    
    print("Testing backend agent command with payload:")
    print(json.dumps(instruction_payload, indent=2))
    
    response = requests.post(f"{backend_url}/agents/control", json=instruction_payload)
    print(f"\nResponse status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        # Check if it's a real task assignment or mock response
        if "task_id" in result:
            print("✅ Real task assignment detected")
        else:
            print("❌ Mock response detected")
    else:
        print(f"Error response: {response.text}")

if __name__ == "__main__":
    test_backend_agent_command()
