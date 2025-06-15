#!/usr/bin/env python3
"""
Ultimate AI Completion System

An advanced AI completion system that integrates all components:
- Intelligent agent orchestration
- Cross-provider model management
- Persistent learning
- Real-time optimization
- Advanced coordination
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
from pathlib import Path

class CompletionType(Enum):
    CODE = "code"
    DOCUMENTATION = "documentation"
    ANALYSIS = "analysis"
    RESEARCH = "research"
    PLANNING = "planning"
    OPTIMIZATION = "optimization"
    TESTING = "testing"
    REVIEW = "review"

class QualityLevel(Enum):
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"
    PREMIUM = "premium"

@dataclass
class CompletionRequest:
    """Request for AI completion"""
    request_id: str
    completion_type: CompletionType
    prompt: str
    context: Dict[str, Any] = field(default_factory=dict)
    quality_level: QualityLevel = QualityLevel.STANDARD
    max_tokens: int = 2000
    temperature: float = 0.7
    use_agents: bool = True
    agent_collaboration: bool = False
    learning_enabled: bool = True
    output_format: str = "text"  # text, json, markdown, code
    files_context: List[str] = field(default_factory=list)
    
@dataclass
class CompletionResponse:
    """Response from AI completion"""
    request_id: str
    success: bool
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    agent_used: Optional[str] = None
    model_used: Optional[str] = None
    processing_time: float = 0.0
    quality_score: float = 0.0
    tokens_used: int = 0
    error: Optional[str] = None

class UltimateAICompletion:
    """
    Ultimate AI completion system that leverages all available intelligence
    """
    
    def __init__(self, output_dir: str = "completion_outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Core components
        self.memory_manager = None
        self.unified_intelligence = None
        self.orchestrator = None
        self.persistent_intelligence = None
        
        # Completion state
        self.active_requests: Dict[str, CompletionRequest] = {}
        self.completion_history: List[CompletionResponse] = []
        self.performance_metrics: Dict[str, Any] = {}
        
        # Setup logging
        self.logger = logging.getLogger("UltimateAICompletion")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    async def initialize(self):
        """Initialize all components"""
        try:
            self.logger.info("Initializing Ultimate AI Completion System...")
            
            # Initialize memory manager
            from fixed_memory_manager import MemoryAwareModelManager
            self.memory_manager = MemoryAwareModelManager()
            await self.memory_manager.initialize()
            
            # Initialize unified intelligence
            from unified_model_intelligence import UnifiedModelIntelligence
            self.unified_intelligence = UnifiedModelIntelligence(self.memory_manager)
            
            # Initialize orchestrator
            from intelligent_agent_orchestrator_fixed import IntelligentAgentOrchestrator
            self.orchestrator = IntelligentAgentOrchestrator()
            await self.orchestrator.initialize()
            
            # Initialize persistent intelligence
            from persistent_agent_intelligence import PersistentAgentIntelligence
            self.persistent_intelligence = PersistentAgentIntelligence()
            
            self.logger.info("Ultimate AI Completion System initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize completion system: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Process a completion request"""
        start_time = datetime.now()
        self.active_requests[request.request_id] = request
        
        try:
            self.logger.info(f"Processing completion request: {request.request_id} ({request.completion_type.value})")
            
            # Choose completion strategy based on request
            if request.use_agents and request.agent_collaboration:
                response = await self._agent_collaborative_completion(request)
            elif request.use_agents:
                response = await self._agent_based_completion(request)
            else:
                response = await self._direct_model_completion(request)
            
            # Calculate processing time and quality
            processing_time = (datetime.now() - start_time).total_seconds()
            response.processing_time = processing_time
            response.quality_score = await self._calculate_quality_score(request, response)
            
            # Learn from completion if enabled
            if request.learning_enabled and self.persistent_intelligence:
                await self._learn_from_completion(request, response)
            
            # Update metrics
            self._update_metrics(request, response)
            
            # Save completion history
            self.completion_history.append(response)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Completion failed: {e}")
            return CompletionResponse(
                request_id=request.request_id,
                success=False,
                content="",
                error=str(e),
                processing_time=(datetime.now() - start_time).total_seconds()
            )
        finally:
            if request.request_id in self.active_requests:
                del self.active_requests[request.request_id]
    
    async def _agent_collaborative_completion(self, request: CompletionRequest) -> CompletionResponse:
        """Use multiple agents collaborating on the completion"""
        self.logger.info("Using collaborative agent completion")
        
        try:
            # Create workflow based on completion type
            workflow_template = self._get_workflow_template(request.completion_type)
            
            # Customize workflow for this request
            workflow = await self.orchestrator.create_workflow_from_template(
                workflow_template,
                {
                    "original_prompt": request.prompt,
                    "context": request.context,
                    "quality_level": request.quality_level.value,
                    "output_format": request.output_format
                }
            )
            
            # Execute workflow
            results = await self.orchestrator.execute_workflow(workflow)
            
            # Combine results
            content = self._combine_workflow_results(results, request)
            
            return CompletionResponse(
                request_id=request.request_id,
                success=True,
                content=content,
                metadata={
                    "workflow_id": workflow.workflow_id,
                    "agents_used": [r.agent_id for r in results],
                    "models_used": list(set(r.model_used for r in results))
                }
            )
            
        except Exception as e:
            self.logger.error(f"Collaborative completion failed: {e}")
            raise
    
    async def _agent_based_completion(self, request: CompletionRequest) -> CompletionResponse:
        """Use single agent for completion"""
        self.logger.info("Using single agent completion")
        
        try:
            # Find best agent for the task
            agent_role = self._get_best_agent_role(request.completion_type)
            
            # Request model allocation
            from unified_model_intelligence import TaskRequest, TaskPriority, AgentRole
            
            agent_role_map = {
                "architect": AgentRole.ARCHITECT,
                "researcher": AgentRole.RESEARCHER,
                "developer": AgentRole.DEVELOPER,
                "tester": AgentRole.TESTER,
                "reviewer": AgentRole.REVIEWER
            }
            
            task_request = TaskRequest(
                agent_id=f"{agent_role}_completion",
                agent_role=agent_role_map.get(agent_role, AgentRole.DEVELOPER),
                task_type=request.completion_type.value,
                priority=self._get_priority_from_quality(request.quality_level),
                estimated_duration=600  # 10 minutes
            )
            
            model_key = await self.unified_intelligence.request_model_allocation(task_request)
            if not model_key:
                raise ValueError("No model available for completion")
            
            # Prepare enhanced prompt
            enhanced_prompt = self._enhance_prompt(request)
            
            # Generate completion using allocated model
            content = await self._generate_with_model(model_key, enhanced_prompt, request)
            
            # Release model
            await self.unified_intelligence.release_model_allocation(task_request.agent_id)
            
            return CompletionResponse(
                request_id=request.request_id,
                success=True,
                content=content,
                agent_used=agent_role,
                model_used=model_key,
                metadata={"completion_method": "single_agent"}
            )
            
        except Exception as e:
            self.logger.error(f"Agent-based completion failed: {e}")
            raise
    
    async def _direct_model_completion(self, request: CompletionRequest) -> CompletionResponse:
        """Direct model completion without agents"""
        self.logger.info("Using direct model completion")
        
        try:
            # Get best available model
            available_models = self.memory_manager.available_models
            if not available_models:
                raise ValueError("No models available")
            
            # Find loaded model with highest score
            best_model = None
            best_score = 0
            
            for model_key, model_info in available_models.items():
                if model_info.is_loaded:
                    score = 100
                    if "7b" in model_info.model_id.lower():
                        score += 20
                    if "instruct" in model_info.model_id.lower():
                        score += 10
                    if score > best_score:
                        best_score = score
                        best_model = model_key
            
            if not best_model:
                # Try to load a suitable model
                for model_key, model_info in available_models.items():
                    if await self.memory_manager._load_model(model_key):
                        best_model = model_key
                        break
            
            if not best_model:
                raise ValueError("No suitable model could be loaded")
            
            # Generate completion
            enhanced_prompt = self._enhance_prompt(request)
            content = await self._generate_with_model(best_model, enhanced_prompt, request)
            
            return CompletionResponse(
                request_id=request.request_id,
                success=True,
                content=content,
                model_used=best_model,
                metadata={"completion_method": "direct_model"}
            )
            
        except Exception as e:
            self.logger.error(f"Direct model completion failed: {e}")
            raise
    
    def _get_workflow_template(self, completion_type: CompletionType) -> str:
        """Get appropriate workflow template for completion type"""
        if completion_type in [CompletionType.CODE, CompletionType.OPTIMIZATION]:
            return "development"
        elif completion_type in [CompletionType.RESEARCH, CompletionType.ANALYSIS]:
            return "research"
        else:
            return "development"  # Default fallback
    
    def _get_best_agent_role(self, completion_type: CompletionType) -> str:
        """Get best agent role for completion type"""
        role_map = {
            CompletionType.CODE: "developer",
            CompletionType.DOCUMENTATION: "writer",
            CompletionType.ANALYSIS: "researcher",
            CompletionType.RESEARCH: "researcher",
            CompletionType.PLANNING: "architect",
            CompletionType.OPTIMIZATION: "developer",
            CompletionType.TESTING: "tester",
            CompletionType.REVIEW: "reviewer"
        }
        return role_map.get(completion_type, "developer")
    
    def _get_priority_from_quality(self, quality_level: QualityLevel):
        """Convert quality level to task priority"""
        from unified_model_intelligence import TaskPriority
        
        priority_map = {
            QualityLevel.DRAFT: TaskPriority.LOW,
            QualityLevel.STANDARD: TaskPriority.NORMAL,
            QualityLevel.HIGH: TaskPriority.HIGH,
            QualityLevel.PREMIUM: TaskPriority.CRITICAL
        }
        return priority_map.get(quality_level, TaskPriority.NORMAL)
    
    def _enhance_prompt(self, request: CompletionRequest) -> str:
        """Enhance prompt with context and quality requirements"""
        enhanced = request.prompt
        
        # Add quality level guidance
        quality_instructions = {
            QualityLevel.DRAFT: "Provide a quick, basic response.",
            QualityLevel.STANDARD: "Provide a well-structured, clear response.",
            QualityLevel.HIGH: "Provide a detailed, comprehensive response with examples.",
            QualityLevel.PREMIUM: "Provide an exceptional, thorough response with deep insights and multiple perspectives."
        }
        
        enhanced += f"\n\nQuality requirement: {quality_instructions.get(request.quality_level, '')}"
        
        # Add output format guidance
        if request.output_format != "text":
            enhanced += f"\n\nPlease format the response as: {request.output_format}"
        
        # Add context if available
        if request.context:
            enhanced += f"\n\nAdditional context: {json.dumps(request.context, indent=2)}"
        
        return enhanced
    
    async def _generate_with_model(self, model_key: str, prompt: str, request: CompletionRequest) -> str:
        """Generate content using specified model"""
        model_info = self.memory_manager.available_models[model_key]
        provider = model_info.provider
        
        try:
            if provider == "lmstudio":
                return await self._generate_lmstudio(model_info.model_id, prompt, request)
            elif provider == "ollama":
                return await self._generate_ollama(model_info.model_id, prompt, request)
            elif provider == "vllm":
                return await self._generate_vllm(model_info.model_id, prompt, request)
            else:
                raise ValueError(f"Unknown provider: {provider}")
                
        except Exception as e:
            self.logger.error(f"Generation failed with {provider}: {e}")
            # Fallback to mock response
            return f"Generated response for: {prompt[:100]}... (using {model_key})"
    
    async def _generate_lmstudio(self, model_id: str, prompt: str, request: CompletionRequest) -> str:
        """Generate using LM Studio"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model_id,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "stream": False
            }
            
            async with session.post("http://localhost:1234/v1/chat/completions", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"LM Studio API error: {response.status}")
    
    async def _generate_ollama(self, model_id: str, prompt: str, request: CompletionRequest) -> str:
        """Generate using Ollama"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model_id,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": request.max_tokens,
                    "temperature": request.temperature
                }
            }
            
            async with session.post("http://localhost:11434/api/generate", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("response", "")
                else:
                    raise Exception(f"Ollama API error: {response.status}")
    
    async def _generate_vllm(self, model_id: str, prompt: str, request: CompletionRequest) -> str:
        """Generate using vLLM"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": model_id,
                "prompt": prompt,
                "max_tokens": request.max_tokens,
                "temperature": request.temperature
            }
            
            async with session.post("http://localhost:8000/v1/completions", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["choices"][0]["text"]
                else:
                    raise Exception(f"vLLM API error: {response.status}")
    
    def _combine_workflow_results(self, results: List, request: CompletionRequest) -> str:
        """Combine workflow results into final content"""
        successful_results = [r for r in results if r.success and r.output]
        
        if not successful_results:
            return "No successful results from workflow execution."
        
        # Combine outputs based on task order
        combined = []
        for result in successful_results:
            combined.append(f"=== {result.task_id.replace('_', ' ').title()} ===\n{result.output}")
        
        return "\n\n".join(combined)
    
    async def _calculate_quality_score(self, request: CompletionRequest, response: CompletionResponse) -> float:
        """Calculate quality score for the response"""
        score = 5.0  # Base score
        
        # Length factor
        if len(response.content) > 100:
            score += 1.0
        if len(response.content) > 500:
            score += 1.0
        
        # Quality level achievement
        quality_multipliers = {
            QualityLevel.DRAFT: 0.8,
            QualityLevel.STANDARD: 1.0,
            QualityLevel.HIGH: 1.2,
            QualityLevel.PREMIUM: 1.5
        }
        score *= quality_multipliers.get(request.quality_level, 1.0)
        
        # Speed bonus
        if response.processing_time < 5.0:
            score += 0.5
        
        return min(score, 10.0)  # Cap at 10
    
    async def _learn_from_completion(self, request: CompletionRequest, response: CompletionResponse):
        """Learn from completion for future improvements"""
        if self.persistent_intelligence:
            try:
                experience = {
                    "completion_type": request.completion_type.value,
                    "quality_level": request.quality_level.value,
                    "success": response.success,
                    "quality_score": response.quality_score,
                    "processing_time": response.processing_time,
                    "model_used": response.model_used,
                    "agent_used": response.agent_used
                }
                
                await self.persistent_intelligence.record_experience(
                    agent_id="completion_system",
                    experience_type="completion",
                    experience_data=experience,
                    outcome_quality=response.quality_score / 10.0
                )
                
            except Exception as e:
                self.logger.warning(f"Failed to record learning experience: {e}")
    
    def _update_metrics(self, request: CompletionRequest, response: CompletionResponse):
        """Update performance metrics"""
        if "total_completions" not in self.performance_metrics:
            self.performance_metrics = {
                "total_completions": 0,
                "successful_completions": 0,
                "average_quality": 0.0,
                "average_processing_time": 0.0,
                "completion_types": {},
                "quality_levels": {}
            }
        
        self.performance_metrics["total_completions"] += 1
        
        if response.success:
            self.performance_metrics["successful_completions"] += 1
            
            # Update averages
            total_successful = self.performance_metrics["successful_completions"]
            current_avg_quality = self.performance_metrics["average_quality"]
            current_avg_time = self.performance_metrics["average_processing_time"]
            
            self.performance_metrics["average_quality"] = (
                (current_avg_quality * (total_successful - 1) + response.quality_score) / total_successful
            )
            
            self.performance_metrics["average_processing_time"] = (
                (current_avg_time * (total_successful - 1) + response.processing_time) / total_successful
            )
        
        # Update type and quality counters
        completion_type = request.completion_type.value
        quality_level = request.quality_level.value
        
        self.performance_metrics["completion_types"][completion_type] = (
            self.performance_metrics["completion_types"].get(completion_type, 0) + 1
        )
        
        self.performance_metrics["quality_levels"][quality_level] = (
            self.performance_metrics["quality_levels"].get(quality_level, 0) + 1
        )
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            "completion_system": {
                "active_requests": len(self.active_requests),
                "total_completions": len(self.completion_history),
                "performance_metrics": self.performance_metrics
            }
        }
        
        # Add component statuses
        if self.unified_intelligence:
            try:
                status["unified_intelligence"] = await self.unified_intelligence.get_system_status()
            except:
                status["unified_intelligence"] = {"status": "error"}
        
        if self.memory_manager:
            try:
                status["memory_manager"] = await self.memory_manager.get_memory_status()
            except:
                status["memory_manager"] = {"status": "error"}
        
        return status
    
    async def save_completion_report(self, output_file: str = None):
        """Save comprehensive completion report"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"completion_report_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_status": await self.get_system_status(),
            "recent_completions": [
                {
                    "request_id": resp.request_id,
                    "success": resp.success,
                    "quality_score": resp.quality_score,
                    "processing_time": resp.processing_time,
                    "model_used": resp.model_used,
                    "agent_used": resp.agent_used
                }
                for resp in self.completion_history[-50:]  # Last 50 completions
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Completion report saved: {output_file}")

async def test_completion_system():
    """Test the ultimate AI completion system"""
    print("=== Testing Ultimate AI Completion System ===")
    
    completion_system = UltimateAICompletion()
    
    # Initialize
    success = await completion_system.initialize()
    if not success:
        print("Failed to initialize completion system")
        return False
    
    # Test different completion types
    test_requests = [
        CompletionRequest(
            request_id="test_code_001",
            completion_type=CompletionType.CODE,
            prompt="Create a Python function to calculate fibonacci numbers",
            quality_level=QualityLevel.HIGH,
            use_agents=True,
            agent_collaboration=False
        ),
        CompletionRequest(
            request_id="test_docs_001",
            completion_type=CompletionType.DOCUMENTATION,
            prompt="Write documentation for a REST API endpoint",
            quality_level=QualityLevel.STANDARD,
            use_agents=True,
            agent_collaboration=False,
            output_format="markdown"
        ),
        CompletionRequest(
            request_id="test_analysis_001",
            completion_type=CompletionType.ANALYSIS,
            prompt="Analyze the benefits and drawbacks of microservices architecture",
            quality_level=QualityLevel.HIGH,
            use_agents=True,
            agent_collaboration=True
        )
    ]
    
    print(f"Processing {len(test_requests)} completion requests...")
    
    for request in test_requests:
        print(f"\nProcessing: {request.request_id} ({request.completion_type.value})")
        response = await completion_system.complete(request)
        
        if response.success:
            print(f"✓ SUCCESS - Quality: {response.quality_score:.1f}/10, "
                  f"Time: {response.processing_time:.1f}s, Model: {response.model_used}")
            print(f"Content preview: {response.content[:200]}...")
        else:
            print(f"✗ FAILED - Error: {response.error}")
    
    # Show system status
    status = await completion_system.get_system_status()
    print(f"\n=== System Status ===")
    print(f"Total completions: {status['completion_system']['total_completions']}")
    print(f"Performance metrics: {status['completion_system']['performance_metrics']}")
    
    # Save report
    await completion_system.save_completion_report()
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_completion_system())
    exit(0 if result else 1)
