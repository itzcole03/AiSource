#!/usr/bin/env python3
"""
Direct test of Enhanced Agent Manager
"""
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.enhanced_agent_manager import EnhancedAgentManager

def test_direct_agent_manager():
    print("Testing Enhanced Agent Manager directly...")
      # Initialize the manager
    workspace = "C:\\Users\\bcmad\\OneDrive\\Desktop\\agenttest"
    manager = EnhancedAgentManager()
    manager.workspace_path = workspace  # Set workspace path after initialization
    
    print(f"Manager initialized with workspace: {workspace}")
    print(f"Number of agents: {len(manager.agents)}")
    
    # Send an instruction
    instruction = "create a file called direct_test.txt with the content 'Direct test successful'"
    print(f"\nSending instruction: {instruction}")
    
    result = manager.send_instruction(instruction, workspace)
    print(f"Send instruction result: {result}")
    
    # Wait a bit for processing
    import time
    time.sleep(3)
    
    # Check agent status
    status = manager.get_agent_status()
    print(f"\nAgent status:")
    print(f"  Active tasks: {status.get('active_tasks', 0)}")
    print(f"  Completed tasks: {status.get('completed_tasks', 0)}")
    print(f"  Task queue length: {status.get('task_queue_length', 0)}")
    
    # Check if file was created
    test_file = os.path.join(workspace, "direct_test.txt")
    if os.path.exists(test_file):
        print(f"\n✅ SUCCESS: direct_test.txt was created!")
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Content: {content}")
    else:
        print(f"\n❌ FAILED: direct_test.txt was not created")
    
    # Check task details
    all_tasks = manager.get_all_tasks()
    print(f"\nTotal tasks: {len(all_tasks)}")
    for task in all_tasks[-2:]:  # Show last 2 tasks
        print(f"  Task {task['id']}: {task['status']} - {task['instruction'][:50]}...")
        if task.get('result'):
            print(f"    Result: {task['result'].get('message', 'No message')}")

if __name__ == "__main__":
    test_direct_agent_manager()
