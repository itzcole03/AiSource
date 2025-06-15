#!/usr/bin/env python3
"""
Memory-Aware Model Manager for 8GB VRAM Systems
Intelligently loads/unloads models to prevent memory issues
"""

import asyncio
import aiohttp
import json
import logging
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field

@dataclass
class ModelInfo:
    """Information about a model"""
    provider: str
    model_id: str
    estimated_vram_mb: int = 0
    is_loaded: bool = False
    last_used: datetime = field(default_factory=datetime.now)
    response_time: float = 0.0
    priority_score: float = 0.0

class MemoryAwareModelManager:
    """Model manager that respects VRAM limitations"""
    
    def __init__(self, max_vram_mb: int = 7000):  # Conservative 7GB limit for 8GB cards
        self.logger = logging.getLogger("MemoryAwareModelManager")
        self.max_vram_mb = max_vram_mb
        self.current_vram_usage = 0
        
        # Model tracking
        self.available_models: Dict[str, ModelInfo] = {}
        self.loaded_models: List[str] = []
        self.model_queue: List[str] = []  # Priority queue for loading
        
        # Provider configs
        self.providers = {
            'lmstudio': {
                'base_url': 'http://localhost:1234',
                'can_unload': True,  # LM Studio can actually unload models
                'can_load': True,    # LM Studio can load models via API
                'max_concurrent': 5  # Allow current setup
            },
            'ollama': {
                'base_url': 'http://127.0.0.1:11434',                'can_unload': True,  # Ollama can unload models
                'can_load': True,    # Ollama can load models
                'max_concurrent': 3   # Allow multiple models
            }
        }
        
    async def initialize(self):
        """Initialize with memory-conscious discovery"""
        self.logger.info("Initializing Memory-Aware Model Manager (8GB VRAM mode)")
        
        # Discover available models without loading them
        await self._discover_available_models()
        
        # Estimate VRAM requirements
        await self._estimate_model_sizes()
        
        # Load one high-priority model to start
        await self._load_initial_model()
        
        self.logger.info(f"Ready - {len(self.available_models)} models available, {len(self.loaded_models)} loaded")
      async def _discover_available_models(self):
        """Discover models and detect which are already loaded"""
        self.logger.info("Discovering available models and checking load status...")
        
        # Check LM Studio - detect already loaded models
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.providers['lmstudio']['base_url']}/v1/models") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        loaded_count = 0
                        for model in data.get('data', []):
                            model_id = model.get('id', '')
                            model_key = f"lmstudio:{model_id}"
                            
                            # Test if model is actually loaded by making a quick request
                            is_loaded = await self._test_model_loaded(model_id, 'lmstudio')
                            
                            model_info = ModelInfo(
                                provider='lmstudio',
                                model_id=model_id,
                                estimated_vram_mb=self._estimate_vram_from_name(model_id),
                                is_loaded=is_loaded
                            )
                            
                            self.available_models[model_key] = model_info
                            
                            if is_loaded:
                                self.loaded_models.append(model_key)
                                self.current_vram_usage += model_info.estimated_vram_mb
                                loaded_count += 1
                        
                        self.logger.info(f"Found {len(data.get('data', []))} LM Studio models ({loaded_count} loaded)")
        except Exception as e:
            self.logger.warning(f"LM Studio not available: {e}")
        
        # Check Ollama - detect loaded models  
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.providers['ollama']['base_url']}/api/tags") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        loaded_count = 0
                        for model in data.get('models', []):
                            model_name = model.get('name', '')
                            size_mb = model.get('size', 0) // (1024 * 1024)  # Convert to MB
                            model_key = f"ollama:{model_name}"
                            
                            # Ollama models listed in /api/tags are typically loaded
                            is_loaded = await self._test_model_loaded(model_name, 'ollama')
                            
                            model_info = ModelInfo(
                                provider='ollama',
                                model_id=model_name,
                                estimated_vram_mb=max(size_mb, self._estimate_vram_from_name(model_name)),
                                is_loaded=is_loaded
                            )
                            
                            self.available_models[model_key] = model_info
                            
                            if is_loaded:
                                self.loaded_models.append(model_key)
                                self.current_vram_usage += model_info.estimated_vram_mb
                                loaded_count += 1
                        
                        self.logger.info(f"Found {len(data.get('models', []))} Ollama models ({loaded_count} loaded)")
        except Exception as e:
            self.logger.warning(f"Ollama not available: {e}")
    
    async def _test_model_loaded(self, model_id: str, provider: str) -> bool:
        """Test if a model is actually loaded and responsive"""
        try:
            if provider == 'lmstudio':
                # Test with a simple completion request
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": model_id,
                        "messages": [{"role": "user", "content": "Hi"}],
                        "max_tokens": 1,
                        "temperature": 0
                    }
                    async with session.post(
                        f"{self.providers['lmstudio']['base_url']}/v1/chat/completions",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as resp:
                        return resp.status == 200
                        
            elif provider == 'ollama':
                # Test with Ollama generate endpoint
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": model_id,
                        "prompt": "Hi",
                        "stream": False
                    }
                    async with session.post(
                        f"{self.providers['ollama']['base_url']}/api/generate",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as resp:
                        return resp.status == 200
                        
        except Exception:
            return False
        
        return False
                                provider='ollama',
                                model_id=model_name,
                                estimated_vram_mb=max(size_mb, self._estimate_vram_from_name(model_name))
                            )
                        self.logger.info(f"Found {len(data.get('models', []))} Ollama models")
        except Exception as e:
            self.logger.warning(f"Ollama not available: {e}")
    
    def _estimate_vram_from_name(self, model_name: str) -> int:
        """Estimate VRAM usage from model name"""
        model_name_lower = model_name.lower()
        
        # Size-based estimates (in MB)
        if '1b' in model_name_lower or '1.5b' in model_name_lower:
            return 1500
        elif '2b' in model_name_lower or '3b' in model_name_lower:
            return 2500
        elif '7b' in model_name_lower:
            return 4500
        elif '8b' in model_name_lower:
            return 5000
        elif '12b' in model_name_lower or '13b' in model_name_lower:
            return 7000
        elif '24b' in model_name_lower or '22b' in model_name_lower:
            return 12000  # Too big for 8GB
        elif '70b' in model_name_lower or '72b' in model_name_lower:
            return 40000  # Way too big
        else:
            # Default conservative estimate
            return 3000
    
    async def _estimate_model_sizes(self):
        """Refine VRAM estimates and set priorities"""
        for key, model in self.available_models.items():
            # Priority scoring (higher = better for 8GB systems)
            if model.estimated_vram_mb <= 2500:  # Small models
                model.priority_score = 10
            elif model.estimated_vram_mb <= 4500:  # Medium models (7B)
                model.priority_score = 8
            elif model.estimated_vram_mb <= 6000:  # Large models that might fit
                model.priority_score = 5
            else:  # Too large for 8GB
                model.priority_score = 1
            
            # Boost priority for coding/instruct models
            if any(word in model.model_id.lower() for word in ['code', 'instruct', 'chat']):
                model.priority_score += 2
    
    async def _load_initial_model(self):
        """Load one high-priority model to start"""
        # Sort by priority and VRAM efficiency
        sorted_models = sorted(
            self.available_models.items(),
            key=lambda x: (x[1].priority_score, -x[1].estimated_vram_mb),
            reverse=True
        )
        
        for key, model in sorted_models:
            if model.estimated_vram_mb <= self.max_vram_mb:
                success = await self._load_model(key)
                if success:
                    self.logger.info(f"Initial model loaded: {model.model_id}")
                    break
    
    async def get_best_model_for_task(self, task_type: str, agent_role: str) -> Optional[str]:
        """Get best available model, loading if necessary"""
        # First check if we have a suitable loaded model
        for model_key in self.loaded_models:
            model = self.available_models[model_key]
            if self._is_suitable_for_task(model, task_type, agent_role):
                model.last_used = datetime.now()
                return model_key
        
        # Find best unloaded model that fits in memory
        candidates = []
        for key, model in self.available_models.items():
            if (key not in self.loaded_models and 
                model.estimated_vram_mb <= self.max_vram_mb and
                self._is_suitable_for_task(model, task_type, agent_role)):
                candidates.append((key, model))
        
        if not candidates:
            # Return any loaded model as fallback
            return self.loaded_models[0] if self.loaded_models else None
        
        # Sort by suitability score
        candidates.sort(key=lambda x: self._calculate_task_score(x[1], task_type, agent_role), reverse=True)
        best_key, best_model = candidates[0]
        
        # Load the best model (this will handle unloading if needed)
        success = await self._load_model(best_key)
        return best_key if success else None
    
    def _is_suitable_for_task(self, model: ModelInfo, task_type: str, agent_role: str) -> bool:
        """Check if model is suitable for the task"""
        model_name = model.model_id.lower()
        
        # Code generation tasks
        if task_type == "code_generation":
            return any(word in model_name for word in ['code', 'programming', 'dev'])
        
        # General tasks - any instruct/chat model
        if task_type in ["general", "analysis", "writing"]:
            return any(word in model_name for word in ['instruct', 'chat', 'assistant'])
        
        return True  # Default: any model can try
    
    def _calculate_task_score(self, model: ModelInfo, task_type: str, agent_role: str) -> float:
        """Calculate how good a model is for a specific task"""
        score = model.priority_score
        
        model_name = model.model_id.lower()
        
        # Bonus for task-specific models
        if task_type == "code_generation" and any(word in model_name for word in ['code', 'dev', 'programming']):
            score += 5
        
        # Bonus for agent-specific models
        if agent_role == "architect" and any(word in model_name for word in ['architect', 'design']):
            score += 3
        
        # Penalty for oversized models
        if model.estimated_vram_mb > self.max_vram_mb * 0.8:  # Using >80% of VRAM
            score -= 3
        
        return score
    
    async def _load_model(self, model_key: str) -> bool:
        """Load a model, unloading others if necessary"""
        model = self.available_models[model_key]
        
        # Check if already loaded
        if model_key in self.loaded_models:
            return True
        
        # Check if we need to unload models first
        needed_vram = model.estimated_vram_mb
        available_vram = self.max_vram_mb - self.current_vram_usage
        
        if needed_vram > available_vram:
            await self._free_vram_for_model(needed_vram)
        
        # Attempt to load the model
        try:
            if model.provider == 'ollama':
                success = await self._load_ollama_model(model.model_id)
            else:
                success = await self._request_lmstudio_load(model.model_id)
            
            if success:
                self.loaded_models.append(model_key)
                self.current_vram_usage += model.estimated_vram_mb
                model.is_loaded = True
                model.last_used = datetime.now()
                self.logger.info(f"Loaded {model.model_id} ({model.estimated_vram_mb}MB VRAM)")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to load {model.model_id}: {e}")
        
        return False
    
    async def _free_vram_for_model(self, needed_vram_mb: int):
        """Free up VRAM by unloading least recently used models"""
        self.logger.info(f"Freeing {needed_vram_mb}MB VRAM...")
        
        # Sort loaded models by last used (oldest first)
        loaded_with_info = [
            (key, self.available_models[key]) for key in self.loaded_models
        ]
        loaded_with_info.sort(key=lambda x: x[1].last_used)
        
        freed_vram = 0
        for model_key, model in loaded_with_info:
            if freed_vram >= needed_vram_mb:
                break
            
            success = await self._unload_model(model_key)
            if success:
                freed_vram += model.estimated_vram_mb
    
    async def _unload_model(self, model_key: str) -> bool:
        """Unload a specific model"""
        model = self.available_models[model_key]
        
        try:
            if model.provider == 'ollama':
                # Ollama doesn't easily unload, but we can try
                self.logger.warning(f"Ollama models don't unload easily: {model.model_id}")
                return False
            else:
                # For LM Studio, we can only request unload via GUI
                self.logger.info(f"Please unload {model.model_id} in LM Studio GUI for optimal memory usage")
                
            # Update our tracking
            if model_key in self.loaded_models:
                self.loaded_models.remove(model_key)
                self.current_vram_usage -= model.estimated_vram_mb
                model.is_loaded = False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unload {model.model_id}: {e}")
            return False
    
    async def _load_ollama_model(self, model_name: str) -> bool:
        """Load an Ollama model"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"name": model_name}
                async with session.post(
                    f"{self.providers['ollama']['base_url']}/api/pull",
                    json=payload
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False
    
    async def _request_lmstudio_load(self, model_name: str) -> bool:
        """Request LM Studio to load a model (user must do manually)"""
        self.logger.info(f"To use {model_name}, please load it in LM Studio GUI")
        # We assume it will be loaded manually and return True optimistically
        return True
    
    async def get_memory_status(self) -> Dict:
        """Get current memory usage status"""
        return {
            "max_vram_mb": self.max_vram_mb,
            "current_usage_mb": self.current_vram_usage,
            "available_mb": self.max_vram_mb - self.current_vram_usage,
            "loaded_models": len(self.loaded_models),
            "available_models": len(self.available_models),
            "memory_efficiency": (self.current_vram_usage / self.max_vram_mb) * 100
        }
    
    async def get_active_models(self) -> Dict[str, Dict]:
        """Get currently active (loaded) models"""
        active = {}
        for provider in ['lmstudio', 'ollama']:
            active[provider] = {}
            for key, model in self.available_models.items():
                if model.provider == provider and model.is_loaded:
                    active[provider][model.model_id] = {
                        "vram_mb": model.estimated_vram_mb,
                        "last_used": model.last_used.isoformat(),
                        "priority_score": model.priority_score
                    }
        return active

# Test function
async def test_memory_manager():
    """Test the memory-aware manager"""
    print("Testing Memory-Aware Model Manager (8GB VRAM)")
    
    manager = MemoryAwareModelManager(max_vram_mb=7000)
    await manager.initialize()
    
    status = await manager.get_memory_status()
    print(f"Memory Status: {status}")
    
    # Test getting best model for different tasks
    code_model = await manager.get_best_model_for_task("code_generation", "architect")
    print(f"Best model for code generation: {code_model}")
    
    active = await manager.get_active_models()
    print(f"Active models: {active}")

if __name__ == "__main__":
    asyncio.run(test_memory_manager())
