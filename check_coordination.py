#!/usr/bin/env python3
"""
Check File Coordination Status
Shows what agents are currently working and any file locks
"""

import time
from pathlib import Path
from core.file_coordinator import get_file_coordinator

def check_coordination_status():
    """Check and display current coordination status"""
    workspace_root = Path(__file__).parent
    coordinator = get_file_coordinator(str(workspace_root))
    
    print("File Coordination Status")
    print("=" * 40)
    
    stats = coordinator.get_coordination_stats()
    print(f"🔒 Active file locks: {stats['active_locks']}")
    print(f"⏳ Queued operations: {stats['total_queued_operations']}")
    print(f"Tracked files: {stats['tracked_files']}")
    print(f"📂 Coordination dir: {stats['coordination_dir']}")
    
    # Show lock details if any exist
    if stats['active_locks'] > 0:
        print(f"\nActive Lock Details:")
        coord_dir = Path(stats['coordination_dir'])
        
        for lock_file in coord_dir.glob("*.lock"):
            try:
                import json
                with open(lock_file, 'r') as f:
                    lock_data = json.load(f)
                
                file_path = lock_data.get('file_path', 'unknown')
                agent_id = lock_data.get('agent_id', 'unknown')
                timestamp = lock_data.get('timestamp', 'unknown')
                
                print(f"  🔒 {Path(file_path).name} locked by {agent_id} at {timestamp}")
            except:
                print(f"  🔒 {lock_file.name} (details unavailable)")
    
    # Show queue details if any exist
    if stats['total_queued_operations'] > 0:
        print(f"\n⏳ Queue Details:")
        coord_dir = Path(stats['coordination_dir'])
        
        for queue_file in coord_dir.glob("*.queue"):
            try:
                import json
                with open(queue_file, 'r') as f:
                    queue_data = json.load(f)
                
                if queue_data:
                    file_path = queue_file.name.replace('.queue', '').replace('_', '/')
                    print(f"  ⏳ {len(queue_data)} operations queued for {file_path}")
                    
                    for i, op in enumerate(queue_data[:3]):  # Show first 3
                        agent = op.get('agent_id', 'unknown')
                        op_type = op.get('operation_type', 'unknown')
                        priority = op.get('priority', 0)
                        print(f"    {i+1}. {agent} wants to {op_type} (priority: {priority})")
                    
                    if len(queue_data) > 3:
                        print(f"    ... and {len(queue_data) - 3} more")
            except:
                print(f"  ⏳ {queue_file.name} (details unavailable)")
    
    if stats['active_locks'] == 0 and stats['total_queued_operations'] == 0:
        print("\nNo coordination conflicts - all agents working smoothly!")

if __name__ == "__main__":
    try:
        while True:
            check_coordination_status()
            print("\n" + "=" * 40)
            print("Press Ctrl+C to stop monitoring...")
            time.sleep(5)
            print("\033[H\033[J", end="")  # Clear screen
    except KeyboardInterrupt:
        print("\n👋 Coordination monitoring stopped.")


