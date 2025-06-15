#!/usr/bin/env python3
"""
Check agent task status and details
"""

import sys
import os
sys.path.append('.')

from agents.enhanced_agent_manager import EnhancedAgentManager

def main():
    print("Initializing Enhanced Agent Manager...")
    manager = EnhancedAgentManager()
    
    print(f"\nAgent Manager Status:")
    print(f"Active tasks: {len([t for t in manager.tasks.values() if t.status in ['pending', 'in_progress']])}")
    print(f"Completed tasks: {len([t for t in manager.tasks.values() if t.status == 'completed'])}")
    print(f"Total tasks: {len(manager.tasks)}")
    print(f"Task queue length: {len(manager.task_queue)}")
    
    print(f"\nTask Details:")
    for task_id, task in manager.tasks.items():
        print(f"Task {task_id}:")
        print(f"  Status: {task.status}")
        print(f"  Instruction: {task.instruction}")
        print(f"  Workspace: {task.workspace_path}")
        print(f"  Started: {task.started_at}")
        print(f"  Completed: {task.completed_at}")
        if task.result:
            print(f"  Result: {task.result}")
        print("")

if __name__ == "__main__":
    main()
