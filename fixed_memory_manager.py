#!/usr/bin/env python3
"""
Fixed Memory-Aware Model Manager for 8GB VRAM Systems
Properly detects loaded models and intelligently manages them
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
    """Model manager that respects VRAM limitations and detects loaded models"""
    
    def __init__(self, max_vram_mb: int = 7000):
        self.logger = logging.getLogger("MemoryAwareModelManager")
        self.max_vram_mb = max_vram_mb
        self.current_vram_usage = 0
        
        # Model tracking
        self.available_models: Dict[str, ModelInfo] = {}
        self.loaded_models: List[str] = []
          # Provider configs
        self.providers = {
            'lmstudio': {
                'base_url': 'http://localhost:1234',
                'can_unload': True,
                'can_load': True,
                'max_concurrent': 5  # Allow your current setup
            },
            'ollama': {
                'base_url': 'http://127.0.0.1:11434', 
                'can_unload': True,
                'can_load': True,
                'max_concurrent': 3
            },
            'vllm': {
                'base_url': 'http://localhost:8000',
                'can_unload': True,  # Can stop/restart server
                'can_load': True,    # Can start server with different models
                'max_concurrent': 1  # Only one model at a time in vLLM
            }
        }
        
    async def initialize(self):
        """Initialize with proper model detection"""
        self.logger.info("Initializing Memory-Aware Model Manager (8GB VRAM mode)")
        
        # Discover and check loaded status
        await self._discover_and_check_models()
        
        # Calculate current VRAM usage
        self._calculate_current_usage()
        
        self.logger.info(f"Ready - {len(self.available_models)} models available, {len(self.loaded_models)} currently loaded")
          # Show current status
        status = await self.get_memory_status()
        self.logger.info(f"Current VRAM usage: {status['current_usage_mb']}MB / {status['max_vram_mb']}MB")
    
    async def _discover_and_check_models(self):
        """Discover models and check which are actually loaded"""
        self.logger.info("Discovering models and checking load status...")
        
        # Check LM Studio
        await self._check_lmstudio_models()
        
        # Check Ollama
        await self._check_ollama_models()
        
        # Check vLLM
        await self._check_vllm_models()
    
    async def _check_lmstudio_models(self):
        """Check LM Studio models and detect loaded ones"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.providers['lmstudio']['base_url']}/v1/models",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        loaded_count = 0
                        
                        for model in data.get('data', []):
                            model_id = model.get('id', '')
                            model_key = f"lmstudio:{model_id}"
                            
                            # Test if model is actually loaded
                            is_loaded = await self._test_model_responsiveness(model_id, 'lmstudio')
                            
                            model_info = ModelInfo(
                                provider='lmstudio',
                                model_id=model_id,
                                estimated_vram_mb=self._estimate_vram_from_name(model_id),
                                is_loaded=is_loaded,
                                last_used=datetime.now() if is_loaded else datetime.min
                            )
                            
                            self.available_models[model_key] = model_info
                            
                            if is_loaded:
                                self.loaded_models.append(model_key)
                                loaded_count += 1
                        
                        self.logger.info(f"LM Studio: {len(data.get('data', []))} models available, {loaded_count} loaded")
                        
        except Exception as e:
            self.logger.warning(f"LM Studio check failed: {e}")
    
    async def _check_ollama_models(self):
        """Check Ollama models and detect loaded ones"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.providers['ollama']['base_url']}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        loaded_count = 0
                        
                        for model in data.get('models', []):
                            model_name = model.get('name', '')
                            size_mb = model.get('size', 0) // (1024 * 1024)
                            model_key = f"ollama:{model_name}"
                            
                            # Test if model is loaded and responsive
                            is_loaded = await self._test_model_responsiveness(model_name, 'ollama')
                            
                            model_info = ModelInfo(
                                provider='ollama',
                                model_id=model_name,
                                estimated_vram_mb=max(size_mb, self._estimate_vram_from_name(model_name)),
                                is_loaded=is_loaded,
                                last_used=datetime.now() if is_loaded else datetime.min
                            )
                            
                            self.available_models[model_key] = model_info
                            
                            if is_loaded:
                                self.loaded_models.append(model_key)
                                loaded_count += 1
                        
                        self.logger.info(f"Ollama: {len(data.get('models', []))} models available, {loaded_count} loaded")
                        
        except Exception as e:
            self.logger.warning(f"Ollama check failed: {e}")
    
    async def _check_vllm_models(self):
        """Check vLLM models and detect loaded ones"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.providers['vllm']['base_url']}/v1/models",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        loaded_count = 0
                        
                        for model in data.get('data', []):
                            model_id = model.get('id', '')
                            model_key = f"vllm:{model_id}"
                            
                            # Test if model is actually loaded and responsive
                            is_loaded = await self._test_model_responsiveness(model_id, 'vllm')
                            
                            model_info = ModelInfo(
                                provider='vllm',
                                model_id=model_id,
                                estimated_vram_mb=self._estimate_vram_from_name(model_id),
                                is_loaded=is_loaded,
                                last_used=datetime.now() if is_loaded else datetime.min                            )
                            
                            self.available_models[model_key] = model_info
                            
                            if is_loaded:
                                self.loaded_models.append(model_key)
                                loaded_count += 1
                        
                        self.logger.info(f"vLLM: {len(data.get('data', []))} models available, {loaded_count} loaded")
                        
        except Exception as e:
            self.logger.warning(f"vLLM check failed: {e}")
    
    async def _test_model_responsiveness(self, model_id: str, provider: str) -> bool:
        """Test if a model is actually loaded and responsive"""
        try:
            if provider == 'lmstudio':
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": model_id,
                        "messages": [{"role": "user", "content": "test"}],
                        "max_tokens": 1,
                        "temperature": 0
                    }
                    async with session.post(
                        f"{self.providers['lmstudio']['base_url']}/v1/chat/completions",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=3)
                    ) as resp:
                        return resp.status == 200
            
            elif provider == 'ollama':
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": model_id,
                        "prompt": "test",
                        "stream": False
                    }
                    async with session.post(
                        f"{self.providers['ollama']['base_url']}/api/generate",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=3)
                    ) as resp:
                        return resp.status == 200
                        
            elif provider == 'vllm':
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": model_id,
                        "messages": [{"role": "user", "content": "test"}],
                        "max_tokens": 1,
                        "temperature": 0
                    }
                    async with session.post(
                        f"{self.providers['vllm']['base_url']}/v1/chat/completions",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=3)
                    ) as resp:
                        return resp.status == 200
                        
        except Exception:
            return False
        
        return False
    
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
            return 12000
        elif '70b' in model_name_lower or '72b' in model_name_lower:
            return 40000
        else:
            return 3000  # Default conservative estimate
    
    def _calculate_current_usage(self):
        """Calculate current VRAM usage from loaded models"""
        self.current_vram_usage = 0
        for model_key in self.loaded_models:
            if model_key in self.available_models:
                self.current_vram_usage += self.available_models[model_key].estimated_vram_mb
    
    async def get_best_model_for_task(self, task_type: str, agent_role: str) -> Optional[str]:
        """Get best model for task, preferring already loaded models"""
        
        # First, check loaded models
        for model_key in self.loaded_models:
            model = self.available_models.get(model_key)
            if model and self._is_suitable_for_task(model, task_type, agent_role):
                model.last_used = datetime.now()
                self.logger.info(f"Using already loaded model: {model.model_id}")
                return model_key
        
        # If no suitable loaded model, find best unloaded model
        candidates = []
        for key, model in self.available_models.items():
            if (key not in self.loaded_models and 
                self._is_suitable_for_task(model, task_type, agent_role)):
                score = self._calculate_task_score(model, task_type, agent_role)
                candidates.append((key, model, score))
        
        if not candidates:
            # Return any loaded model as fallback
            return self.loaded_models[0] if self.loaded_models else None
        
        # Sort by score and pick best
        candidates.sort(key=lambda x: x[2], reverse=True)
        best_key, best_model, score = candidates[0]
        
        # Try to load the best model if we have VRAM space
        if await self._can_load_model(best_model):
            success = await self._load_model(best_key)
            if success:
                return best_key
        
        # Return best loaded model as fallback
        return self.loaded_models[0] if self.loaded_models else None
    
    def _is_suitable_for_task(self, model: ModelInfo, task_type: str, agent_role: str) -> bool:
        """Check if model is suitable for the task"""
        model_name = model.model_id.lower()
        
        if task_type == "code_generation":
            return any(word in model_name for word in ['code', 'programming', 'dev', 'instruct'])
        
        if task_type in ["general", "analysis", "writing"]:
            return any(word in model_name for word in ['instruct', 'chat', 'assistant', 'it'])
        
        return True
    
    def _calculate_task_score(self, model: ModelInfo, task_type: str, agent_role: str) -> float:
        """Calculate how good a model is for a specific task"""
        score = 5.0  # Base score
        
        model_name = model.model_id.lower()
        
        # Size efficiency for 8GB VRAM
        if model.estimated_vram_mb <= 2500:
            score += 3  # Small models get bonus
        elif model.estimated_vram_mb <= 4500:
            score += 2  # Medium models
        elif model.estimated_vram_mb <= 7000:
            score += 1  # Large models that fit
        else:
            score -= 2  # Too large models get penalty
        
        # Task-specific bonuses
        if task_type == "code_generation":
            if any(word in model_name for word in ['code', 'dev', 'programming']):
                score += 3
        
        # Model quality indicators
        if any(word in model_name for word in ['instruct', 'chat']):
            score += 2
        
        return score
    
    async def _can_load_model(self, model: ModelInfo) -> bool:
        """Check if we can load a model without exceeding VRAM"""
        needed_vram = model.estimated_vram_mb
        available_vram = self.max_vram_mb - self.current_vram_usage
        
        return needed_vram <= available_vram
    
    async def _load_model(self, model_key: str) -> bool:
        """Load a model"""
        model = self.available_models[model_key]
        
        if model_key in self.loaded_models:
            return True
        
        try:
            if model.provider == 'ollama':
                success = await self._load_ollama_model(model.model_id)
            else:
                # For LM Studio, we assume user loads manually
                self.logger.info(f"To load {model.model_id}, please load it in LM Studio")
                success = True  # Optimistic
            
            if success:
                self.loaded_models.append(model_key)
                self.current_vram_usage += model.estimated_vram_mb
                model.is_loaded = True
                model.last_used = datetime.now()
                self.logger.info(f"Loaded {model.model_id} ({model.estimated_vram_mb}MB)")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to load {model.model_id}: {e}")
        
        return False
    
    async def _load_ollama_model(self, model_name: str) -> bool:
        """Load an Ollama model"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {"name": model_name}
                async with session.post(
                    f"{self.providers['ollama']['base_url']}/api/pull",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    return resp.status == 200
        except Exception:
            return False
    
    async def get_memory_status(self) -> Dict:
        """Get current memory usage status"""
        return {
            "max_vram_mb": self.max_vram_mb,
            "current_usage_mb": self.current_vram_usage,
            "available_mb": self.max_vram_mb - self.current_vram_usage,
            "loaded_models": len(self.loaded_models),
            "available_models": len(self.available_models),
            "memory_efficiency": (self.current_vram_usage / self.max_vram_mb) * 100 if self.max_vram_mb > 0 else 0
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
async def test_fixed_manager():
    """Test the fixed memory-aware manager"""
    print("Testing Fixed Memory-Aware Model Manager")
    
    manager = MemoryAwareModelManager(max_vram_mb=7000)
    await manager.initialize()
    
    print("\nMemory Status:")
    status = await manager.get_memory_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\nActive Models:")
    active = await manager.get_active_models()
    for provider, models in active.items():
        print(f"  {provider}: {len(models)} models")
        for model_id, info in models.items():
            print(f"    - {model_id}: {info['vram_mb']}MB")
    
    # Test model selection
    print("\nTesting model selection:")
    best_model = await manager.get_best_model_for_task("code_generation", "architect")
    print(f"Best model for code generation: {best_model}")

if __name__ == "__main__":
    asyncio.run(test_fixed_manager())
