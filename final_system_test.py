#!/usr/bin/env python3
"""
Final test of the complete dashboard system
"""

import requests
import time

def test_dashboard_system():
    backend_url = "http://localhost:8001"
    
    print("Testing Ultimate Copilot Dashboard System")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing backend health...")
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Backend healthy - Version: {data.get('version', 'Unknown')}")
        else:
            print(f"   ✗ Backend health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ✗ Backend not reachable: {e}")
        return
    
    # Test 2: Agent status
    print("2. Testing agent status...")
    try:
        response = requests.get(f"{backend_url}/agents/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("agent_manager_available"):
                print(f"   ✓ Agent manager available")
                print(f"   ✓ Active tasks: {data.get('active_tasks', 0)}")
                print(f"   ✓ Completed tasks: {data.get('completed_tasks', 0)}")
            else:
                print(f"   ✗ Agent manager not available")
        else:
            print(f"   ✗ Agent status failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Agent status error: {e}")
    
    # Test 3: Agent instruction
    print("3. Testing agent instruction...")
    try:
        payload = {
            "agent_id": "orchestrator",
            "action": "send_instruction", 
            "instruction": "create a test file called final_test.txt with content 'Final system test successful'",
            "workspace": "C:\\Users\\bcmad\\OneDrive\\Desktop\\agenttest"
        }
        response = requests.post(f"{backend_url}/agents/control", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✓ Instruction sent successfully")
                print(f"   ✓ Task ID: {data.get('task_id', 'Unknown')}")
                print(f"   ✓ Agent: {data.get('agent_id', 'Unknown')}")
            else:
                print(f"   ✗ Instruction failed: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ✗ Instruction request failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Instruction error: {e}")
    
    # Test 4: File deletion instruction
    print("4. Testing file deletion instruction...")
    try:
        payload = {
            "agent_id": "orchestrator",
            "action": "send_instruction",
            "instruction": "delete all the files in the workspace",
            "workspace": "C:\\Users\\bcmad\\OneDrive\\Desktop\\agenttest"
        }
        response = requests.post(f"{backend_url}/agents/control", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"   ✓ File deletion instruction sent successfully")
                print(f"   ✓ Task ID: {data.get('task_id', 'Unknown')}")
            else:
                print(f"   ✗ File deletion failed: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ✗ File deletion request failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ File deletion error: {e}")
    
    print("\nSystem Test Complete!")
    print(f"Dashboard UI: http://localhost:8501")
    print(f"Backend API: {backend_url}")

if __name__ == "__main__":
    test_dashboard_system()
