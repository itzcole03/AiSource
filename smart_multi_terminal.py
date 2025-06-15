#!/usr/bin/env python3
"""
Smart Multi-Terminal Agent Manager
Enables safe concurrent execution of intelligent agents with automatic coordination
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def check_running_instances() -> int:
    """Check how many instances are currently running"""
    coordination_dir = Path("logs/coordination")
    coordination_dir.mkdir(parents=True, exist_ok=True)
    
    active_instances = 0
    current_time = datetime.now()
    
    # Clean up stale instance files and count active ones
    for instance_file in coordination_dir.glob("instance_*.json"):
        try:
            with open(instance_file, 'r', encoding='utf-8') as f:
                instance_data = json.load(f)
            
            last_update = datetime.fromisoformat(instance_data.get('last_update', '2000-01-01'))
            
            # Consider instance active if updated within last 5 minutes
            if (current_time - last_update).total_seconds() < 300:
                active_instances += 1
            else:
                # Remove stale instance file
                instance_file.unlink(missing_ok=True)
                
        except Exception:
            # Remove corrupted instance file
            instance_file.unlink(missing_ok=True)
    
    return active_instances

def create_instance_marker(instance_id: str, focus_area: str) -> Path:
    """Create an instance marker file"""
    coordination_dir = Path("logs/coordination")
    coordination_dir.mkdir(parents=True, exist_ok=True)
    
    instance_file = coordination_dir / f"instance_{instance_id}.json"
    instance_data = {
        "instance_id": instance_id,
        "focus_area": focus_area,
        "start_time": datetime.now().isoformat(),
        "last_update": datetime.now().isoformat(),
        "pid": os.getpid()
    }
    
    with open(instance_file, 'w', encoding='utf-8') as f:
        json.dump(instance_data, f, indent=2)
    
    return instance_file

def get_recommended_focus_areas() -> List[str]:
    """Get recommended focus areas for different instances"""
    return [
        "frontend_development",
        "backend_optimization", 
        "api_enhancement",
        "security_improvement",
        "performance_tuning",
        "testing_qa",
        "deployment_automation",
        "general_development"
    ]

def main():
    """Main function to coordinate multiple instances"""
    print("Ultimate Copilot - Smart Multi-Terminal Agent Manager")
    print("=" * 65)
    
    # Check existing instances
    running_instances = check_running_instances()
    
    print(f"Currently running instances: {running_instances}")
    
    # Determine if safe to run multiple instances
    if running_instances == 0:
        print("No other instances detected - safe to start")
        instance_id = "primary"
        focus_area = "comprehensive_development"
    else:
        print(f"{running_instances} instance(s) already running")
        
        focus_areas = get_recommended_focus_areas()
        if running_instances < len(focus_areas):
            suggested_focus = focus_areas[running_instances]
            print(f"Suggested focus for this instance: {suggested_focus}")
            
            response = input(f"\\nStart additional instance focused on '{suggested_focus}'? (y/N): ").strip().lower()
            if response != 'y':
                print("Cancelled by user")
                return
            
            instance_id = f"instance_{running_instances + 1}"
            focus_area = suggested_focus
        else:
            print("Warning: Many instances already running. Performance may be impacted.")
            response = input("\\nStart additional general instance anyway? (y/N): ").strip().lower()
            if response != 'y':
                print("Cancelled by user")
                return
            
            instance_id = f"instance_{running_instances + 1}"
            focus_area = "general_support"
    
    # Create instance marker
    import uuid
    instance_id = f"{instance_id}_{str(uuid.uuid4())[:8]}"
    instance_file = create_instance_marker(instance_id, focus_area)    
    print(f"🏷️  Instance ID: {instance_id}")
    print(f"Focus Area: {focus_area}")
    print("=" * 65)
    
    # Set environment variables for this instance
    os.environ['COPILOT_INSTANCE_ID'] = instance_id
    os.environ['COPILOT_FOCUS_AREA'] = focus_area
    os.environ['COPILOT_INSTANCE_NUMBER'] = str(running_instances + 1)
    
    try:
        # Import and run the intelligent agents directly
        print(f"Launching intelligent agents with focus: {focus_area}")
        print("Starting agent system...")
          # Direct import and execution
        print("Importing intelligent agents...")
        import run_intelligent_agents
        
        print("Starting intelligent agent main function...")
        import asyncio
        
        # Call the main function from run_intelligent_agents
        asyncio.run(run_intelligent_agents.main())
        
    except KeyboardInterrupt:
        print(f"\\n🛑 Shutting down instance {instance_id}")
    except Exception as e:
        print(f"Error in instance {instance_id}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up instance marker
        try:
            instance_file.unlink(missing_ok=True)
        except Exception:
            pass
        print(f"🧹 Instance {instance_id} cleaned up")

if __name__ == "__main__":
    main()


