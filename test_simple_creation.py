#!/usr/bin/env python3
"""
Test simple file creation to isolate the issue
"""
import requests
import json
import time
import os

def test_simple_file_creation():
    backend_url = "http://127.0.0.1:8002"
    workspace = "C:\\Users\\bcmad\\OneDrive\\Desktop\\agenttest"
    
    test_cases = [
        {
            "name": "Simple create",
            "instruction": "create a file called simple.txt with the word Testing"
        },
        {
            "name": "File named",
            "instruction": "create a file named test.txt containing Hello World"
        },
        {
            "name": "Story instruction",
            "instruction": "write a story in a file called story.txt and make the story about pikachu vs kakashi from naruto"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n=== {test_case['name']} ===")
        print(f"Instruction: {test_case['instruction']}")
        
        payload = {
            "agent_id": "swarm",
            "action": "send_instruction",
            "instruction": test_case['instruction'],
            "workspace": workspace
        }
        
        response = requests.post(f"{backend_url}/agents/control", json=payload)
        if response.status_code == 200:
            result = response.json()
            task_id = result.get("task_id", "unknown")
            print(f"Task assigned: {task_id}")
            
            # Wait for processing
            time.sleep(3)
            
            # Check for new files
            print("Files created in last 10 seconds:")
            import datetime
            cutoff = datetime.datetime.now() - datetime.timedelta(seconds=10)
            for filename in os.listdir(workspace):
                filepath = os.path.join(workspace, filename)
                if os.path.isfile(filepath):
                    mtime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))
                    if mtime > cutoff:
                        print(f"  - {filename} (size: {os.path.getsize(filepath)} bytes)")
        else:
            print(f"Failed: {response.status_code}")

if __name__ == "__main__":
    test_simple_file_creation()
