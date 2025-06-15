#!/usr/bin/env python3
"""
Specialized Role Agents Runner
Uses the existing role-based agents with their specific model assignments.
Each agent has designated models and doesn't stall.
"""

import asyncio
import os
import sys
import time
import yaml
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.architect_agent import ArchitectAgent
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.qa_agent import QAAgent
from agents.orchestrator_agent import OrchestratorAgent
from core.real_llm_manager import RealLLMManager
from core.advanced_memory_manager import AdvancedMemoryManager
from core.file_coordinator import get_file_coordinator, safe_write_file

class SpecializedAgentCoordinator:
    """Coordinates specialized role-based agents with their designated models"""
    
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        
        # Initialize core systems
        self.llm_manager = RealLLMManager()
        self.memory_manager = AdvancedMemoryManager()
        self.file_coordinator = get_file_coordinator(str(workspace_root))
        
        # Setup logging
        self.logs_dir = self.workspace_root / "logs" / "specialized_agents"
        self.logs_dir.mkdir(exist_ok=True, parents=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("SpecializedCoordinator")
        
        # Load configurations
        self.models_config = self._load_models_config()
        self.agents = {}
        self.task_queue = []
        self.active_tasks = {}
        
        # Performance tracking
        self.start_time = time.time()
        self.total_tasks_completed = 0
        self.agent_stats = {}
    
    def _load_models_config(self) -> Dict:
        """Load models configuration"""
        config_path = self.workspace_root / "config" / "models_config.yaml"
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Could not load models config: {e}, using defaults")
            return {"agent_assignments": {}}
    
    async def initialize_agents(self):
        """Initialize all specialized agents"""
        self.logger.info("Initializing specialized role-based agents...")
        
        agent_configs = {
            "architect": {
                "role": "System Architect",
                "models": self.models_config.get("agent_assignments", {}).get("architect", {}).get("primary", ["ollama/mistral"]),
                "fallback_models": self.models_config.get("agent_assignments", {}).get("architect", {}).get("fallback", ["ollama/llama3"]),
                "specialties": ["system_design", "architecture_review", "technology_selection"]
            },
            "backend": {
                "role": "Backend Developer", 
                "models": self.models_config.get("agent_assignments", {}).get("backend_dev", {}).get("primary", ["ollama/codellama"]),
                "fallback_models": self.models_config.get("agent_assignments", {}).get("backend_dev", {}).get("fallback", ["ollama/llama3"]),
                "specialties": ["api_development", "database_design", "performance_optimization", "security_implementation"]
            },
            "frontend": {
                "role": "Frontend Developer",
                "models": self.models_config.get("agent_assignments", {}).get("frontend_dev", {}).get("primary", ["ollama/codellama"]),
                "fallback_models": self.models_config.get("agent_assignments", {}).get("frontend_dev", {}).get("fallback", ["ollama/llama3"]),
                "specialties": ["component_development", "ui_design", "performance_optimization", "accessibility"]
            },
            "qa": {
                "role": "QA Analyst",
                "models": self.models_config.get("agent_assignments", {}).get("qa_analyst", {}).get("primary", ["ollama/llama3"]),
                "fallback_models": self.models_config.get("agent_assignments", {}).get("qa_analyst", {}).get("fallback", ["ollama/mistral"]),
                "specialties": ["test_planning", "quality_assurance", "bug_analysis", "test_automation"]
            },
            "orchestrator": {
                "role": "Task Orchestrator",
                "models": self.models_config.get("agent_assignments", {}).get("orchestrator", {}).get("primary", ["ollama/mistral"]),
                "fallback_models": self.models_config.get("agent_assignments", {}).get("orchestrator", {}).get("fallback", ["ollama/llama3"]),
                "specialties": ["task_coordination", "resource_management", "workflow_optimization"]
            }
        }
        
        # Initialize each agent
        for agent_id, config in agent_configs.items():
            try:
                if agent_id == "architect":
                    agent = ArchitectAgent(agent_id, config, self.llm_manager, self.memory_manager)
                elif agent_id == "backend":
                    agent = BackendAgent(agent_id, config, self.llm_manager, self.memory_manager)
                elif agent_id == "frontend":
                    agent = FrontendAgent(agent_id, config, self.llm_manager, self.memory_manager)
                elif agent_id == "qa":
                    agent = QAAgent(agent_id, config, self.llm_manager, self.memory_manager)
                elif agent_id == "orchestrator":
                    agent = OrchestratorAgent(agent_id, config, self.llm_manager, self.memory_manager)
                
                await agent.initialize()
                self.agents[agent_id] = agent
                self.agent_stats[agent_id] = {
                    "tasks_completed": 0,
                    "tasks_failed": 0,
                    "total_time": 0,
                    "last_active": datetime.now()
                }
                
                self.logger.info(f"Initialized {agent_id} agent with models: {config['models']}")
                
            except Exception as e:
                self.logger.error(f"Failed to initialize {agent_id} agent: {e}")
        
        self.logger.info(f"Initialized {len(self.agents)} specialized agents")
    
    def _generate_diverse_tasks(self) -> List[Dict]:
        """Generate diverse tasks for each agent specialty"""
        tasks = []
        
        # Architecture tasks
        arch_tasks = [
            {
                "id": "arch_001",
                "title": "Design Ultimate Copilot Core Architecture",
                "description": "Design a scalable, modular architecture for the AI agent system",
                "type": "system_design",
                "priority": 9,
                "agent_preference": "architect",
                "complexity": 8,
                "estimated_time": 30
            },
            {
                "id": "arch_002", 
                "title": "Review Agent Communication Patterns",
                "description": "Analyze and optimize how agents communicate and coordinate",
                "type": "architecture_review",
                "priority": 7,
                "agent_preference": "architect",
                "complexity": 6,
                "estimated_time": 20
            }
        ]
        
        # Backend tasks
        backend_tasks = [
            {
                "id": "be_001",
                "title": "Implement Agent API Gateway",
                "description": "Create a unified API gateway for agent interactions",
                "type": "api_development",
                "priority": 8,
                "agent_preference": "backend",
                "complexity": 7,
                "estimated_time": 40,
                "file_to_create": "api/agent_gateway.py"
            },
            {
                "id": "be_002",
                "title": "Design Agent Memory Database Schema",
                "description": "Create optimal database schema for agent memory and coordination",
                "type": "database_design",
                "priority": 8,
                "agent_preference": "backend",
                "complexity": 6,
                "estimated_time": 25,
                "file_to_create": "database/agent_memory_schema.sql"
            },
            {
                "id": "be_003",
                "title": "Implement Agent Performance Monitoring",
                "description": "Create comprehensive monitoring for agent performance and health",
                "type": "performance_optimization",
                "priority": 7,
                "agent_preference": "backend",
                "complexity": 6,
                "estimated_time": 30,
                "file_to_create": "monitoring/agent_performance.py"
            }
        ]
        
        # Frontend tasks
        frontend_tasks = [
            {
                "id": "fe_001",
                "title": "Create Agent Dashboard UI",
                "description": "Build a real-time dashboard to monitor all agents",
                "type": "component_development",
                "priority": 8,
                "agent_preference": "frontend",
                "complexity": 7,
                "estimated_time": 35,
                "file_to_create": "frontend/components/AgentDashboard.tsx"
            },
            {
                "id": "fe_002",
                "title": "Design Agent Visualization Interface",
                "description": "Create visual representations of agent workflows and status",
                "type": "ui_design",
                "priority": 6,
                "agent_preference": "frontend",
                "complexity": 5,
                "estimated_time": 25,
                "file_to_create": "frontend/components/AgentVisualizer.tsx"
            }
        ]
        
        # QA tasks
        qa_tasks = [
            {
                "id": "qa_001",
                "title": "Create Agent Integration Test Suite",
                "description": "Develop comprehensive tests for agent coordination and file safety",
                "type": "test_planning",
                "priority": 9,
                "agent_preference": "qa",
                "complexity": 7,
                "estimated_time": 30,
                "file_to_create": "test/agent_integration_tests.py"
            },
            {
                "id": "qa_002",
                "title": "Analyze Agent Coordination Quality",
                "description": "Evaluate the effectiveness of agent coordination and file safety",
                "type": "quality_assurance",
                "priority": 8,
                "agent_preference": "qa",
                "complexity": 6,
                "estimated_time": 20
            }
        ]
        
        # Orchestrator tasks  
        orchestrator_tasks = [
            {
                "id": "orch_001",
                "title": "Optimize Agent Task Distribution",
                "description": "Improve how tasks are distributed among agents based on capability and load",
                "type": "task_coordination",
                "priority": 8,
                "agent_preference": "orchestrator",
                "complexity": 7,
                "estimated_time": 25
            }
        ]
        
        tasks.extend(arch_tasks)
        tasks.extend(backend_tasks)
        tasks.extend(frontend_tasks)
        tasks.extend(qa_tasks)
        tasks.extend(orchestrator_tasks)
        
        return tasks
    
    def _assign_task_to_agent(self, task: Dict) -> Optional[str]:
        """Intelligently assign task to best suited agent"""
        # Prefer agent specified in task
        preferred_agent = task.get("agent_preference")
        if preferred_agent and preferred_agent in self.agents:
            agent = self.agents[preferred_agent]
            if agent.status == "ready" and task.get("type") in agent.config.get("specialties", []):
                return preferred_agent
        
        # Find agent by task type and availability
        task_type = task.get("type", "generic")
        available_agents = []
        
        for agent_id, agent in self.agents.items():
            if agent.status == "ready" and task_type in agent.config.get("specialties", []):
                available_agents.append((agent_id, self.agent_stats[agent_id]["tasks_completed"]))
        
        # Prefer agents with fewer completed tasks (load balancing)
        if available_agents:
            available_agents.sort(key=lambda x: x[1])
            return available_agents[0][0]
        
        # Fallback to any available agent
        for agent_id, agent in self.agents.items():
            if agent.status == "ready":
                return agent_id
        
        return None
    
    async def _execute_agent_task(self, agent_id: str, task: Dict) -> Dict:
        """Execute a task with a specific agent"""
        agent = self.agents[agent_id]
        start_time = time.time()
        
        try:
            self.logger.info(f"Agent {agent_id} starting task: {task['title']}")
            self.active_tasks[task["id"]] = {
                "agent": agent_id,
                "task": task,
                "start_time": start_time
            }
            
            # Execute task with timeout
            result = await asyncio.wait_for(
                agent.execute_task(task),
                timeout=60.0  # 1 minute timeout per task
            )
            
            execution_time = time.time() - start_time
            
            # Update stats
            self.agent_stats[agent_id]["tasks_completed"] += 1
            self.agent_stats[agent_id]["total_time"] += execution_time
            self.agent_stats[agent_id]["last_active"] = datetime.now()
            
            # Handle file creation if specified
            if task.get("file_to_create") and result.get("content"):
                file_path = self.workspace_root / task["file_to_create"]
                if safe_write_file(str(file_path), result["content"], agent_id, priority=task.get("priority", 5)):
                    self.logger.info(f"Agent {agent_id} created file: {task['file_to_create']}")
                else:
                    self.logger.warning(f"Agent {agent_id} failed to create file: {task['file_to_create']}")
            
            self.logger.info(f"Agent {agent_id} completed task in {execution_time:.1f}s: {task['title']}")
            
            return {
                "success": True,
                "agent": agent_id,
                "task_id": task["id"],
                "execution_time": execution_time,
                "result": result
            }
            
        except asyncio.TimeoutError:
            self.logger.warning(f"⏰ Agent {agent_id} timed out on task: {task['title']}")
            self.agent_stats[agent_id]["tasks_failed"] += 1
            return {
                "success": False,
                "agent": agent_id,
                "task_id": task["id"],
                "error": "timeout",
                "execution_time": time.time() - start_time
            }
            
        except Exception as e:
            self.logger.error(f"Agent {agent_id} failed task: {task['title']} - {e}")
            self.agent_stats[agent_id]["tasks_failed"] += 1
            return {
                "success": False,
                "agent": agent_id,
                "task_id": task["id"],
                "error": str(e),
                "execution_time": time.time() - start_time
            }
        
        finally:
            if task["id"] in self.active_tasks:
                del self.active_tasks[task["id"]]
    
    async def run_agent_coordination(self):
        """Main coordination loop"""
        self.logger.info("🎬 Starting specialized agent coordination...")
        
        # Generate initial tasks
        tasks = self._generate_diverse_tasks()
        self.task_queue.extend(tasks)
        self.logger.info(f"Generated {len(tasks)} diverse tasks")
        
        concurrent_tasks = 3  # Run up to 3 tasks concurrently
        running_tasks = []
        
        while self.task_queue or running_tasks:
            # Start new tasks if we have capacity and tasks available
            while len(running_tasks) < concurrent_tasks and self.task_queue:
                task = self.task_queue.pop(0)
                agent_id = self._assign_task_to_agent(task)
                
                if agent_id:
                    task_future = asyncio.create_task(self._execute_agent_task(agent_id, task))
                    running_tasks.append(task_future)
                    self.logger.info(f"Assigned task '{task['title']}' to agent {agent_id}")
                else:
                    # No available agents, put task back and wait
                    self.task_queue.insert(0, task)
                    break
              # Wait for at least one task to complete
            if running_tasks:
                done, pending = await asyncio.wait(
                    running_tasks, 
                    return_when=asyncio.FIRST_COMPLETED,
                    timeout=1.0
                )
                running_tasks = list(pending)  # Convert set back to list
                
                # Process completed tasks
                for task_future in done:
                    result = await task_future
                    if result["success"]:
                        self.total_tasks_completed += 1
                        self.logger.info(f"🎉 Task completed successfully by {result['agent']}")
                    else:
                        self.logger.warning(f"Task failed: {result.get('error', 'unknown')}")
            
            # Brief pause to prevent busy waiting
            await asyncio.sleep(0.1)
        
        self.logger.info("🏁 All tasks completed!")
    
    def print_final_stats(self):
        """Print final performance statistics"""
        total_time = time.time() - self.start_time
        
        print("\n" + "="*60)
        print("SPECIALIZED AGENTS PERFORMANCE REPORT")
        print("="*60)
        print(f"⏱️  Total Runtime: {total_time:.1f} seconds")
        print(f"Tasks Completed: {self.total_tasks_completed}")
        print(f"Tasks/Minute: {(self.total_tasks_completed / total_time * 60):.1f}")
        
        print(f"\nAGENT PERFORMANCE:")
        for agent_id, stats in self.agent_stats.items():
            if stats["tasks_completed"] > 0:
                avg_time = stats["total_time"] / stats["tasks_completed"]
                success_rate = stats["tasks_completed"] / (stats["tasks_completed"] + stats["tasks_failed"]) * 100
                print(f"  {agent_id.title()}: {stats['tasks_completed']} tasks, {avg_time:.1f}s avg, {success_rate:.1f}% success")
        
        # File coordination stats
        coord_stats = self.file_coordinator.get_coordination_stats()
        print(f"\n🔒 FILE COORDINATION:")
        print(f"  - Files tracked: {coord_stats['tracked_files']}")
        print(f"  - Active locks: {coord_stats['active_locks']}")
        print(f"  - Queued operations: {coord_stats['total_queued_operations']}")
        
        print("\n🎉 All agents completed their specialized work successfully!")
        print("="*60)

async def main():
    """Main entry point"""
    workspace_root = Path(__file__).parent
    coordinator = SpecializedAgentCoordinator(str(workspace_root))
    
    try:
        # Initialize all specialized agents
        await coordinator.initialize_agents()
        
        # Run coordination
        await coordinator.run_agent_coordination()
        
    except KeyboardInterrupt:
        coordinator.logger.info("🛑 Coordination stopped by user")
    except Exception as e:
        coordinator.logger.error(f"Coordination failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Print final statistics
        coordinator.print_final_stats()

if __name__ == "__main__":
    asyncio.run(main())


