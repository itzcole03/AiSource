#!/usr/bin/env python3
"""
Enhanced Dashboard Integration

Simple, focused dashboard that integrates with the enhanced agent system
and provides essential monitoring and control features.
"""

import asyncio
import json
import logging
import threading
import time
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger("EnhancedDashboard")

class EnhancedDashboardIntegration:
    """Simple dashboard integration with enhanced agent system"""
    
    def __init__(self):
        self.logger = logging.getLogger("EnhancedDashboard")
        self.enhanced_agents = None
        self.agent_statuses = {}
        self.task_history = []
        self.running = False
        
    async def initialize(self):
        """Initialize the dashboard and enhanced agent system"""
        try:
            self.logger.info("🚀 Initializing Enhanced Dashboard Integration...")
            
            # Initialize enhanced agent system
            try:
                from working_agent_upgrade import WorkingAgentUpgrade, dispatch_enhanced_task
                self.enhanced_agents = WorkingAgentUpgrade()
                await self.enhanced_agents.initialize()
                self.dispatch_task = dispatch_enhanced_task
                self.logger.info("✅ Enhanced agent system initialized")
            except ImportError as e:
                self.logger.error(f"Enhanced agent system not available: {e}")
                return False
            
            # Initialize agent statuses
            agent_names = ["architect", "backend", "frontend", "QA"]
            for name in agent_names:
                self.agent_statuses[name] = {
                    "status": "ready",
                    "last_activity": datetime.now(),
                    "current_task": None,
                    "error_count": 0
                }
            
            self.logger.info("✅ Dashboard integration initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Dashboard initialization failed: {e}")
            return False
    
    async def execute_task(self, agent_name: str, task_description: str) -> Dict[str, Any]:
        """Execute a task using the enhanced agent system"""
        try:
            # Update agent status
            self.agent_statuses[agent_name]["status"] = "working"
            self.agent_statuses[agent_name]["current_task"] = task_description[:50] + "..."
            self.agent_statuses[agent_name]["last_activity"] = datetime.now()
            
            self.logger.info(f"Executing task with {agent_name}: {task_description[:100]}...")
            
            # Execute using enhanced agents
            result = await self.dispatch_task(agent_name, task_description)
            
            # Update status based on result
            success = not result.get("error")
            self.agent_statuses[agent_name]["status"] = "completed" if success else "error"
            self.agent_statuses[agent_name]["current_task"] = None
            self.agent_statuses[agent_name]["last_activity"] = datetime.now()
            
            if not success:
                self.agent_statuses[agent_name]["error_count"] += 1
            
            # Add to task history
            task_record = {
                "timestamp": datetime.now().isoformat(),
                "agent": agent_name,
                "task": task_description,
                "status": "completed" if success else "error",
                "result": result
            }
            self.task_history.append(task_record)
            
            # Keep only last 100 tasks
            if len(self.task_history) > 100:
                self.task_history = self.task_history[-100:]
            
            self.logger.info(f"Task completed: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            self.agent_statuses[agent_name]["status"] = "error"
            self.agent_statuses[agent_name]["current_task"] = None
            self.agent_statuses[agent_name]["error_count"] += 1
            
            error_result = {"error": str(e)}
            task_record = {
                "timestamp": datetime.now().isoformat(),
                "agent": agent_name,
                "task": task_description,
                "status": "error",
                "result": error_result
            }
            self.task_history.append(task_record)
            
            return error_result
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        active_agents = sum(1 for status in self.agent_statuses.values() 
                          if status["status"] in ["working", "ready"])
        
        total_tasks = len(self.task_history)
        completed_tasks = len([t for t in self.task_history if t["status"] == "completed"])
        error_tasks = len([t for t in self.task_history if t["status"] == "error"])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "agents": {
                "total": len(self.agent_statuses),
                "active": active_agents,
                "statuses": dict(self.agent_statuses)
            },
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "errors": error_tasks,
                "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            },
            "enhanced_agents_available": self.enhanced_agents is not None
        }
    
    def get_agent_memory_info(self) -> Dict[str, Any]:
        """Get agent memory information"""
        if not self.enhanced_agents:
            return {"error": "Enhanced agents not available"}
        
        try:
            memory_info = {}
            if hasattr(self.enhanced_agents, 'memory_cache'):
                for agent_name, memory_data in self.enhanced_agents.memory_cache.items():
                    memory_info[agent_name] = {
                        "memory_size": len(str(memory_data)),
                        "last_updated": datetime.now().isoformat(),
                        "has_context": bool(memory_data.get("context"))
                    }
            
            return memory_info
        except Exception as e:
            return {"error": str(e)}
    
    async def test_all_agents(self) -> Dict[str, Any]:
        """Test all agents with a simple connectivity check"""
        test_task = "Test agent connectivity and basic functionality"
        results = {}
        
        for agent_name in self.agent_statuses.keys():
            self.logger.info(f"Testing agent: {agent_name}")
            result = await self.execute_task(agent_name, test_task)
            results[agent_name] = result
        
        return results
    
    def start_status_monitoring(self, interval: int = 10):
        """Start background status monitoring"""
        def monitor():
            while self.running:
                try:
                    status = self.get_system_status()
                    self.logger.info(f"System Status - Agents: {status['agents']['active']}/{status['agents']['total']}, "
                                   f"Tasks: {status['tasks']['completed']}/{status['tasks']['total']}")
                    time.sleep(interval)
                except Exception as e:
                    self.logger.error(f"Status monitoring error: {e}")
                    time.sleep(interval)
        
        self.running = True
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        self.logger.info(f"✅ Status monitoring started (interval: {interval}s)")
    
    def stop(self):
        """Stop the dashboard"""
        self.running = False
        self.logger.info("Dashboard stopped")

