#!/usr/bin/env python3
"""
Test file deletion through the updated backend
"""
import requests
import json
import time
import os

def test_backend_deletion():
    backend_url = "http://127.0.0.1:8004"
    workspace = "C:\\Users\\bcmad\\OneDrive\\Desktop\\agenttest"
    
    print("=== Testing File Deletion Through Backend ===")
    
    # Check files before deletion
    files_before = [f for f in os.listdir(workspace) if os.path.isfile(os.path.join(workspace, f))]
    print(f"Files before deletion: {len(files_before)}")
    for file in files_before:
        print(f"  - {file}")
    
    # Send deletion instruction
    instruction_payload = {
        "agent_id": "swarm",
        "action": "send_instruction",
        "instruction": "delete all the files in the workspace",
        "workspace": workspace
    }
    
    print(f"\nSending deletion instruction...")
    response = requests.post(f"{backend_url}/agents/control", json=instruction_payload)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Task assigned: {result.get('task_id', 'unknown')}")
        print(f"   Agent: {result.get('agent_id', 'unknown')}")
        
        # Wait for processing
        print("Waiting for deletion to complete...")
        time.sleep(5)
        
        # Check files after deletion
        files_after = [f for f in os.listdir(workspace) if os.path.isfile(os.path.join(workspace, f))]
        print(f"\nFiles after deletion: {len(files_after)}")
        
        if files_after:
            print("Remaining files:")
            for file in files_after:
                print(f"  - {file}")
            print("❌ Deletion failed - files still exist")
        else:
            print("✅ SUCCESS: All files deleted!")
            
        return len(files_after) == 0
    else:
        print(f"❌ Request failed: {response.status_code}")
        print(f"Response: {response.text}")
        return False

if __name__ == "__main__":
    success = test_backend_deletion()
    if success:
        print("\n🎉 File deletion now works through the dashboard!")
    else:
        print("\n❌ File deletion still needs fixing")
