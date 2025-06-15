#!/usr/bin/env python3
"""
Quick test script to check agent status API response format
"""
import requests
import json

def test_agent_status():
    try:
        response = requests.get("http://127.0.0.1:8001/agents/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("Raw response:")
            print(json.dumps(data, indent=2))
            
            print("\nAgents data:")
            agents = data.get("agents", {})
            print(f"Type: {type(agents)}")
            print(json.dumps(agents, indent=2))
            
            if "agents" in agents:
                print("\nNested agents found!")
                nested_agents = agents["agents"]
                print(json.dumps(nested_agents, indent=2))
                
        else:
            print(f"Error: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_agent_status()
