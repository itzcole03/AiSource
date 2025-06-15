#!/usr/bin/env python3
"""
Test the backend API directly
"""
import requests
import json

backend_url = "http://localhost:8002"

print("Testing backend API...")

# Test health endpoint
try:
    response = requests.get(f"{backend_url}/health", timeout=5)
    print(f"✅ Health check: {response.status_code}")
except Exception as e:
    print(f"❌ Health check failed: {e}")

# Test agents status
try:
    response = requests.get(f"{backend_url}/agents/status", timeout=5)
    print(f"✅ Agents status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Agent manager available: {data.get('agent_manager_available', False)}")
        agents = data.get('agents', {})
        print(f"   Number of agents: {len(agents)}")
        for agent_id, agent_info in agents.items():
            print(f"   - {agent_id}: {agent_info.get('status', 'unknown')}")
except Exception as e:
    print(f"❌ Agents status failed: {e}")

# Test agent control endpoint
try:
    payload = {
        "agent_id": "orchestrator",
        "action": "send_instruction",
        "instruction": "create a file named test_backend.txt with the word 'backend_test'",
        "workspace": "C:\\Users\\bcmad\\OneDrive\\Desktop\\agenttest"
    }
    
    print(f"📤 Sending POST request to {backend_url}/agents/control")
    print(f"   Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(f"{backend_url}/agents/control", 
                           json=payload, 
                           timeout=30)
    
    print(f"✅ Agent control response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   Result: {json.dumps(result, indent=2)}")
    else:
        print(f"   Error response: {response.text}")
        
except Exception as e:
    print(f"❌ Agent control failed: {e}")
    import traceback
    traceback.print_exc()
