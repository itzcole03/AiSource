#!/usr/bin/env python3
"""
Intelligent Agent Orchestrator

A comprehensive orchestration system that manages intelligent agents with
cross-provider model allocation, persistent learning, and real-time optimization.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import threading
from pathlib import Path

class WorkflowType(Enum):
    DEVELOPMENT = "development"
    RESEARCH = "research"
    ANALYSIS = "analysis"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    OPTIMIZATION = "optimization"

class ExecutionMode(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"

@dataclass
class WorkflowTask:
    """Individual task within a workflow"""
    task_id: str
    agent_role: str
    task_type: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    priority: int = 5  # 1-10 scale
    estimated_duration: int = 1800  # seconds
    required_models: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Workflow:
    """Complete workflow definition"""
    workflow_id: str
    name: str
    workflow_type: WorkflowType
    execution_mode: ExecutionMode
    tasks: List[WorkflowTask]
    global_context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ExecutionResult:
    """Result of task/workflow execution"""
    task_id: str
    agent_id: str
    model_used: str
    start_time: datetime
    end_time: datetime
    success: bool
    output: Any = None
    error: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)

class IntelligentAgentOrchestrator:
    """
    Advanced orchestrator that manages intelligent agents across complex workflows
    with autonomous model allocation and persistent learning
    """
    
    def __init__(self, output_dir: str = "orchestrator_outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Core components (will be initialized)
        self.memory_manager = None
        self.unified_intelligence = None
        self.persistent_intelligence = None
        self.coordination_system = None
        
        # Orchestrator state
        self.active_workflows: Dict[str, Workflow] = {}
        self.execution_results: List[ExecutionResult] = []
        self.agent_pool: Dict[str, Any] = {}
        self.workflow_templates: Dict[str, Workflow] = {}
        
        # Setup logging
        self.logger = logging.getLogger("IntelligentOrchestrator")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Background tasks
        self._background_tasks: Set[asyncio.Task] = set()
        
        # Initialize workflow templates
        self._initialize_workflow_templates()
    
    async def initialize(self):
        """Initialize all core components"""
        try:
            # Initialize memory manager
            from fixed_memory_manager import MemoryAwareModelManager
            self.memory_manager = MemoryAwareModelManager()
            await self.memory_manager.initialize()
            
            # Initialize unified intelligence
            from unified_model_intelligence import UnifiedModelIntelligence
            self.unified_intelligence = UnifiedModelIntelligence(self.memory_manager)
            
            # Initialize persistent intelligence
            from persistent_agent_intelligence import PersistentAgentIntelligence
            self.persistent_intelligence = PersistentAgentIntelligence()
            
            # Initialize coordination system (optional)
            try:
                from advanced_agent_coordination import AdvancedAgentCoordination
                self.coordination_system = AdvancedAgentCoordination()
            except ImportError:
                self.logger.warning("Advanced coordination system not available")
                self.coordination_system = None
            
            # Initialize agent pool
            await self._initialize_agent_pool()
            
            # Start background tasks
            await self._start_background_tasks()
            
            self.logger.info("Intelligent Agent Orchestrator initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _initialize_workflow_templates(self):
        """Initialize predefined workflow templates"""
        
        # Development workflow template
        dev_workflow = Workflow(
            workflow_id="dev_template",
            name="Software Development Workflow",
            workflow_type=WorkflowType.DEVELOPMENT,
            execution_mode=ExecutionMode.ADAPTIVE,
            tasks=[
                WorkflowTask(
                    task_id="analyze_requirements",
                    agent_role="architect",
                    task_type="analysis",
                    description="Analyze requirements and create system design",
                    priority=9
                ),
                WorkflowTask(
                    task_id="research_technologies",
                    agent_role="researcher",
                    task_type="research",
                    description="Research relevant technologies and best practices",
                    dependencies=["analyze_requirements"],
                    priority=7
                ),
                WorkflowTask(
                    task_id="implement_core",
                    agent_role="developer",
                    task_type="coding",
                    description="Implement core functionality",
                    dependencies=["analyze_requirements", "research_technologies"],
                    priority=8
                ),
                WorkflowTask(
                    task_id="create_tests",
                    agent_role="tester",
                    task_type="testing",
                    description="Create comprehensive test suite",
                    dependencies=["implement_core"],
                    priority=6
                ),
                WorkflowTask(
                    task_id="review_code",
                    agent_role="reviewer",
                    task_type="review",
                    description="Review code quality and architecture",
                    dependencies=["implement_core", "create_tests"],
                    priority=7
                ),
                WorkflowTask(
                    task_id="optimize_performance",
                    agent_role="developer",
                    task_type="optimization",
                    description="Optimize performance and resource usage",
                    dependencies=["review_code"],
                    priority=5
                )
            ]
        )
        
        # Research workflow template
        research_workflow = Workflow(
            workflow_id="research_template",
            name="Research and Analysis Workflow",
            workflow_type=WorkflowType.RESEARCH,
            execution_mode=ExecutionMode.PARALLEL,
            tasks=[
                WorkflowTask(
                    task_id="literature_review",
                    agent_role="researcher",
                    task_type="research",
                    description="Conduct comprehensive literature review",
                    priority=9
                ),
                WorkflowTask(
                    task_id="data_collection",
                    agent_role="researcher",
                    task_type="data_collection",
                    description="Collect and organize relevant data",
                    priority=8
                ),
                WorkflowTask(
                    task_id="analyze_data",
                    agent_role="analyst",
                    task_type="analysis",
                    description="Perform statistical and qualitative analysis",
                    dependencies=["data_collection"],
                    priority=9
                ),
                WorkflowTask(
                    task_id="synthesize_findings",
                    agent_role="researcher",
                    task_type="synthesis",
                    description="Synthesize findings and generate insights",
                    dependencies=["literature_review", "analyze_data"],
                    priority=8
                ),
                WorkflowTask(
                    task_id="create_report",
                    agent_role="writer",
                    task_type="documentation",
                    description="Create comprehensive research report",
                    dependencies=["synthesize_findings"],
                    priority=7
                )
            ]
        )
        
        self.workflow_templates = {
            "development": dev_workflow,
            "research": research_workflow
        }
    
    async def _initialize_agent_pool(self):
        """Initialize the pool of available agents"""
        try:
            # Try to import agent classes, fall back to mock agents if not available
            try:
                from agents.architect_agent import ArchitectAgent
                from agents.base_agent import BaseAgent
                
                # Create agent instances with proper parameters
                agents = [
                    {
                        "agent_id": "architect_001",
                        "role": "architect",
                        "status": "ready",
                        "agent_type": "architect"
                    },
                    {
                        "agent_id": "researcher_001", 
                        "role": "researcher",
                        "status": "ready",
                        "agent_type": "researcher"
                    },
                    {
                        "agent_id": "developer_001",
                        "role": "developer", 
                        "status": "ready",
                        "agent_type": "developer"
                    }
                ]
                
                for agent_info in agents:
                    self.agent_pool[agent_info["agent_id"]] = agent_info
                    self.logger.info(f"Initialized agent: {agent_info['agent_id']}")
                
            except ImportError:
                self.logger.warning("Agent classes not available, using mock agents")
                # Create mock agents for testing
                self.agent_pool = {
                    "architect_001": {"role": "architect", "status": "ready", "agent_type": "mock"},
                    "researcher_001": {"role": "researcher", "status": "ready", "agent_type": "mock"},
                    "developer_001": {"role": "developer", "status": "ready", "agent_type": "mock"}
                }
                
        except Exception as e:
            self.logger.error(f"Error initializing agent pool: {e}")
            # Fallback to basic mock agents
            self.agent_pool = {
                "fallback_001": {"role": "general", "status": "ready", "agent_type": "fallback"}
            }
    
    async def execute_workflow(self, workflow: Workflow) -> List[ExecutionResult]:
        """Execute a complete workflow"""
        self.logger.info(f"Starting workflow execution: {workflow.name}")
        
        # Add to active workflows
        self.active_workflows[workflow.workflow_id] = workflow
        
        try:
            if workflow.execution_mode == ExecutionMode.SEQUENTIAL:
                return await self._execute_sequential(workflow)
            elif workflow.execution_mode == ExecutionMode.PARALLEL:
                return await self._execute_parallel(workflow)
            elif workflow.execution_mode == ExecutionMode.ADAPTIVE:
                return await self._execute_adaptive(workflow)
            else:
                raise ValueError(f"Unknown execution mode: {workflow.execution_mode}")
                
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            raise
        finally:
            # Remove from active workflows
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]
    
    async def _execute_sequential(self, workflow: Workflow) -> List[ExecutionResult]:
        """Execute workflow tasks sequentially"""
        results = []
        
        # Sort tasks by dependencies and priority
        sorted_tasks = self._topological_sort(workflow.tasks)
        
        for task in sorted_tasks:
            result = await self._execute_task(task, workflow.global_context)
            results.append(result)
            
            # Update global context with task results
            if result.success and result.output:
                workflow.global_context[f"{task.task_id}_result"] = result.output
        
        return results
    
    async def _execute_parallel(self, workflow: Workflow) -> List[ExecutionResult]:
        """Execute workflow tasks in parallel where possible"""
        results = []
        completed_tasks = set()
        
        while len(completed_tasks) < len(workflow.tasks):
            # Find tasks that can be executed (dependencies satisfied)
            ready_tasks = [
                task for task in workflow.tasks
                if task.task_id not in completed_tasks
                and all(dep in completed_tasks for dep in task.dependencies)
            ]
            
            if not ready_tasks:
                break
            
            # Execute ready tasks in parallel
            task_futures = [
                self._execute_task(task, workflow.global_context)
                for task in ready_tasks
            ]
            
            batch_results = await asyncio.gather(*task_futures, return_exceptions=True)
            
            for i, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    self.logger.error(f"Task {ready_tasks[i].task_id} failed: {result}")
                    # Create error result
                    result = ExecutionResult(
                        task_id=ready_tasks[i].task_id,
                        agent_id="unknown",
                        model_used="none",
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        success=False,
                        error=str(result)
                    )
                
                results.append(result)
                completed_tasks.add(result.task_id)
                
                # Update global context
                if result.success and result.output:
                    workflow.global_context[f"{result.task_id}_result"] = result.output
        
        return results
    
    async def _execute_adaptive(self, workflow: Workflow) -> List[ExecutionResult]:
        """Execute workflow with adaptive scheduling based on resource availability"""
        results = []
        completed_tasks = set()
        running_tasks = {}
        
        while len(completed_tasks) < len(workflow.tasks) or running_tasks:
            # Find tasks that can be executed
            ready_tasks = [
                task for task in workflow.tasks
                if task.task_id not in completed_tasks
                and task.task_id not in running_tasks
                and all(dep in completed_tasks for dep in task.dependencies)
            ]
            
            # Check system resources
            if self.unified_intelligence:
                try:
                    system_status = await self.unified_intelligence.get_system_status()
                    available_slots = max(1, 3 - len(running_tasks))  # Max 3 concurrent tasks
                except:
                    available_slots = max(1, 2 - len(running_tasks))  # Conservative fallback
            else:
                available_slots = max(1, 2 - len(running_tasks))
            
            # Start new tasks based on priority and resource availability
            ready_tasks.sort(key=lambda t: t.priority, reverse=True)
            
            for task in ready_tasks[:available_slots]:
                task_future = asyncio.create_task(
                    self._execute_task(task, workflow.global_context)
                )
                running_tasks[task.task_id] = task_future
                self.logger.info(f"Started task: {task.task_id}")
            
            # Check for completed tasks
            if running_tasks:
                done, pending = await asyncio.wait(
                    running_tasks.values(),
                    timeout=1.0,
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for future in done:
                    # Find which task completed
                    completed_task_id = None
                    for task_id, task_future in running_tasks.items():
                        if task_future == future:
                            completed_task_id = task_id
                            break
                    
                    if completed_task_id:
                        try:
                            result = await future
                            results.append(result)
                            completed_tasks.add(completed_task_id)
                            
                            # Update global context
                            if result.success and result.output:
                                workflow.global_context[f"{result.task_id}_result"] = result.output
                            
                            self.logger.info(f"Completed task: {completed_task_id}")
                            
                        except Exception as e:
                            self.logger.error(f"Task {completed_task_id} failed: {e}")
                            result = ExecutionResult(
                                task_id=completed_task_id,
                                agent_id="unknown",
                                model_used="none",
                                start_time=datetime.now(),
                                end_time=datetime.now(),
                                success=False,
                                error=str(e)
                            )
                            results.append(result)
                            completed_tasks.add(completed_task_id)
                        
                        del running_tasks[completed_task_id]
            
            # Brief pause to prevent busy waiting
            await asyncio.sleep(0.1)
        
        return results
    
    async def _execute_task(self, task: WorkflowTask, global_context: Dict) -> ExecutionResult:
        """Execute a single task"""
        start_time = datetime.now()
        
        try:
            # Find suitable agent
            agent = await self._find_suitable_agent(task)
            if not agent:
                raise ValueError(f"No suitable agent found for task: {task.task_id}")
            
            # Request model allocation if unified intelligence is available
            model_key = "mock_model"
            if self.unified_intelligence:
                try:
                    from unified_model_intelligence import TaskRequest, TaskPriority, AgentRole
                    
                    # Map agent role
                    agent_role_map = {
                        "architect": AgentRole.ARCHITECT,
                        "researcher": AgentRole.RESEARCHER,
                        "developer": AgentRole.DEVELOPER,
                        "tester": AgentRole.TESTER,
                        "reviewer": AgentRole.REVIEWER
                    }
                    
                    task_request = TaskRequest(
                        agent_id=agent["agent_id"] if isinstance(agent, dict) else agent.agent_id,
                        agent_role=agent_role_map.get(task.agent_role, AgentRole.DEVELOPER),
                        task_type=task.task_type,
                        priority=TaskPriority.HIGH if task.priority >= 8 else TaskPriority.NORMAL,
                        estimated_duration=task.estimated_duration
                    )
                    
                    model_key = await self.unified_intelligence.request_model_allocation(task_request)
                    if not model_key:
                        model_key = "fallback_model"
                        self.logger.warning(f"Using fallback model for task: {task.task_id}")
                except Exception as e:
                    self.logger.warning(f"Model allocation failed, using mock: {e}")
                    model_key = "mock_model"
            
            # Execute task
            task_context = {**global_context, **task.context}
            
            if hasattr(agent, 'execute_task'):
                output = await agent.execute_task(task.description, task_context)
            else:
                # Mock execution for testing
                output = f"Executed {task.task_id}: {task.description} (using {model_key})"
                await asyncio.sleep(1)  # Simulate work
            
            # Release model allocation if unified intelligence is available
            if self.unified_intelligence and model_key != "mock_model":
                try:
                    await self.unified_intelligence.release_model_allocation(
                        agent["agent_id"] if isinstance(agent, dict) else agent.agent_id
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to release model allocation: {e}")
            
            return ExecutionResult(
                task_id=task.task_id,
                agent_id=agent["agent_id"] if isinstance(agent, dict) else agent.agent_id,
                model_used=model_key,
                start_time=start_time,
                end_time=datetime.now(),
                success=True,
                output=output
            )
            
        except Exception as e:
            return ExecutionResult(
                task_id=task.task_id,
                agent_id="unknown",
                model_used="none",
                start_time=start_time,
                end_time=datetime.now(),
                success=False,
                error=str(e)
            )
    
    async def _find_suitable_agent(self, task: WorkflowTask):
        """Find the most suitable agent for a task"""
        # Simple role-based matching for now
        for agent_id, agent in self.agent_pool.items():
            agent_role = agent.get("role") if isinstance(agent, dict) else getattr(agent, "role", None)
            if agent_role == task.agent_role:
                return agent if isinstance(agent, dict) else {"agent_id": agent_id, "role": agent_role}
        
        # Return first available agent as fallback
        if self.agent_pool:
            agent_id, agent = next(iter(self.agent_pool.items()))
            return agent if isinstance(agent, dict) else {"agent_id": agent_id}
        
        return None
    
    def _topological_sort(self, tasks: List[WorkflowTask]) -> List[WorkflowTask]:
        """Sort tasks topologically based on dependencies"""
        # Simple implementation - can be enhanced
        sorted_tasks = []
        remaining_tasks = tasks.copy()
        
        while remaining_tasks:
            # Find tasks with no unmet dependencies
            ready_tasks = [
                task for task in remaining_tasks
                if all(
                    dep in [t.task_id for t in sorted_tasks]
                    for dep in task.dependencies
                )
            ]
            
            if not ready_tasks:
                # Circular dependency or missing dependency
                ready_tasks = [remaining_tasks[0]]  # Take first task to break deadlock
            
            # Sort by priority
            ready_tasks.sort(key=lambda t: t.priority, reverse=True)
            
            # Add highest priority task
            task = ready_tasks[0]
            sorted_tasks.append(task)
            remaining_tasks.remove(task)
        
        return sorted_tasks
    
    async def _start_background_tasks(self):
        """Start background maintenance tasks"""
        # Start unified intelligence background tasks if available
        if self.unified_intelligence and hasattr(self.unified_intelligence, 'start_background_tasks'):
            try:
                task = asyncio.create_task(self.unified_intelligence.start_background_tasks())
                self._background_tasks.add(task)
            except Exception as e:
                self.logger.warning(f"Failed to start unified intelligence background tasks: {e}")
        
        # Start orchestrator monitoring
        task = asyncio.create_task(self._monitor_workflows())
        self._background_tasks.add(task)
    
    async def _monitor_workflows(self):
        """Monitor active workflows and system health"""
        while True:
            try:
                # Log system status
                if self.active_workflows:
                    if self.unified_intelligence:
                        try:
                            status = await self.unified_intelligence.get_system_status()
                            self.logger.info(f"Active workflows: {len(self.active_workflows)}, "
                                           f"VRAM usage: {status['memory_status']['current_usage_mb']}MB")
                        except:
                            self.logger.info(f"Active workflows: {len(self.active_workflows)}")
                    else:
                        self.logger.info(f"Active workflows: {len(self.active_workflows)}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in workflow monitoring: {e}")
                await asyncio.sleep(10)
    
    async def create_workflow_from_template(self, template_name: str, custom_context: Optional[Dict] = None) -> Workflow:
        """Create a workflow from a template"""
        if template_name not in self.workflow_templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = self.workflow_templates[template_name]
        
        # Create new workflow with unique ID
        workflow = Workflow(
            workflow_id=f"{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=f"{template.name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            workflow_type=template.workflow_type,
            execution_mode=template.execution_mode,
            tasks=template.tasks.copy(),
            global_context=custom_context or {}
        )
        
        return workflow
    
    async def save_execution_report(self, workflow_id: str, results: List[ExecutionResult]):
        """Save detailed execution report"""
        report_path = self.output_dir / f"execution_report_{workflow_id}.json"
        
        report = {
            'workflow_id': workflow_id,
            'execution_time': datetime.now().isoformat(),
            'total_tasks': len(results),
            'successful_tasks': sum(1 for r in results if r.success),
            'failed_tasks': sum(1 for r in results if not r.success),
            'results': [
                {
                    'task_id': r.task_id,
                    'agent_id': r.agent_id,
                    'model_used': r.model_used,
                    'duration_seconds': (r.end_time - r.start_time).total_seconds(),
                    'success': r.success,
                    'error': r.error
                }
                for r in results
            ]
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Execution report saved: {report_path}")

async def test_orchestrator():
    """Test the intelligent orchestrator"""
    print("=== Testing Intelligent Agent Orchestrator ===")
    
    orchestrator = IntelligentAgentOrchestrator()
    
    # Initialize
    success = await orchestrator.initialize()
    if not success:
        print("Failed to initialize orchestrator")
        return False
    
    # Create and execute a development workflow
    workflow = await orchestrator.create_workflow_from_template(
        "development",
        {"project_name": "Test Project", "target_platform": "Python"}
    )
    
    print(f"Created workflow: {workflow.name}")
    print(f"Tasks: {[task.task_id for task in workflow.tasks]}")
    
    # Execute workflow
    results = await orchestrator.execute_workflow(workflow)
    
    # Show results
    print(f"\n=== Execution Results ===")
    for result in results:
        status = "SUCCESS" if result.success else "FAILED"
        duration = (result.end_time - result.start_time).total_seconds()
        print(f"{result.task_id}: {status} ({duration:.1f}s) - Agent: {result.agent_id}, Model: {result.model_used}")
    
    # Save report
    await orchestrator.save_execution_report(workflow.workflow_id, results)
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_orchestrator())
    exit(0 if result else 1)
