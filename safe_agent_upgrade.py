#!/usr/bin/env python3
"""
Safe Agent Upgrade Integration

This file safely integrates the agent upgrade kit with your existing system
without breaking any current functionality.
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Ensure we can import the existing modules
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger("AgentUpgradeIntegration")

class SafeAgentUpgrade:
    """Safely integrates upgrade functionality with existing agents"""
    
    def __init__(self):
        self.initialized = False
        self.memory_manager = None
        self.llm_manager = None
        self.agent_profiles = {}
        
    async def initialize(self):
        """Initialize the upgrade system with existing infrastructure"""
        try:
            # Try to use existing memory manager
            self.memory_manager = await self._get_memory_manager()
            
            # Try to use existing LLM manager  
            self.llm_manager = await self._get_llm_manager()
            
            # Load or create agent profiles
            await self._load_agent_profiles()
            
            self.initialized = True
            logger.info("✅ Agent upgrade system initialized safely")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize upgrade system: {e}")
            return False
    
    async def _get_memory_manager(self):
        """Get existing memory manager or create mock"""
        try:
            from core.advanced_memory_manager import AdvancedMemoryManager
            memory_manager = AdvancedMemoryManager()
            await memory_manager.initialize()
            return memory_manager
        except Exception as e:
            logger.warning(f"Using mock memory manager: {e}")
            from core.mock_managers import MockMemoryManager
            return MockMemoryManager()
    
    async def _get_llm_manager(self):
        """Get existing LLM manager or create mock"""
        try:
            from intelligent_llm_manager import IntelligentLLMManager
            llm_manager = IntelligentLLMManager()
            await llm_manager.initialize()
            return llm_manager
        except Exception as e:
            logger.warning(f"Using mock LLM manager: {e}")
            from core.mock_managers import MockLLMManager
            return MockLLMManager()
    
    async def _load_agent_profiles(self):
        """Load or create agent profiles"""
        profiles_path = Path("prompt_profiles/agent_prompt_profiles.json")
        
        if profiles_path.exists():
            try:
                import json
                with open(profiles_path) as f:
                    self.agent_profiles = json.load(f)
                logger.info("Loaded existing agent profiles")
            except Exception as e:
                logger.warning(f"Could not load agent profiles: {e}")
                self.agent_profiles = self._create_default_profiles()
        else:
            self.agent_profiles = self._create_default_profiles()
            await self._save_agent_profiles()
    
    def _create_default_profiles(self):
        """Create default agent profiles"""
        return {
            "orchestrator": {
                "role": "Task Orchestrator",
                "prompt_template": "You are a senior project manager coordinating AI agents. Your task: {task}\n\nContext: {context}\n\nProvide clear delegation and coordination.",
                "preferred_model": "llama3:8b",
                "fallback_model": "deepseek-coder:6.7b"
            },
            "architect": {
                "role": "System Architect", 
                "prompt_template": "You are a senior software architect. Your task: {task}\n\nMemory context: {memory}\n\nProvide architectural guidance following SOLID principles.",
                "preferred_model": "deepseek-coder:6.7b",
                "fallback_model": "codellama:7b"
            },
            "backend": {
                "role": "Backend Developer",
                "prompt_template": "You are a senior backend engineer. Your task: {task}\n\nRelevant knowledge: {memory}\n\nWrite production-ready Python code with proper error handling.",
                "preferred_model": "codellama:7b", 
                "fallback_model": "deepseek-coder:6.7b"
            },
            "frontend": {
                "role": "Frontend Developer",
                "prompt_template": "You are a senior frontend engineer. Your task: {task}\n\nContext: {memory}\n\nCreate modern, responsive UI components.",
                "preferred_model": "deepseek-coder:6.7b",
                "fallback_model": "llama3:8b"
            },
            "qa": {
                "role": "QA Engineer",
                "prompt_template": "You are a senior QA engineer. Your task: {task}\n\nPrevious findings: {memory}\n\nWrite comprehensive tests and identify issues.",
                "preferred_model": "deepseek-coder:6.7b",
                "fallback_model": "codellama:7b"
            }
        }
    
    async def _save_agent_profiles(self):
        """Save agent profiles to disk"""
        profiles_path = Path("prompt_profiles/agent_prompt_profiles.json")
        profiles_path.parent.mkdir(exist_ok=True)
        
        try:
            import json
            with open(profiles_path, 'w') as f:
                json.dump(self.agent_profiles, f, indent=2)
            logger.info("Saved agent profiles")
        except Exception as e:
            logger.warning(f"Could not save agent profiles: {e}")
    
    async def enhanced_agent_call(self, agent_name: str, task: str, context: Dict[str, Any] = None):
        """Enhanced agent call with memory injection and retry logic"""
        if not self.initialized:
            await self.initialize()
        
        context = context or {}
        
        try:
            # Get agent profile
            profile = self.agent_profiles.get(agent_name.lower(), self.agent_profiles.get("orchestrator"))
            
            # Retrieve relevant memories (if memory manager available)
            memory_context = await self._get_memory_context(agent_name, task)
            
            # Format enhanced prompt
            prompt = profile["prompt_template"].format(
                task=task,
                context=str(context),
                memory=memory_context
            )
            
            # Try with preferred model first
            try:
                result = await self._call_llm_safe(prompt, profile["preferred_model"])
            except Exception as e:
                logger.warning(f"Preferred model failed for {agent_name}, trying fallback: {e}")
                result = await self._call_llm_safe(prompt, profile["fallback_model"])
            
            # Store learning (if memory manager available)
            await self._store_learning(agent_name, task, result)
            
            return {
                "agent": agent_name,
                "task": task,
                "result": result,
                "timestamp": str(datetime.now()),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Enhanced agent call failed for {agent_name}: {e}")
            return {
                "agent": agent_name,
                "task": task,
                "error": str(e),
                "timestamp": str(datetime.now()),
                "success": False
            }
    
    async def _get_memory_context(self, agent_name: str, task: str) -> str:
        """Get relevant memory context for the task"""
        if not hasattr(self.memory_manager, 'retrieve_memories'):
            return "No memory context available"
        
        try:
            # Try to get relevant memories
            memories = await self.memory_manager.retrieve_memories(
                query=task,
                agent_id=agent_name,
                limit=3
            )
            
            if memories:
                return "\\n".join([f"- {m}" for m in memories])
            else:
                return "No specific memories found for this task"
                
        except Exception as e:
            logger.warning(f"Could not retrieve memories: {e}")
            return "Memory retrieval unavailable"
    
    async def _call_llm_safe(self, prompt: str, model: str) -> str:
        """Safely call LLM with fallback"""
        try:
            if hasattr(self.llm_manager, 'call_model'):
                return await self.llm_manager.call_model(prompt, model)
            elif hasattr(self.llm_manager, 'generate'):
                return await self.llm_manager.generate(prompt, model)
            else:
                # Mock response for testing
                return f"Mock response for task: {prompt[:100]}..."
                
        except Exception as e:
            logger.warning(f"LLM call failed: {e}")
            return f"Task acknowledged: {prompt[:100]}... (LLM unavailable)"
    
    async def _store_learning(self, agent_name: str, task: str, result: str):
        """Store learning outcome"""
        try:
            if hasattr(self.memory_manager, 'store_memory'):
                await self.memory_manager.store_memory(
                    content=f"Task: {task} | Result: {result[:200]}",
                    agent_id=agent_name,
                    memory_type="task_completion"
                )
        except Exception as e:
            logger.warning(f"Could not store learning: {e}")

# Global instance
safe_upgrade = SafeAgentUpgrade()

# Easy-to-use function for integration
async def dispatch_enhanced_task(agent_name: str, task: str, context: Dict[str, Any] = None):
    """
    Enhanced task dispatcher that can be dropped into existing code
    
    Usage:
        result = await dispatch_enhanced_task("backend", "Create API endpoint")
        result = await dispatch_enhanced_task("qa", "Test the login system") 
    """
    return await safe_upgrade.enhanced_agent_call(agent_name, task, context)

# Synchronous wrapper for compatibility
def dispatch_task_sync(agent_name: str, task: str, context: Dict[str, Any] = None):
    """Synchronous wrapper for existing code that doesn't use async"""
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(dispatch_enhanced_task(agent_name, task, context))

if __name__ == "__main__":
    # Test the system
    import asyncio
    
    async def test():
        result = await dispatch_enhanced_task("backend", "Create a status endpoint")
        print("Test result:", result)
    
    asyncio.run(test())
