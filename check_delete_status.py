#!/usr/bin/env python3
"""
Check the status of the delete instruction
"""
import requests
import json

def check_delete_instruction_status():
    backend_url = "http://127.0.0.1:8003"
    
    print("Checking agent status and recent tasks...")
    response = requests.get(f"{backend_url}/agents/status")
    if response.status_code == 200:
        data = response.json()
        print(f"Active tasks: {data.get('active_tasks', 0)}")
        print(f"Completed tasks: {data.get('completed_tasks', 0)}")
        
        # Check coordination data for recent instructions
        coordination = data.get("coordination", {})
        recent_instructions = coordination.get("recent_instructions", [])
        
        print(f"\nRecent instructions ({len(recent_instructions)}):")
        for instruction in recent_instructions[-3:]:
            timestamp = instruction.get('timestamp', '')
            instr_text = instruction.get('instruction', '')
            status = instruction.get('status', '')
            print(f"  {timestamp}: {instr_text}")
            print(f"    Status: {status}")
    else:
        print(f"Failed to get agent status: {response.status_code}")

if __name__ == "__main__":
    check_delete_instruction_status()
