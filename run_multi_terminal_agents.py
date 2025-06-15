#!/usr/bin/env python3
"""
Multi-Terminal Intelligent Agent Launcher
Safely runs multiple intelligent agent instances with coordination
"""

import asyncio
import os
import sys
import time
import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class MultiTerminalAgentLauncher:
    """Coordinates multiple intelligent agent instances safely"""
    
    def __init__(self):
        self.workspace_root = Path(__file__).parent
        self.coordination_dir = self.workspace_root / "logs" / "coordination"
        self.coordination_dir.mkdir(parents=True, exist_ok=True)
        self.instance_id = str(uuid.uuid4())[:8]
        self.instance_file = self.coordination_dir / f"instance_{self.instance_id}.json"
        
    def check_running_instances(self) -> List[Dict[str, Any]]:
        """Check for other running instances"""
        instances = []
        if not self.coordination_dir.exists():
            return instances
            
        for instance_file in self.coordination_dir.glob("instance_*.json"):
            try:
                with open(instance_file, 'r', encoding='utf-8') as f:
                    instance_data = json.load(f)
                    
                # Check if instance is still alive (updated within last 5 minutes)
                last_update = datetime.fromisoformat(instance_data.get('last_update', '2000-01-01'))
                if (datetime.now() - last_update).total_seconds() < 300:
                    instances.append(instance_data)
                else:
                    # Remove stale instance file
                    instance_file.unlink(missing_ok=True)
                    
            except Exception as e:
                print(f"Error reading instance file {instance_file}: {e}")
                instance_file.unlink(missing_ok=True)
                
        return instances
    
    def register_instance(self, focus_area: str = "general") -> None:
        """Register this instance"""
        instance_data = {
            "instance_id": self.instance_id,
            "focus_area": focus_area,
            "start_time": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat(),
            "status": "active"
        }
        
        with open(self.instance_file, 'w', encoding='utf-8') as f:
            json.dump(instance_data, f, indent=2)
    
    def update_instance_heartbeat(self) -> None:
        """Update instance heartbeat"""
        try:
            if self.instance_file.exists():
                with open(self.instance_file, 'r', encoding='utf-8') as f:
                    instance_data = json.load(f)
                    
                instance_data['last_update'] = datetime.now().isoformat()
                
                with open(self.instance_file, 'w', encoding='utf-8') as f:
                    json.dump(instance_data, f, indent=2)
        except Exception as e:
            print(f"Error updating heartbeat: {e}")
    
    def suggest_focus_area(self, running_instances: List[Dict[str, Any]]) -> str:
        """Suggest a focus area based on running instances"""
        existing_focuses = [inst.get('focus_area', 'general') for inst in running_instances]
        
        focus_areas = [
            "frontend_ui", 
            "backend_api", 
            "database_optimization", 
            "security_enhancement",
            "performance_tuning",
            "testing_qa",
            "deployment_ops",
            "documentation"
        ]
        
        # Find an area not being focused on
        for area in focus_areas:
            if area not in existing_focuses:
                return area
        
        # If all areas covered, use general
        return "general_development"
    
    def cleanup_instance(self) -> None:
        """Cleanup instance registration"""
        try:
            if self.instance_file.exists():
                self.instance_file.unlink()
        except Exception as e:
            print(f"Error cleaning up instance: {e}")

def get_safe_agent_config(instance_id: str, focus_area: str) -> Dict[str, Any]:
    """Get agent configuration that avoids conflicts"""
    return {
        "instance_id": instance_id,
        "focus_area": focus_area,
        "log_suffix": f"_{instance_id}",
        "memory_namespace": f"ns_{instance_id}",
        "coordination_enabled": True,
        "file_lock_timeout": 30,
        "max_concurrent_file_ops": 2
    }

async def run_intelligent_agents_safely(config: Dict[str, Any]):
    """Run intelligent agents with safe concurrent execution"""
    instance_id = config["instance_id"]
    focus_area = config["focus_area"]
    
    print(f"Starting Intelligent Agents Instance: {instance_id}")
    print(f"Focus Area: {focus_area}")
    print(f"Safe Coordination: ENABLED")
    print("="*60)
    
    # Import and configure agents with instance-specific settings
    sys.path.append(str(Path(__file__).parent))
    
    try:
        # Import with the existing intelligent agents but modify for safe execution
        import importlib.util
        
        # Load the intelligent agents module
        spec = importlib.util.spec_from_file_location(
            "intelligent_agents_module", 
            Path(__file__).parent / "run_intelligent_agents.py"
        )
        intelligent_agents_module = importlib.util.module_from_spec(spec)
        
        # Set configuration for safe execution
        os.environ['AGENT_INSTANCE_ID'] = instance_id
        os.environ['AGENT_FOCUS_AREA'] = focus_area
        os.environ['AGENT_LOG_SUFFIX'] = config["log_suffix"]
        
        # Run the agents
        spec.loader.exec_module(intelligent_agents_module)
        
    except Exception as e:
        print(f"Error running intelligent agents: {e}")
        raise

def print_coordination_status(instances: List[Dict[str, Any]]):
    """Print current coordination status"""
    print("MULTI-TERMINAL COORDINATION STATUS")
    print("="*50)
    
    if not instances:
        print("No other instances detected")
        print("Safe to run single instance")
    else:
        print(f"{len(instances)} other instance(s) detected:")
        for i, inst in enumerate(instances, 1):
            focus = inst.get('focus_area', 'unknown')
            start_time = inst.get('start_time', 'unknown')
            print(f"   {i}. Instance {inst.get('instance_id', 'unknown')[:8]} - {focus}")
            print(f"      Started: {start_time}")
    
    print("="*50)

async def main():
    """Main coordination function"""
    launcher = MultiTerminalAgentLauncher()
    
    print("Ultimate Copilot - Multi-Terminal Intelligent Agent Coordinator")
    print("="*70)
    
    try:
        # Check for running instances
        running_instances = launcher.check_running_instances()
        print_coordination_status(running_instances)
        
        # Suggest focus area
        suggested_focus = launcher.suggest_focus_area(running_instances)
        
        print(f"Suggested Focus Area: {suggested_focus}")
        print(f"Instance ID: {launcher.instance_id}")
        
        # Ask user for confirmation
        if len(running_instances) > 0:
            print(f"Warning: {len(running_instances)} other instance(s) running")
            print("   This will coordinate safely with existing instances")
            
        response = input("\\nStart this instance? (y/N): ").lower().strip()
        
        if response != 'y':
            print("Cancelled by user")
            return
        
        # Register this instance
        launcher.register_instance(suggested_focus)
        print(f"Instance registered with focus: {suggested_focus}")
        
        # Get safe configuration
        config = get_safe_agent_config(launcher.instance_id, suggested_focus)
        
        # Start heartbeat task
        async def heartbeat_task():
            while True:
                await asyncio.sleep(60)  # Update every minute
                launcher.update_instance_heartbeat()
        
        heartbeat = asyncio.create_task(heartbeat_task())
        
        # Run the intelligent agents
        await run_intelligent_agents_safely(config)
        
    except KeyboardInterrupt:
        print("\\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        launcher.cleanup_instance()
        print("🧹 Instance cleanup completed")

if __name__ == "__main__":
    asyncio.run(main())


