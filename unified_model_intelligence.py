#!/usr/bin/env python3
"""
Unified Cross-Provider Model Intelligence System

This is the core orchestration system that manages model allocation across
LM Studio, Ollama, and vLLM providers with autonomous decision making.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class AgentRole(Enum):
    ARCHITECT = "architect"
    RESEARCHER = "researcher"
    DEVELOPER = "developer"
    TESTER = "tester"
    REVIEWER = "reviewer"
    COORDINATOR = "coordinator"

@dataclass
class TaskRequest:
    """A task request from an agent"""
    agent_id: str
    agent_role: AgentRole
    task_type: str
    priority: TaskPriority
    estimated_duration: int  # seconds
    preferred_providers: List[str] = field(default_factory=lambda: ["lmstudio", "ollama", "vllm"])
    required_capabilities: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ModelAllocation:
    """Model allocation for an agent"""
    agent_id: str
    model_key: str
    provider: str
    allocated_at: datetime
    expires_at: datetime
    task_type: str
    priority: TaskPriority

class UnifiedModelIntelligence:
    """
    Unified intelligence system that coordinates model usage across all providers
    and agents with autonomous decision making
    """
    
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager
        self.active_allocations: Dict[str, ModelAllocation] = {}
        self.task_queue: List[TaskRequest] = []
        self.agent_preferences: Dict[str, Dict] = {}
        
        # Setup logging
        self.logger = logging.getLogger("UnifiedModelIntelligence")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Load agent preferences
        self._load_agent_preferences()
    
    def _load_agent_preferences(self):
        """Load agent preferences for model selection"""
        self.agent_preferences = {
            AgentRole.ARCHITECT.value: {
                "preferred_model_sizes": ["7b", "8b", "13b"],
                "task_types": ["planning", "analysis", "design"],
                "provider_preference": ["lmstudio", "vllm", "ollama"]
            },
            AgentRole.RESEARCHER.value: {
                "preferred_model_sizes": ["7b", "8b", "13b", "22b"],
                "task_types": ["research", "analysis", "summarization"],
                "provider_preference": ["vllm", "lmstudio", "ollama"]
            },
            AgentRole.DEVELOPER.value: {
                "preferred_model_sizes": ["7b", "8b"],
                "task_types": ["coding", "debugging", "implementation"],
                "provider_preference": ["lmstudio", "ollama", "vllm"]
            },
            AgentRole.TESTER.value: {
                "preferred_model_sizes": ["3b", "7b"],
                "task_types": ["testing", "validation", "qa"],
                "provider_preference": ["ollama", "lmstudio", "vllm"]
            },
            AgentRole.REVIEWER.value: {
                "preferred_model_sizes": ["7b", "8b", "13b"],
                "task_types": ["review", "evaluation", "critique"],
                "provider_preference": ["vllm", "lmstudio", "ollama"]
            }
        }
    
    async def request_model_allocation(self, task_request: TaskRequest) -> Optional[str]:
        """
        Request model allocation for an agent task
        Returns model_key if successful, None if no suitable model available
        """
        self.logger.info(f"Processing model request for agent {task_request.agent_id} ({task_request.agent_role.value})")
        
        # Add to task queue
        self.task_queue.append(task_request)
        
        # Process allocation
        allocation = await self._process_allocation_request(task_request)
        
        if allocation:
            self.active_allocations[task_request.agent_id] = allocation
            self.logger.info(f"Allocated {allocation.model_key} to agent {task_request.agent_id}")
            return allocation.model_key
        else:
            self.logger.warning(f"No suitable model available for agent {task_request.agent_id}")
            return None
    
    async def _process_allocation_request(self, task_request: TaskRequest) -> Optional[ModelAllocation]:
        """Process allocation request with intelligent decision making"""
        
        # Get current system state
        memory_status = await self.memory_manager.get_memory_status()
        available_models = self.memory_manager.available_models
        
        # Find candidate models
        candidates = await self._find_candidate_models(task_request, available_models)
        
        if not candidates:
            self.logger.warning("No candidate models found")
            return None
        
        # Score and rank candidates
        scored_candidates = await self._score_model_candidates(task_request, candidates)
        
        # Check if we need to free up VRAM or negotiate with other agents
        best_candidate = scored_candidates[0] if scored_candidates else None
        
        if best_candidate:
            model_info = available_models[best_candidate['model_key']]
            
            # Check if model is already loaded
            if model_info.is_loaded:
                return self._create_allocation(task_request, best_candidate['model_key'])
            
            # Check if we can load the model
            can_load = await self._can_load_model_safely(model_info)
            
            if can_load:
                # Load the model
                success = await self.memory_manager._load_model(best_candidate['model_key'])
                if success:
                    return self._create_allocation(task_request, best_candidate['model_key'])
            else:
                # Try to negotiate with other agents
                negotiated_model = await self._negotiate_model_access(task_request, scored_candidates)
                if negotiated_model:
                    return self._create_allocation(task_request, negotiated_model)
        
        return None
    
    async def _find_candidate_models(self, task_request: TaskRequest, available_models: Dict) -> List[str]:
        """Find candidate models for the task"""
        candidates = []
        agent_prefs = self.agent_preferences.get(task_request.agent_role.value, {})
        
        for model_key, model_info in available_models.items():
            # Check provider preference
            if model_info.provider not in task_request.preferred_providers:
                continue
                
            # Check if model is suitable for task
            if self._is_model_suitable_for_task(model_info, task_request, agent_prefs):
                candidates.append(model_key)
        
        return candidates
    
    def _is_model_suitable_for_task(self, model_info, task_request: TaskRequest, agent_prefs: Dict) -> bool:
        """Check if model is suitable for the task"""
        model_name = model_info.model_id.lower()
        
        # Check preferred model sizes
        preferred_sizes = agent_prefs.get("preferred_model_sizes", [])
        if preferred_sizes:
            model_matches_size = any(size in model_name for size in preferred_sizes)
            if not model_matches_size:
                return False
        
        # Check task type compatibility
        task_types = agent_prefs.get("task_types", [])
        if task_types and task_request.task_type not in task_types:
            # Allow if it's a general purpose model
            if not any(keyword in model_name for keyword in ["chat", "instruct", "general"]):
                return False
        
        return True
    
    async def _score_model_candidates(self, task_request: TaskRequest, candidates: List[str]) -> List[Dict]:
        """Score and rank model candidates"""
        scored_candidates = []
        agent_prefs = self.agent_preferences.get(task_request.agent_role.value, {})
        
        for model_key in candidates:
            model_info = self.memory_manager.available_models[model_key]
            score = self._calculate_model_score(model_info, task_request, agent_prefs)
            
            scored_candidates.append({
                'model_key': model_key,
                'score': score,
                'provider': model_info.provider,
                'is_loaded': model_info.is_loaded
            })
        
        # Sort by score (higher is better)
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates
    
    def _calculate_model_score(self, model_info, task_request: TaskRequest, agent_prefs: Dict) -> float:
        """Calculate score for a model candidate"""
        score = 0.0
        
        # Base score for being available
        score += 10.0
        
        # Bonus for already being loaded
        if model_info.is_loaded:
            score += 20.0
        
        # Provider preference bonus
        provider_prefs = agent_prefs.get("provider_preference", [])
        if provider_prefs:
            try:
                provider_index = provider_prefs.index(model_info.provider)
                score += (len(provider_prefs) - provider_index) * 5.0
            except ValueError:
                pass
        
        # Recent usage bonus
        if model_info.last_used and model_info.last_used > datetime.now() - timedelta(hours=1):
            score += 15.0
        
        # Priority adjustment
        priority_multiplier = {
            TaskPriority.LOW: 0.8,
            TaskPriority.NORMAL: 1.0,
            TaskPriority.HIGH: 1.2,
            TaskPriority.CRITICAL: 1.5
        }
        score *= priority_multiplier.get(task_request.priority, 1.0)
        
        return score
    
    async def _can_load_model_safely(self, model_info) -> bool:
        """Check if we can load a model without exceeding VRAM limits"""
        memory_status = await self.memory_manager.get_memory_status()
        
        available_vram = memory_status['max_vram_mb'] - memory_status['current_usage_mb']
        estimated_usage = model_info.estimated_vram_mb
        
        # Leave some safety margin
        safety_margin = 500  # MB
        return available_vram >= (estimated_usage + safety_margin)
    
    async def _negotiate_model_access(self, task_request: TaskRequest, candidates: List[Dict]) -> Optional[str]:
        """Negotiate model access with other agents"""
        self.logger.info(f"Negotiating model access for agent {task_request.agent_id}")
        
        # Check if we can unload lower priority models
        for allocation in list(self.active_allocations.values()):
            if allocation.priority.value < task_request.priority.value:
                # Check if this allocation is close to expiring
                time_remaining = (allocation.expires_at - datetime.now()).total_seconds()
                
                if time_remaining < 300:  # Less than 5 minutes
                    self.logger.info(f"Freeing up model {allocation.model_key} from lower priority agent {allocation.agent_id}")
                    await self.release_model_allocation(allocation.agent_id)
                    
                    # Try to load our preferred model
                    for candidate in candidates:
                        if await self._can_load_model_safely(self.memory_manager.available_models[candidate['model_key']]):
                            success = await self.memory_manager._load_model(candidate['model_key'])
                            if success:
                                return candidate['model_key']
        
        return None
    
    def _create_allocation(self, task_request: TaskRequest, model_key: str) -> ModelAllocation:
        """Create a model allocation"""
        duration = timedelta(seconds=task_request.estimated_duration)
        
        return ModelAllocation(
            agent_id=task_request.agent_id,
            model_key=model_key,
            provider=self.memory_manager.available_models[model_key].provider,
            allocated_at=datetime.now(),
            expires_at=datetime.now() + duration,
            task_type=task_request.task_type,
            priority=task_request.priority
        )
    
    async def release_model_allocation(self, agent_id: str) -> bool:
        """Release model allocation for an agent"""
        if agent_id in self.active_allocations:
            allocation = self.active_allocations[agent_id]
            self.logger.info(f"Releasing allocation for agent {agent_id} (model: {allocation.model_key})")
            del self.active_allocations[agent_id]
            return True
        return False
    
    async def extend_allocation(self, agent_id: str, additional_seconds: int) -> bool:
        """Extend model allocation for an agent"""
        if agent_id in self.active_allocations:
            allocation = self.active_allocations[agent_id]
            allocation.expires_at += timedelta(seconds=additional_seconds)
            self.logger.info(f"Extended allocation for agent {agent_id} by {additional_seconds} seconds")
            return True
        return False
    
    async def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        memory_status = await self.memory_manager.get_memory_status()
        
        # Count allocations by provider
        provider_allocations = {}
        for allocation in self.active_allocations.values():
            provider = allocation.provider
            provider_allocations[provider] = provider_allocations.get(provider, 0) + 1
        
        return {
            'memory_status': memory_status,
            'active_allocations': len(self.active_allocations),
            'queued_requests': len(self.task_queue),
            'allocations_by_provider': provider_allocations,
            'total_agents': len(set(alloc.agent_id for alloc in self.active_allocations.values()))
        }
    
    async def cleanup_expired_allocations(self):
        """Clean up expired allocations"""
        now = datetime.now()
        expired_agents = [
            agent_id for agent_id, allocation in self.active_allocations.items()
            if allocation.expires_at < now
        ]
        
        for agent_id in expired_agents:
            await self.release_model_allocation(agent_id)
            self.logger.info(f"Cleaned up expired allocation for agent {agent_id}")
    
    async def start_background_tasks(self):
        """Start background maintenance tasks"""
        while True:
            try:
                await self.cleanup_expired_allocations()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                self.logger.error(f"Error in background task: {e}")
                await asyncio.sleep(10)

async def test_unified_intelligence():
    """Test the unified intelligence system"""
    # Import here to avoid circular imports during development
    try:
        from fixed_memory_manager import MemoryAwareModelManager
        
        # Initialize components
        memory_manager = MemoryAwareModelManager()
        await memory_manager.initialize()
        
        unified_intelligence = UnifiedModelIntelligence(memory_manager)
        
        # Create test task requests
        test_requests = [
            TaskRequest(
                agent_id="architect_001",
                agent_role=AgentRole.ARCHITECT,
                task_type="planning",
                priority=TaskPriority.HIGH,
                estimated_duration=1800  # 30 minutes
            ),
            TaskRequest(
                agent_id="developer_001", 
                agent_role=AgentRole.DEVELOPER,
                task_type="coding",
                priority=TaskPriority.NORMAL,
                estimated_duration=3600  # 1 hour
            ),
            TaskRequest(
                agent_id="researcher_001",
                agent_role=AgentRole.RESEARCHER,
                task_type="research",
                priority=TaskPriority.HIGH,
                estimated_duration=2400  # 40 minutes
            )
        ]
        
        print("=== Testing Unified Model Intelligence ===")
        
        # Test allocations
        for request in test_requests:
            model_key = await unified_intelligence.request_model_allocation(request)
            if model_key:
                print(f"✓ Agent {request.agent_id} allocated model: {model_key}")
            else:
                print(f"✗ Failed to allocate model for agent {request.agent_id}")
        
        # Show system status
        status = await unified_intelligence.get_system_status()
        print(f"\n=== System Status ===")
        print(f"Active allocations: {status['active_allocations']}")
        print(f"Total agents: {status['total_agents']}")
        print(f"VRAM usage: {status['memory_status']['current_usage_mb']}MB / {status['memory_status']['max_vram_mb']}MB")
        print(f"Allocations by provider: {status['allocations_by_provider']}")
        
        return True
        
    except Exception as e:
        print(f"Error testing unified intelligence: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_unified_intelligence())
    exit(0 if result else 1)
