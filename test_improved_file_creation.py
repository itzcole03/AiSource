#!/usr/bin/env python3
"""
Test the improved file creation functionality
"""
import requests
import json
import time
import os

def test_file_creation():
    backend_url = "http://127.0.0.1:8002"
    workspace = "C:\\Users\\bcmad\\OneDrive\\Desktop\\agenttest"
    
    print("Testing improved file creation...")
    
    # Test the story instruction
    instruction_payload = {
        "agent_id": "swarm",
        "action": "send_instruction", 
        "instruction": "write a story in a file called story.txt and make the story about pikachu vs kakashi from naruto",
        "workspace": workspace
    }
    
    response = requests.post(f"{backend_url}/agents/control", json=instruction_payload)
    if response.status_code == 200:
        result = response.json()
        print(f"Instruction sent successfully: {result}")
        
        # Wait for processing
        time.sleep(3)
        
        # Check if file was created
        story_file = os.path.join(workspace, "story.txt")
        if os.path.exists(story_file):
            print(f"\n✅ SUCCESS: story.txt was created!")
            with open(story_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"Content preview: {content[:200]}...")
        else:
            print(f"\n❌ FAILED: story.txt was not created")
            print("Files in workspace:")
            for file in os.listdir(workspace):
                print(f"  - {file}")
    else:
        print(f"Failed to send instruction: {response.status_code}")

if __name__ == "__main__":
    test_file_creation()
