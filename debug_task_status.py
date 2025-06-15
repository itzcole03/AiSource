#!/usr/bin/env python3
"""
Debug script to check task queue status
"""
import requests
import json

def debug_task_status():
    backend_url = "http://127.0.0.1:8001"
    
    print("Checking current agent status and task queue...")
    response = requests.get(f"{backend_url}/agents/status")
    if response.status_code == 200:
        data = response.json()
        print(f"Active tasks: {data.get('active_tasks', 0)}")
        print(f"Completed tasks: {data.get('completed_tasks', 0)}")
        print(f"Task queue length: {data.get('task_queue_length', 0)}")
        
        agents = data.get("agents", {})
        for name, agent in agents.items():
            status = agent.get('status', 'unknown')
            current_task = agent.get('current_task')
            print(f"  {name}: {status}, current_task: {current_task}")
        
        # Check coordination data
        coordination = data.get("coordination", {})
        recent_instructions = coordination.get("recent_instructions", [])
        print(f"\nRecent instructions ({len(recent_instructions)}):")
        for instruction in recent_instructions[-3:]:
            print(f"  {instruction.get('timestamp', '')}: {instruction.get('instruction', '')}")
            print(f"    Status: {instruction.get('status', '')}")
    else:
        print(f"Failed to get agent status: {response.status_code}")

if __name__ == "__main__":
    debug_task_status()
