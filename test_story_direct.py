#!/usr/bin/env python3
"""
Test the Enhanced Agent Manager directly with the story instruction
"""
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.enhanced_agent_manager import EnhancedAgentManager

def test_story_instruction():
    print("Testing story instruction directly...")
    
    workspace = "C:\\Users\\bcmad\\OneDrive\\Desktop\\agenttest"
    manager = EnhancedAgentManager()
    manager.workspace_path = workspace
    
    instruction = "write a story in a file called story.txt and make the story about pikachu vs kakashi from naruto"
    print(f"Instruction: {instruction}")
    
    try:
        result = manager.send_instruction(instruction, workspace)
        print(f"Send instruction result: {result}")
        
        # Wait for processing
        import time
        time.sleep(5)
        
        # Check all tasks
        all_tasks = manager.get_all_tasks()
        print(f"\nTotal tasks: {len(all_tasks)}")
        
        # Find the story task
        story_task = None
        for task in all_tasks:
            if "story.txt" in task['instruction']:
                story_task = task
                break
        
        if story_task:
            print(f"\nStory task found:")
            print(f"  ID: {story_task['id']}")
            print(f"  Status: {story_task['status']}")
            print(f"  Agent: {story_task['agent_id']}")
            
            if story_task.get('result'):
                result = story_task['result']
                print(f"  Result status: {result.get('status', 'unknown')}")
                print(f"  Message: {result.get('message', 'no message')}")
                print(f"  Files created: {result.get('files_created', [])}")
                if result.get('actions_taken'):
                    print("  Actions taken:")
                    for action in result['actions_taken']:
                        print(f"    - {action}")
        
        # Check if file exists
        story_file = os.path.join(workspace, "story.txt")
        if os.path.exists(story_file):
            print(f"\n✅ SUCCESS: story.txt was created!")
            with open(story_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"Content length: {len(content)} characters")
                print(f"First 200 characters: {content[:200]}...")
        else:
            print(f"\n❌ FAILED: story.txt was not created")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_story_instruction()
