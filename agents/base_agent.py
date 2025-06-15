"""
Base Agent Class - Foundation for all AI agents with Persistent Intelligence
"""

import asyncio
import logging
import sys
import os
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from persistent_agent_intelligence import PersistentAgentIntelligence, ExperienceType

class BaseAgent(ABC):
    def __init__(self, agent_id: str, config: Dict, llm_manager, memory_manager, model_manager=None):
        self.agent_id = agent_id
        self.config = config
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        self.model_manager = model_manager  # Advanced model manager for intelligent model selection
        
        self.logger = logging.getLogger(f"Agent.{agent_id}")
        self.status = "initializing"
        self.current_task = None
        
        # Agent capabilities
        self.role = config.get('role', 'Generic Agent')
        self.model = config.get('model', 'default')
        self.capabilities = config.get('capabilities', [])
        
        # Persistent Intelligence Integration
        self.intelligence = PersistentAgentIntelligence()
        self.current_project_context = self._detect_project_context()
        self.task_start_time = None
        self.learning_enabled = config.get('learning_enabled', True)
    
    def _detect_project_context(self) -> Dict[str, Any]:
        """Detect current project context for intelligent learning"""
        context = {
            "workspace": os.getcwd(),
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        # Detect programming language
        common_files = {
            'package.json': 'javascript',
            'requirements.txt': 'python', 
            'Cargo.toml': 'rust',
            'pom.xml': 'java',
            'composer.json': 'php',
            'Gemfile': 'ruby'
        }
        
        for file, lang in common_files.items():
            if os.path.exists(file):
                context['language'] = lang
                break
        
        # Detect framework/library
        if context.get('language') == 'python':
            if os.path.exists('manage.py'):
                context['framework'] = 'django'
            elif 'fastapi' in str(Path('.').glob('**/*.py')):
                context['framework'] = 'fastapi'
            elif 'flask' in str(Path('.').glob('**/*.py')):
                context['framework'] = 'flask'
        
        if context.get('language') == 'javascript':
            try:
                with open('package.json', 'r') as f:
                    import json
                    pkg = json.load(f)
                    deps = pkg.get('dependencies', {})
                    if 'react' in deps:
                        context['framework'] = 'react'
                    elif 'vue' in deps:
                        context['framework'] = 'vue'
                    elif 'express' in deps:
                        context['framework'] = 'express'
            except:
                pass
        
        return context
    
    async def get_best_model_for_task(self, task_type: str = "general") -> str:
        """Get the best available model for the current task"""
        if self.model_manager:
            try:
                best_model = await self.model_manager.get_best_model_for_task(task_type, self.role)
                if best_model:
                    self.logger.debug(f"Selected model {best_model} for {task_type}")
                    return best_model
            except Exception as e:
                self.logger.warning(f"Model selection failed: {e}")
        
        # Fallback to configured model
        return self.model
    
    async def initialize(self):
        """Initialize the agent"""
        self.logger.info(f"Initializing {self.agent_id} agent...")
        
        # Load agent-specific configuration
        await self.load_configuration()
        
        # Initialize agent memory
        await self.initialize_memory()
        
        # Perform agent-specific initialization
        await self.agent_initialize()
        
        self.status = "ready"
        self.logger.info(f"Agent {self.agent_id} initialized successfully")
    
    async def execute_task(self, task: Dict) -> Dict:
        """Execute a task"""
        self.logger.info(f"Executing task: {task.get('title', task.get('id', 'Unknown'))}")
        
        self.status = "busy"
        self.current_task = task
        
        try:
            # Pre-task setup
            await self.pre_task_setup(task)
            
            # Get relevant context from memory
            context = await self.get_task_context(task)
            
            # Execute the actual task
            result = await self.process_task(task, context)
            
            # Post-task cleanup
            await self.post_task_cleanup(task, result)
            
            self.status = "ready"
            self.current_task = None
            
            self.logger.info(f"Task completed: {task.get('id', 'Unknown')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Task failed: {e}")
            self.status = "error"
            self.current_task = None
            raise e
    
    async def execute_intelligent_task(self, task: Dict) -> Dict:
        """
        Execute a task with persistent intelligence - learns from experience
        and applies previous learnings to improve performance
        """
        task_description = task.get('description', task.get('title', 'Unknown task'))
        task_type = task.get('type', 'general')
        
        self.logger.info(f"Executing intelligent task: {task_description}")
        self.task_start_time = datetime.datetime.now()
        
        # Get expertise summary for this agent
        expertise = self.intelligence.get_agent_expertise_summary(self.role)
        self.logger.info(f"Agent expertise level: {expertise['expertise_level']} ({expertise['experience_count']} experiences)")
        
        # Get suggested approach based on previous experience
        suggestion = self.intelligence.suggest_approach(
            agent_role=self.role,
            task_description=task_description,
            project_context=self.current_project_context
        )
        
        if suggestion['confidence'] > 0.5:
            self.logger.info(f"Applying learned approach (confidence: {suggestion['confidence']:.2f})")
            self.logger.debug(f"Suggestion: {suggestion['suggestion']}")
        
        try:
            # Execute task with intelligence
            result = await self._execute_with_intelligence(task, suggestion)
            
            # Record successful experience
            if self.learning_enabled and result.get('success', True):
                await self._record_task_experience(task, result, suggestion, True)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Intelligent task failed: {e}")
            
            # Record failure experience
            if self.learning_enabled:
                await self._record_task_experience(task, {"error": str(e)}, suggestion, False)
            
            raise
    
    async def _execute_with_intelligence(self, task: Dict, suggestion: Dict) -> Dict:
        """Execute task applying intelligent suggestions"""
        
        # Combine suggested approach with standard execution
        enhanced_task = task.copy()
        
        if suggestion['confidence'] > 0.5:
            # Add intelligence context to the task
            enhanced_task['intelligence_context'] = {
                'suggested_approach': suggestion['suggestion'],
                'confidence': suggestion['confidence'],
                'experiences_used': suggestion['experiences_used']
            }
            
            # Add relevant patterns to the prompt/context
            if 'detailed_experiences' in suggestion:
                patterns = []
                for exp in suggestion['detailed_experiences'][:3]:
                    patterns.append(f"Pattern: {exp['pattern']} (Success rate: {exp['success_rate']:.1%})")
                enhanced_task['learned_patterns'] = patterns
        
        # Execute the enhanced task
        return await self.execute_task(enhanced_task)
    
    async def _record_task_experience(self, task: Dict, result: Dict, suggestion: Dict, was_successful: bool):
        """Record experience from task execution for future learning"""
        
        task_description = task.get('description', task.get('title', 'Unknown task'))
        task_type = task.get('type', 'general')
        
        # Determine experience type based on task
        experience_type = self._classify_experience_type(task_type, task)
        
        # Create solution description
        if was_successful:
            solution = result.get('solution', result.get('output', 'Task completed successfully'))
            outcome = f"Success: {result.get('summary', 'Task completed')}"
        else:
            solution = f"Attempted standard approach, encountered: {result.get('error', 'Unknown error')}"
            outcome = f"Failed: {result.get('error', 'Unknown error')}"
        
        # Calculate confidence based on success and time taken
        if self.task_start_time:
            execution_time = (datetime.datetime.now() - self.task_start_time).total_seconds()
            # Higher confidence for faster, successful execution
            time_factor = max(0.1, 1.0 - (execution_time / 3600))  # Normalize by hour
            confidence = (0.8 if was_successful else 0.3) * time_factor
        else:
            confidence = 0.8 if was_successful else 0.3
        
        # Record the experience
        exp_id = self.intelligence.record_experience(
            agent_role=self.role,
            experience_type=experience_type,
            context=task_description,
            solution=solution,
            outcome=outcome,
            project_context=self.current_project_context,
            confidence=confidence,
            tags=self._extract_tags_from_task(task)
        )
        
        # Update success rates for any experiences that were used
        for exp_id_used in suggestion.get('experiences_used', []):
            self.intelligence.update_experience_success(exp_id_used, was_successful)
        
        self.logger.debug(f"Recorded experience: {exp_id}")
    
    def _classify_experience_type(self, task_type: str, task: Dict) -> ExperienceType:
        """Classify the type of experience based on task characteristics"""
        
        task_lower = str(task).lower()
        
        if any(word in task_lower for word in ['debug', 'fix', 'error', 'bug']):
            return ExperienceType.DEBUGGING
        elif any(word in task_lower for word in ['optimize', 'performance', 'speed', 'efficient']):
            return ExperienceType.OPTIMIZATION
        elif any(word in task_lower for word in ['refactor', 'restructure', 'reorganize']):
            return ExperienceType.REFACTORING
        elif any(word in task_lower for word in ['integrate', 'connect', 'combine']):
            return ExperienceType.INTEGRATION
        elif any(word in task_lower for word in ['architect', 'design', 'structure']):
            return ExperienceType.ARCHITECTURE
        elif any(word in task_lower for word in ['workflow', 'process', 'pipeline']):
            return ExperienceType.WORKFLOW
        elif any(word in task_lower for word in ['solve', 'solution', 'resolve']):
            return ExperienceType.SOLUTION_PATTERN
        else:
            return ExperienceType.SOLUTION_PATTERN
    
    def _extract_tags_from_task(self, task: Dict) -> set:
        """Extract relevant tags from task for categorization"""
        tags = set()
        
        # Add language/framework tags
        if self.current_project_context.get('language'):
            tags.add(self.current_project_context['language'])
        if self.current_project_context.get('framework'):
            tags.add(self.current_project_context['framework'])
        
        # Extract tags from task content
        task_text = str(task).lower()
        
        # Technical tags
        tech_keywords = {
            'api', 'database', 'frontend', 'backend', 'security', 'performance',
            'testing', 'deployment', 'docker', 'git', 'ci/cd', 'authentication',
            'authorization', 'cors', 'rest', 'graphql', 'websocket', 'cache'
        }
        
        for keyword in tech_keywords:
            if keyword in task_text:
                tags.add(keyword)
        
        return tags
    
    async def get_learning_summary(self) -> Dict[str, Any]:
        """Get a summary of what this agent has learned"""
        expertise = self.intelligence.get_agent_expertise_summary(self.role)
        
        return {
            'agent_id': self.agent_id,
            'role': self.role,
            'expertise_level': expertise['expertise_level'],
            'total_experiences': expertise['experience_count'],
            'success_rate': expertise.get('average_success_rate', 0.0),
            'confidence': expertise.get('average_confidence', 0.0),
            'specializations': expertise.get('specializations', {}),
            'technologies': expertise.get('technologies', []),
            'top_patterns': expertise.get('most_successful_patterns', [])
        }
    
    async def teach_agent(self, lesson: Dict[str, Any]):
        """Manually teach the agent a specific lesson/pattern"""
        
        exp_id = self.intelligence.record_experience(
            agent_role=self.role,
            experience_type=ExperienceType(lesson.get('type', 'solution_pattern')),
            context=lesson['context'],
            solution=lesson['solution'],
            outcome=lesson.get('outcome', 'Manually taught pattern'),
            project_context=lesson.get('project_context', self.current_project_context),
            confidence=lesson.get('confidence', 1.0),
            tags=set(lesson.get('tags', []))
        )
        
        self.logger.info(f"Learned new pattern: {exp_id}")
        return exp_id
    
    async def health_check(self):
        """Perform health check"""
        try:
            # Check LLM connectivity
            await self.test_llm_connection()
            
            # Check memory connectivity
            await self.test_memory_connection()
            
            # Agent-specific health checks
            await self.agent_health_check()
            
            if self.status == "error":
                self.status = "ready"
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            self.status = "error"
            raise e
    
    async def stop(self):
        """Stop the agent"""
        self.logger.info(f"🛑 Stopping agent {self.agent_id}...")
        
        # Cancel current task if any
        if self.current_task:
            self.logger.warning("Cancelling current task...")
            self.current_task = None
        
        # Agent-specific cleanup
        await self.agent_cleanup()
        
        self.status = "stopped"
        self.logger.info(f"Agent {self.agent_id} stopped")
    
    # Abstract methods to be implemented by specific agents
    
    @abstractmethod
    async def agent_initialize(self):
        """Agent-specific initialization"""
        pass
    
    @abstractmethod
    async def process_task(self, task: Dict, context: Dict) -> Dict:
        """Process the actual task"""
        pass
    
    @abstractmethod
    async def agent_health_check(self):
        """Agent-specific health check"""
        pass
    
    @abstractmethod
    async def agent_cleanup(self):
        """Agent-specific cleanup"""
        pass
    
    # Helper methods
    
    async def load_configuration(self):
        """Load agent configuration"""
        # Load any agent-specific configuration
        pass
    
    async def initialize_memory(self):
        """Initialize agent memory"""
        # Get agent's previous context and memories
        context = await self.memory_manager.get_agent_context(self.agent_id)
        self.memories = context.get('memories', [])
    
    async def pre_task_setup(self, task: Dict):
        """Setup before task execution"""
        pass
    
    async def post_task_cleanup(self, task: Dict, result: Dict):
        """Cleanup after task execution"""
        # Store task result in memory using store_experience
        await self.memory_manager.store_experience(
            self.agent_id, 
            task,
            result,
            {
                "timestamp": datetime.datetime.now().isoformat()
            }
        )
    
    async def get_task_context(self, task: Dict) -> Dict:
        """Get relevant context for the task"""
        # Search for similar tasks in memory using query_memory
        similar_tasks = await self.memory_manager.query_memory(
            task.get('description', ''), 
            limit=3
        )
        
        return {
            'similar_tasks': similar_tasks,
            'agent_memories': self.memories[-5:],  # Last 5 memories
            'task_dependencies': task.get('dependencies', [])
        }
    
    async def generate_llm_response(self, prompt: str, task_type: str = "general", **kwargs) -> str:
        """Generate response using the best available LLM"""
        try:
            # Get the best model for this task
            best_model = await self.get_best_model_for_task(task_type)
            
            # Use the best model for generation
            response = await self.llm_manager.generate_response(
                agent_role=self.role,
                prompt=prompt,
                model=best_model,
                **kwargs
            )
            
            # Log model usage for monitoring
            if self.model_manager:
                try:
                    await self.model_manager._record_model_usage(best_model, True, 0.5)  # Assume success
                except Exception as e:
                    self.logger.debug(f"Failed to record model usage: {e}")
            
            return response.get('content', '')
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            
            # Try fallback model if available
            if self.model_manager and task_type != "fallback":
                self.logger.warning("Trying fallback model...")
                return await self.generate_llm_response(prompt, task_type="fallback", **kwargs)
            
            raise e
    
    async def test_llm_connection(self):
        """Test LLM connection"""
        try:
            await self.generate_llm_response("Hello", max_tokens=5)
        except Exception as e:
            raise Exception(f"LLM connection test failed: {e}")
    
    async def test_memory_connection(self):
        """Test memory connection"""
        try:
            await self.memory_manager.query_memory("test", limit=1)
        except Exception as e:
            raise Exception(f"Memory connection test failed: {e}")
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            'agent_id': self.agent_id,
            'status': self.status,
            'role': self.role,
            'model': self.model,
            'capabilities': self.capabilities,
            'current_task': self.current_task.get('id') if self.current_task else None,
            'memory_count': len(self.memories) if hasattr(self, 'memories') else 0
        }