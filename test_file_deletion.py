#!/usr/bin/env python3
"""
Test the file deletion functionality directly
"""
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.enhanced_agent_manager import EnhancedAgentManager

def test_file_deletion():
    print("Testing file deletion functionality...")
    
    workspace = "C:\\Users\\bcmad\\OneDrive\\Desktop\\agenttest"
    manager = EnhancedAgentManager()
    manager.workspace_path = workspace
    
    # Check files before deletion
    print(f"\nFiles before deletion:")
    files_before = os.listdir(workspace)
    for file in files_before:
        if os.path.isfile(os.path.join(workspace, file)):
            print(f"  - {file}")
    
    print(f"\nTotal files: {len([f for f in files_before if os.path.isfile(os.path.join(workspace, f))])}")
    
    # Send deletion instruction
    instruction = "delete all the files in the workspace"
    print(f"\nSending instruction: {instruction}")
    
    result = manager.send_instruction(instruction, workspace)
    print(f"Send instruction result: {result}")
    
    # Wait for processing
    import time
    time.sleep(3)
    
    # Check files after deletion
    print(f"\nFiles after deletion:")
    files_after = os.listdir(workspace)
    remaining_files = [f for f in files_after if os.path.isfile(os.path.join(workspace, f))]
    
    if remaining_files:
        for file in remaining_files:
            print(f"  - {file}")
    else:
        print("  (no files remaining)")
    
    print(f"\nTotal files remaining: {len(remaining_files)}")
    
    # Check task status
    all_tasks = manager.get_all_tasks()
    deletion_task = all_tasks[-1] if all_tasks else None
    
    if deletion_task:
        print(f"\nTask details:")
        print(f"  Status: {deletion_task['status']}")
        print(f"  Agent: {deletion_task['agent_id']}")
        if deletion_task.get('result'):
            result = deletion_task['result']
            print(f"  Success: {result.get('status') == 'success'}")
            print(f"  Message: {result.get('message', 'no message')}")
            if 'files_deleted' in result:
                deleted = result['files_deleted']
                print(f"  Files deleted: {deleted}")

if __name__ == "__main__":
    test_file_deletion()
