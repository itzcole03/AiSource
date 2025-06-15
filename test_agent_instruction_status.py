#!/usr/bin/env python3
"""
Test sending an agent instruction and checking status updates
"""
import requests
import json
import time

def test_agent_instruction_and_status():
    backend_url = "http://127.0.0.1:8001"
    
    print("1. Checking initial agent status...")
    response = requests.get(f"{backend_url}/agents/status")
    if response.status_code == 200:
        data = response.json()
        agents = data.get("agents", {})
        print(f"Initial active agents: {[name for name, agent in agents.items() if agent.get('active', False)]}")
    
    print("\n2. Sending instruction to agent swarm...")
    instruction_payload = {
        "agent_id": "swarm",
        "action": "send_instruction",
        "instruction": "create a file called status_test.txt with the content 'Agent is working!'",
        "workspace": "C:\\Users\\bcmad\\OneDrive\\Desktop\\agenttest"
    }
    
    response = requests.post(f"{backend_url}/agents/control", json=instruction_payload)
    if response.status_code == 200:
        result = response.json()
        print(f"Instruction result: {result}")
    else:
        print(f"Error sending instruction: {response.status_code}")
        return
    
    print("\n3. Checking agent status after instruction...")
    time.sleep(2)  # Wait for instruction to be processed
    
    response = requests.get(f"{backend_url}/agents/status")
    if response.status_code == 200:
        data = response.json()
        agents = data.get("agents", {})
        active_agents = [name for name, agent in agents.items() if agent.get('active', False)]
        print(f"Active agents after instruction: {active_agents}")
        
        # Show agent details
        for name, agent in agents.items():
            status = agent.get('status', 'unknown')
            current_task = agent.get('current_task')
            print(f"  {name}: {status}, task: {current_task}")
    
    print("\n4. Checking recent activity...")
    response = requests.get(f"{backend_url}/agents/activity")
    if response.status_code == 200:
        activity = response.json()
        print("Recent activity:")
        for log in activity.get("activity", [])[-5:]:  # Show last 5 activities
            print(f"  {log.get('timestamp', '')}: {log.get('message', '')}")

if __name__ == "__main__":
    test_agent_instruction_and_status()
