#!/usr/bin/env python3
"""
Test script to directly test the enhanced agent manager
"""
import sys
import os
import time
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

try:
    from agents.enhanced_agent_manager import EnhancedAgentManager
    print("✅ Successfully imported EnhancedAgentManager")
    
    # Create an instance
    manager = EnhancedAgentManager()
    print("✅ Successfully created EnhancedAgentManager instance")
    
    # Send a test instruction
    instruction = "create a .txt file with the word 'test123'"
    workspace_path = str(Path(__file__).parent)
    
    print(f"📤 Sending instruction: {instruction}")
    print(f"📁 Workspace: {workspace_path}")
    
    result = manager.send_instruction(instruction, workspace_path)
    print(f"📋 Result: {result}")
    
    # Wait a moment for processing
    print("⏳ Waiting 10 seconds for task processing...")
    time.sleep(10)
    
    # Check agent status
    # status = manager.get_agent_status()
    # print(f"👥 Agent Status: {status}")
    
    # Check if file was created
    expected_file = os.path.join(workspace_path, "agent_created_file.txt")
    if os.path.exists(expected_file):
        print(f"✅ File created successfully: {expected_file}")
        with open(expected_file, 'r') as f:
            content = f.read()
            print(f"📄 File content: '{content}'")
    else:
        print(f"❌ File not found: {expected_file}")
        
    # List any .txt files that might have been created
    txt_files = list(Path(workspace_path).glob("*.txt"))
    if txt_files:
        print(f"📄 Found .txt files: {[str(f) for f in txt_files]}")
    else:
        print("📄 No .txt files found in workspace")
        
    # Stop the manager
    manager.stop()
    print("🛑 Stopped agent manager")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
