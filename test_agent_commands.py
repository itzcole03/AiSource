#!/usr/bin/env python3
"""
Test agent start/stop commands
"""
import requests
import json

def test_agent_commands():
    backend_url = "http://127.0.0.1:8001"
    
    print("Testing agent start command...")
    payload = {
        "agent_id": "orchestrator",
        "action": "start"
    }
    
    response = requests.post(f"{backend_url}/agents/control", json=payload)
    print(f"Start command response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print(f"Error: {response.text}")
    
    print("\nTesting agent stop command...")
    payload = {
        "agent_id": "orchestrator",
        "action": "stop"
    }
    
    response = requests.post(f"{backend_url}/agents/control", json=payload)
    print(f"Stop command response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_agent_commands()
