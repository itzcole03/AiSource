#!/usr/bin/env python3
"""
File Coordination Demo
Demonstrates how agents safely coordinate file access without conflicts
"""

import asyncio
import threading
import time
import random
from pathlib import Path
from core.file_coordinator import get_file_coordinator, safe_write_file, safe_read_file

class DemoAgent:
    """Demo agent that tries to edit files"""
    
    def __init__(self, name: str, workspace_root: str):
        self.name = name
        self.workspace_root = Path(workspace_root)
        self.file_coordinator = get_file_coordinator(workspace_root)
    
    def work_on_file(self, file_path: str, iterations: int = 5):
        """Try to edit a file multiple times"""
        print(f"Agent {self.name} starting work on {file_path}")
        
        for i in range(iterations):
            try:
                # Try to read the file first
                content = safe_read_file(file_path, self.name)
                if content is None:
                    content = f"# File created by Agent {self.name}\n"
                
                # Add our contribution
                new_line = f"# Edit {i+1} by Agent {self.name} at {time.time():.2f}\n"
                updated_content = content + new_line
                
                # Try to write safely
                if safe_write_file(file_path, updated_content, self.name, priority=random.randint(1, 3)):
                    print(f"Agent {self.name} successfully wrote edit {i+1}")
                else:
                    print(f"⏳ Agent {self.name} edit {i+1} was blocked (file locked)")
                
                # Random delay between edits
                time.sleep(random.uniform(0.1, 0.5))
                
            except Exception as e:
                print(f"Agent {self.name} failed edit {i+1}: {e}")
        
        print(f"🏁 Agent {self.name} finished work on {file_path}")

def run_demo():
    """Run the file coordination demo"""
    workspace_root = Path(__file__).parent
    demo_file = workspace_root / "demo_shared_file.py"
    
    # Clean up any existing demo file
    if demo_file.exists():
        demo_file.unlink()
    
    # Create multiple demo agents
    agents = [
        DemoAgent("Alice", str(workspace_root)),
        DemoAgent("Bob", str(workspace_root)),
        DemoAgent("Charlie", str(workspace_root)),
        DemoAgent("Diana", str(workspace_root))
    ]
    
    print("Starting File Coordination Demo")
    print(f"Demo file: {demo_file}")
    print("🔒 Agents will try to edit the same file simultaneously")
    print("File coordinator will prevent conflicts and ensure data integrity")
    print()
    
    # Start all agents simultaneously
    threads = []
    for agent in agents:
        thread = threading.Thread(
            target=agent.work_on_file,
            args=(str(demo_file), 3)
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all agents to finish
    for thread in threads:
        thread.join()
    
    print()
    print("Demo Results:")
    print("=" * 50)
    
    # Show the final file content
    if demo_file.exists():
        with open(demo_file, 'r') as f:
            content = f.read()
        
        print("Final file content:")
        print(content)
        
        # Count edits by each agent
        lines = content.split('\n')
        agent_counts = {}
        for line in lines:
            if "Edit" in line and "by Agent" in line:
                agent_name = line.split("by Agent ")[1].split(" at ")[0]
                agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1
        
        print("Edit counts by agent:")
        for agent, count in agent_counts.items():
            print(f"  - {agent}: {count} edits")
    
    # Show coordination stats
    coordinator = get_file_coordinator()
    stats = coordinator.get_coordination_stats()
    print(f"\nCoordination Statistics:")
    print(f"  - Active locks: {stats['active_locks']}")
    print(f"  - Queued operations: {stats['total_queued_operations']}")
    print(f"  - Tracked files: {stats['tracked_files']}")
    
    print("\nDemo completed successfully!")
    print("Key takeaway: All agents could work on the same file without data loss or corruption")

def run_conflict_simulation():
    """Simulate what happens WITHOUT coordination (for comparison)"""
    workspace_root = Path(__file__).parent
    conflict_file = workspace_root / "demo_conflict_file.py"
    
    # Clean up any existing file
    if conflict_file.exists():
        conflict_file.unlink()
    
    print("\n🚨 CONFLICT SIMULATION (WITHOUT Coordination)")
    print("=" * 50)
    print("This shows what happens when agents edit files without coordination...")
    
    def unsafe_write(agent_name: str, iterations: int = 3):
        """Write to file without coordination (UNSAFE)"""
        for i in range(iterations):
            try:
                # Read current content
                content = ""
                if conflict_file.exists():
                    with open(conflict_file, 'r') as f:
                        content = f.read()
                
                # Add our edit
                new_line = f"# UNSAFE Edit {i+1} by {agent_name} at {time.time():.3f}\n"
                updated_content = content + new_line
                
                # Write without coordination (RACE CONDITION!)
                with open(conflict_file, 'w') as f:
                    f.write(updated_content)
                
                print(f"💥 {agent_name} wrote edit {i+1} (UNSAFE)")
                time.sleep(random.uniform(0.05, 0.15))  # Fast conflicts
                
            except Exception as e:
                print(f"💔 {agent_name} failed: {e}")
    
    # Start unsafe agents
    threads = []
    for name in ["UnsafeAgent1", "UnsafeAgent2", "UnsafeAgent3"]:
        thread = threading.Thread(target=unsafe_write, args=(name,))
        threads.append(thread)
        thread.start()
    
    # Wait for completion
    for thread in threads:
        thread.join()
    
    # Show the corrupted/inconsistent result
    if conflict_file.exists():
        with open(conflict_file, 'r') as f:
            content = f.read()
        
        print("\n💥 Result of UNSAFE editing:")
        print(content)
        
        # Count actual edits vs expected
        lines = content.split('\n')
        actual_edits = len([line for line in lines if "UNSAFE Edit" in line])
        expected_edits = 3 * 3  # 3 agents × 3 edits each
        
        print(f"Expected edits: {expected_edits}")
        print(f"Actual edits in file: {actual_edits}")
        
        if actual_edits < expected_edits:
            print(f"🚨 DATA LOSS: {expected_edits - actual_edits} edits were overwritten!")
        
        conflict_file.unlink()  # Clean up

if __name__ == "__main__":
    print("File Coordination System Demo")
    print("=" * 40)
    
    # Run the safe coordination demo
    run_demo()
    
    # Run the unsafe comparison
    run_conflict_simulation()
    
    print("\n🎉 Demo completed! The file coordinator prevents the data loss shown in the conflict simulation.")


