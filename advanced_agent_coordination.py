#!/usr/bin/env python3
"""
Advanced Agent Coordination System

This system manages complex multi-agent workflows with intelligent coordination,
collaboration, and conflict resolution capabilities.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid

class CollaborationMode(Enum):
    SEQUENTIAL = "sequential"  # Agents work one after another
    PARALLEL = "parallel"     # Agents work simultaneously
    PIPELINE = "pipeline"     # Output of one feeds into another
    CONSENSUS = "consensus"   # Agents collaborate to reach agreement
    COMPETITIVE = "competitive"  # Agents compete for best solution

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    DELEGATED = "delegated"

@dataclass
class CollaborativeTask:
    """A task that can involve multiple agents"""
    id: str
    description: str
    collaboration_mode: CollaborationMode
    required_agents: List[str]
    optional_agents: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Other task IDs
    priority: int = 5  # 1-10 scale
    deadline: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    assigned_agents: Set[str] = field(default_factory=set)
    results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class AgentCapability:
    """Describes an agent's capability"""
    name: str
    proficiency: float  # 0.0 to 1.0
    experience_count: int
    success_rate: float
    avg_completion_time: float
    specializations: List[str]

class AdvancedAgentCoordinator:
    """
    Advanced coordination system for managing complex multi-agent workflows
    """
    
    def __init__(self, model_intelligence, agent_intelligence):
        self.model_intelligence = model_intelligence
        self.agent_intelligence = agent_intelligence
        self.active_tasks: Dict[str, CollaborativeTask] = {}
        self.agent_capabilities: Dict[str, AgentCapability] = {}
        self.collaboration_history: List[Dict] = []
        
        # Setup logging
        self.logger = logging.getLogger("AdvancedCoordinator")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    async def register_agent_capabilities(self, agent_id: str, role: str):
        """Register and analyze agent capabilities"""
        
        # Get agent's expertise from intelligence system
        expertise = self.agent_intelligence.get_agent_expertise_summary(role)
        
        # Calculate proficiency based on experience and success rate
        experience_factor = min(expertise.get('experience_count', 0) / 100.0, 1.0)
        success_factor = expertise.get('average_success_rate', 0.5)
        proficiency = (experience_factor * 0.4) + (success_factor * 0.6)
        
        capability = AgentCapability(
            name=agent_id,
            proficiency=proficiency,
            experience_count=expertise.get('experience_count', 0),
            success_rate=expertise.get('average_success_rate', 0.5),
            avg_completion_time=0.0,  # Will be updated from performance data
            specializations=list(expertise.get('specializations', {}).keys())        )
        
        self.agent_capabilities[agent_id] = capability
        self.logger.info(f"Registered agent {agent_id} with proficiency {proficiency:.2f}")
    
    async def create_collaborative_task(self, description: str, collaboration_mode: CollaborationMode,
                                      required_agents: List[str], optional_agents: Optional[List[str]] = None,
                                      priority: int = 5, deadline: Optional[datetime] = None,
                                      dependencies: Optional[List[str]] = None) -> str:
        """Create a new collaborative task"""
        
        task_id = str(uuid.uuid4())[:8]
        
        task = CollaborativeTask(
            id=task_id,
            description=description,
            collaboration_mode=collaboration_mode,
            required_agents=required_agents,
            optional_agents=optional_agents or [],
            dependencies=dependencies or [],
            priority=priority,
            deadline=deadline
        )
        
        self.active_tasks[task_id] = task
        self.logger.info(f"Created collaborative task {task_id}: {description}")
        
        return task_id
    
    async def assign_optimal_agents(self, task_id: str) -> bool:
        """Assign optimal agents to a task based on capabilities and availability"""
        
        task = self.active_tasks.get(task_id)
        if not task:
            return False
        
        # Check if dependencies are satisfied
        if not await self._check_dependencies(task):
            task.status = TaskStatus.BLOCKED
            return False
        
        # Find optimal agent assignment
        optimal_assignment = await self._find_optimal_assignment(task)
        
        if not optimal_assignment:
            self.logger.warning(f"Could not find optimal assignment for task {task_id}")
            return False
        
        # Assign agents
        task.assigned_agents = set(optimal_assignment)
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        
        self.logger.info(f"Assigned agents {optimal_assignment} to task {task_id}")
        return True
    
    async def _check_dependencies(self, task: CollaborativeTask) -> bool:
        """Check if task dependencies are satisfied"""
        
        for dep_id in task.dependencies:
            if dep_id in self.active_tasks:
                dep_task = self.active_tasks[dep_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
        
        return True
    
    async def _find_optimal_assignment(self, task: CollaborativeTask) -> List[str]:
        """Find optimal agent assignment using capability matching"""
        
        # Start with required agents
        assignment = task.required_agents.copy()
        
        # Add optional agents if they would improve the outcome
        for agent_id in task.optional_agents:
            if agent_id in self.agent_capabilities:
                capability = self.agent_capabilities[agent_id]
                
                # Check if agent's specializations match task requirements
                task_keywords = set(task.description.lower().split())
                agent_specializations = set(spec.lower() for spec in capability.specializations)
                
                if task_keywords.intersection(agent_specializations):
                    if capability.proficiency > 0.7:  # Only add high-proficiency optional agents
                        assignment.append(agent_id)
        
        # Ensure we have capabilities for the collaboration mode
        if task.collaboration_mode == CollaborationMode.CONSENSUS:
            # Need at least 3 agents for meaningful consensus
            while len(assignment) < 3 and len(task.optional_agents) > 0:
                best_optional = max(
                    [a for a in task.optional_agents if a not in assignment],
                    key=lambda a: self.agent_capabilities.get(a, AgentCapability("", 0, 0, 0, 0, [])).proficiency,
                    default=None
                )
                if best_optional:
                    assignment.append(best_optional)
                else:
                    break
        
        return assignment
    
    async def execute_collaborative_task(self, task_id: str) -> Dict[str, Any]:
        """Execute a collaborative task with the assigned agents"""
        
        task = self.active_tasks.get(task_id)
        if not task or task.status != TaskStatus.IN_PROGRESS:
            return {"error": "Task not ready for execution"}
        
        self.logger.info(f"Executing collaborative task {task_id} with mode {task.collaboration_mode.value}")
        
        try:
            if task.collaboration_mode == CollaborationMode.SEQUENTIAL:
                result = await self._execute_sequential(task)
            elif task.collaboration_mode == CollaborationMode.PARALLEL:
                result = await self._execute_parallel(task)
            elif task.collaboration_mode == CollaborationMode.PIPELINE:
                result = await self._execute_pipeline(task)
            elif task.collaboration_mode == CollaborationMode.CONSENSUS:
                result = await self._execute_consensus(task)
            elif task.collaboration_mode == CollaborationMode.COMPETITIVE:
                result = await self._execute_competitive(task)
            else:
                result = {"error": "Unknown collaboration mode"}
            
            if "error" not in result:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.results = result
                
                # Record collaboration success
                await self._record_collaboration_success(task)
            else:
                task.status = TaskStatus.FAILED
            
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            task.status = TaskStatus.FAILED
            return {"error": str(e)}
    
    async def _execute_sequential(self, task: CollaborativeTask) -> Dict[str, Any]:
        """Execute task with agents working sequentially"""
        
        results = []
        current_input = {"task": task.description}
        
        for agent_id in task.assigned_agents:
            self.logger.info(f"Agent {agent_id} starting sequential work")
            
            # Simulate agent work (in real implementation, call actual agent)
            agent_result = await self._simulate_agent_work(agent_id, current_input, task)
            results.append({"agent": agent_id, "result": agent_result})
            
            # Pass result to next agent
            current_input["previous_result"] = agent_result
        
        return {
            "mode": "sequential",
            "results": results,
            "final_output": results[-1]["result"] if results else None
        }
    
    async def _execute_parallel(self, task: CollaborativeTask) -> Dict[str, Any]:
        """Execute task with agents working in parallel"""
        
        # All agents work on the same input simultaneously
        input_data = {"task": task.description}
        
        # Start all agents simultaneously
        agent_tasks = []
        for agent_id in task.assigned_agents:
            self.logger.info(f"Agent {agent_id} starting parallel work")
            agent_tasks.append(self._simulate_agent_work(agent_id, input_data, task))
        
        # Wait for all to complete
        results = await asyncio.gather(*agent_tasks, return_exceptions=True)
        
        # Combine results
        combined_results = []
        for i, agent_id in enumerate(task.assigned_agents):
            combined_results.append({"agent": agent_id, "result": results[i]})
        
        return {
            "mode": "parallel",
            "results": combined_results,
            "combined_output": self._combine_parallel_results(combined_results)
        }
    
    async def _execute_pipeline(self, task: CollaborativeTask) -> Dict[str, Any]:
        """Execute task as a pipeline where each agent processes the previous agent's output"""
        
        current_data = {"task": task.description}
        pipeline_results = []
        
        for agent_id in task.assigned_agents:
            self.logger.info(f"Agent {agent_id} processing pipeline stage")
            
            # Agent processes current data and produces output for next stage
            stage_result = await self._simulate_agent_work(agent_id, current_data, task)
            pipeline_results.append({"agent": agent_id, "input": current_data, "output": stage_result})
            
            # Output becomes input for next stage
            current_data = {"previous_stage": stage_result, "original_task": task.description}
        
        return {
            "mode": "pipeline",
            "stages": pipeline_results,
            "final_output": pipeline_results[-1]["output"] if pipeline_results else None
        }
    
    async def _execute_consensus(self, task: CollaborativeTask) -> Dict[str, Any]:
        """Execute task where agents collaborate to reach consensus"""
        
        input_data = {"task": task.description}
        consensus_rounds = []
        
        # Round 1: Initial proposals
        initial_proposals = []
        for agent_id in task.assigned_agents:
            proposal = await self._simulate_agent_work(agent_id, input_data, task)
            initial_proposals.append({"agent": agent_id, "proposal": proposal})
        
        consensus_rounds.append({"round": 1, "type": "initial_proposals", "data": initial_proposals})
        
        # Round 2: Review and refine (agents see each other's proposals)
        review_input = {
            "task": task.description,
            "other_proposals": [p["proposal"] for p in initial_proposals]
        }
        
        refined_proposals = []
        for agent_id in task.assigned_agents:
            refinement = await self._simulate_agent_work(agent_id, review_input, task)
            refined_proposals.append({"agent": agent_id, "refinement": refinement})
        
        consensus_rounds.append({"round": 2, "type": "refinements", "data": refined_proposals})
        
        # Round 3: Final consensus
        consensus_result = self._build_consensus(initial_proposals, refined_proposals)
        
        return {
            "mode": "consensus",
            "rounds": consensus_rounds,
            "consensus": consensus_result
        }
    
    async def _execute_competitive(self, task: CollaborativeTask) -> Dict[str, Any]:
        """Execute task where agents compete for the best solution"""
        
        input_data = {"task": task.description}
        
        # All agents work on the same problem
        solutions = []
        for agent_id in task.assigned_agents:
            solution = await self._simulate_agent_work(agent_id, input_data, task)
            solutions.append({"agent": agent_id, "solution": solution})
        
        # Evaluate and rank solutions
        ranked_solutions = self._rank_solutions(solutions, task)
        
        return {
            "mode": "competitive",
            "all_solutions": solutions,
            "ranked_solutions": ranked_solutions,
            "winner": ranked_solutions[0] if ranked_solutions else None
        }
    
    async def _simulate_agent_work(self, agent_id: str, input_data: Dict, task: CollaborativeTask) -> str:
        """Simulate agent work (in real implementation, this would call actual agents)"""
        
        # Get agent capability
        capability = self.agent_capabilities.get(agent_id, AgentCapability("unknown", 0.5, 0, 0.5, 0, []))
        
        # Simulate different quality based on proficiency
        if capability.proficiency > 0.8:
            quality = "excellent"
        elif capability.proficiency > 0.6:
            quality = "good"
        elif capability.proficiency > 0.4:
            quality = "adequate"
        else:
            quality = "basic"
        
        # Simulate work time based on proficiency
        work_time = 1.0 / max(capability.proficiency, 0.1)
        await asyncio.sleep(min(work_time, 2.0))  # Cap simulation time
        
        return f"{agent_id} produced {quality} work for: {input_data.get('task', 'unknown task')[:50]}..."
    
    def _combine_parallel_results(self, results: List[Dict]) -> str:
        """Combine results from parallel execution"""
        combined = "Combined parallel results:\n"
        for result in results:
            combined += f"- {result['agent']}: {result['result']}\n"
        return combined
    
    def _build_consensus(self, initial_proposals: List[Dict], refinements: List[Dict]) -> str:
        """Build consensus from proposals and refinements"""
        consensus = "Consensus reached incorporating:\n"
        for proposal in initial_proposals:
            consensus += f"- {proposal['agent']}: {proposal['proposal'][:50]}...\n"
        consensus += "Refined with collaborative input."
        return consensus
    
    def _rank_solutions(self, solutions: List[Dict], task: CollaborativeTask) -> List[Dict]:
        """Rank solutions based on agent proficiency and other factors"""
        
        def solution_score(solution):
            agent_id = solution["agent"]
            capability = self.agent_capabilities.get(agent_id, AgentCapability("", 0.5, 0, 0.5, 0, []))
            
            # Base score from agent proficiency
            score = capability.proficiency * 100
            
            # Bonus for relevant specializations
            task_keywords = set(task.description.lower().split())
            agent_specializations = set(spec.lower() for spec in capability.specializations)
            relevance_bonus = len(task_keywords.intersection(agent_specializations)) * 10
            
            return score + relevance_bonus
        
        return sorted(solutions, key=solution_score, reverse=True)
    
    async def _record_collaboration_success(self, task: CollaborativeTask):
        """Record successful collaboration for learning"""
        
        collaboration_record = {
            "task_id": task.id,
            "description": task.description,
            "mode": task.collaboration_mode.value,
            "agents": list(task.assigned_agents),
            "duration": (task.completed_at - task.started_at).total_seconds() if task.completed_at and task.started_at else 0,
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
        self.collaboration_history.append(collaboration_record)
        self.logger.info(f"Recorded successful collaboration for task {task.id}")
    
    async def get_coordination_analytics(self) -> Dict[str, Any]:
        """Get analytics about coordination performance"""
        
        if not self.collaboration_history:
            return {"message": "No collaboration history available"}
        
        # Calculate metrics
        total_collaborations = len(self.collaboration_history)
        successful_collaborations = sum(1 for c in self.collaboration_history if c["success"])
        success_rate = successful_collaborations / total_collaborations
        
        # Mode effectiveness
        mode_stats = {}
        for record in self.collaboration_history:
            mode = record["mode"]
            if mode not in mode_stats:
                mode_stats[mode] = {"count": 0, "success": 0, "avg_duration": 0}
            mode_stats[mode]["count"] += 1
            if record["success"]:
                mode_stats[mode]["success"] += 1
            mode_stats[mode]["avg_duration"] += record["duration"]
        
        for mode in mode_stats:
            stats = mode_stats[mode]
            stats["success_rate"] = stats["success"] / stats["count"]
            stats["avg_duration"] /= stats["count"]
        
        # Agent collaboration frequency
        agent_collaboration_count = {}
        for record in self.collaboration_history:
            for agent in record["agents"]:
                agent_collaboration_count[agent] = agent_collaboration_count.get(agent, 0) + 1
        
        return {
            "total_collaborations": total_collaborations,
            "success_rate": success_rate,
            "mode_effectiveness": mode_stats,
            "agent_collaboration_frequency": agent_collaboration_count,
            "most_effective_mode": max(mode_stats.keys(), key=lambda m: mode_stats[m]["success_rate"]) if mode_stats else None
        }

async def test_advanced_coordination():
    """Test the advanced coordination system"""
    print("Testing Advanced Agent Coordination System...")
    
    # Mock intelligence systems
    class MockModelIntelligence:
        pass
    
    class MockAgentIntelligence:
        def get_agent_expertise_summary(self, role):
            return {
                "experience_count": 10,
                "average_success_rate": 0.85,
                "specializations": {"coding": 5, "testing": 3}
            }
    
    # Initialize coordinator
    coordinator = AdvancedAgentCoordinator(MockModelIntelligence(), MockAgentIntelligence())
    
    # Register agents
    await coordinator.register_agent_capabilities("architect_001", "architect")
    await coordinator.register_agent_capabilities("developer_001", "developer")
    await coordinator.register_agent_capabilities("tester_001", "tester")
    
    # Test different collaboration modes
    
    # 1. Sequential task
    task_id_1 = await coordinator.create_collaborative_task(
        description="Design and implement user authentication system",
        collaboration_mode=CollaborationMode.SEQUENTIAL,
        required_agents=["architect_001", "developer_001", "tester_001"],
        priority=8
    )
    
    # 2. Parallel task
    task_id_2 = await coordinator.create_collaborative_task(
        description="Research and analyze performance optimization options",
        collaboration_mode=CollaborationMode.PARALLEL,
        required_agents=["developer_001", "architect_001"],
        priority=6
    )
    
    # 3. Consensus task
    task_id_3 = await coordinator.create_collaborative_task(
        description="Decide on technology stack for new project",
        collaboration_mode=CollaborationMode.CONSENSUS,
        required_agents=["architect_001", "developer_001"],
        optional_agents=["tester_001"],
        priority=9
    )
    
    print(f"✓ Created 3 collaborative tasks")
    
    # Execute tasks
    for task_id in [task_id_1, task_id_2, task_id_3]:
        await coordinator.assign_optimal_agents(task_id)
        result = await coordinator.execute_collaborative_task(task_id)
        task = coordinator.active_tasks[task_id]
        print(f"✓ Executed {task.collaboration_mode.value} task: {task.description[:50]}...")
    
    # Get analytics
    analytics = await coordinator.get_coordination_analytics()
    print(f"✓ Coordination analytics:")
    print(f"  Success rate: {analytics['success_rate']:.1%}")
    print(f"  Most effective mode: {analytics.get('most_effective_mode', 'N/A')}")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_advanced_coordination())
    exit(0 if result else 1)