async def run_interactive_demo():
    """Run an interactive demo of the enhanced dashboard"""
    dashboard = EnhancedDashboardIntegration()
    
    # Initialize
    if not await dashboard.initialize():
        print("❌ Dashboard initialization failed")
        return
    
    print("🚀 Enhanced Dashboard Integration Demo")
    print("=====================================")
    
    # Start monitoring
    dashboard.start_status_monitoring(5)
    
    try:
        while True:
            print("\nAvailable commands:")
            print("1. status - Show system status")
            print("2. test - Test all agents")
            print("3. task <agent> <description> - Execute a task")
            print("4. memory - Show agent memory info")
            print("5. history - Show task history")
            print("6. quit - Exit")
            
            command = input("\nEnter command: ").strip().lower()
            
            if command == "quit":
                break
            elif command == "status":
                status = dashboard.get_system_status()
                print(json.dumps(status, indent=2))
            elif command == "test":
                print("Testing all agents...")
                results = await dashboard.test_all_agents()
                print("Test results:")
                for agent, result in results.items():
                    success = "✅" if not result.get("error") else "❌"
                    print(f"  {agent}: {success} {result.get('error', 'OK')}")
            elif command.startswith("task "):
                parts = command.split(" ", 2)
                if len(parts) >= 3:
                    agent = parts[1]
                    task_desc = parts[2]
                    if agent in dashboard.agent_statuses:
                        result = await dashboard.execute_task(agent, task_desc)
                        success = "✅" if not result.get("error") else "❌"
                        print(f"{success} Task result: {result}")
                    else:
                        print(f"❌ Unknown agent: {agent}")
                else:
                    print("❌ Usage: task <agent> <description>")
            elif command == "memory":
                memory_info = dashboard.get_agent_memory_info()
                print(json.dumps(memory_info, indent=2))
            elif command == "history":
                print(f"Last {min(10, len(dashboard.task_history))} tasks:")
                for task in dashboard.task_history[-10:]:
                    status_icon = "✅" if task["status"] == "completed" else "❌"
                    timestamp = task["timestamp"][:19]  # Remove microseconds
                    print(f"  {status_icon} [{timestamp}] {task['agent']}: {task['task'][:50]}...")
            else:
                print("❌ Unknown command")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping dashboard...")
    finally:
        dashboard.stop()

def main():
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Enhanced Dashboard Integration")
    print("============================")
    
    # Run interactive demo
    asyncio.run(run_interactive_demo())

if __name__ == "__main__":
    main()
