"""
VRAM-Aware Model Manager for 8GB GPU Systems

This module provides intelligent model management for systems with limited VRAM,
ensuring optimal performance while preventing memory exhaustion.
"""

import asyncio
import logging
import psutil
import subprocess
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class VRAMManager:
    """Manages VRAM usage and model loading for 8GB systems"""
    
    def __init__(self, max_vram_gb: float = 7.5):
        self.max_vram_gb = max_vram_gb
        self.current_vram_usage = 0.0
        self.loaded_models = {}
        self.model_vram_usage = {}
        self.last_activity = {}
        self.unload_timeout = 600  # 10 minutes
          # Model size estimates (in GB) - Updated for latest models
        self.model_sizes = {
            # Ollama models (latest)
            "ollama/llama3.2:1b": 1.2,
            "ollama/llama3.2:3b": 2.0,
            "ollama/llama3.1:8b": 4.7,
            "ollama/llama3.1:70b": 40.0,  # Too large for 8GB
            "ollama/phi3:mini": 2.3,
            "ollama/phi3:medium": 7.9,
            "ollama/gemma2:2b": 1.6,
            "ollama/gemma2:9b": 5.4,
            "ollama/mistral:7b": 4.1,
            "ollama/codellama:7b": 3.8,
            "ollama/codellama:13b": 7.3,
            "ollama/deepseek-coder:6.7b": 3.9,
            "ollama/starcoder2:3b": 1.7,
            "ollama/starcoder2:7b": 4.0,
            "ollama/qwen2.5:7b": 4.3,
            "ollama/qwen2.5:14b": 8.2,  # Borderline for 8GB
            "ollama/stable-code:3b": 1.8,
            
            # LM Studio models
            "lmstudio/microsoft-phi-3-mini": 2.3,
            "lmstudio/microsoft-phi-3-medium": 7.9,
            "lmstudio/meta-llama-3.1-8b": 4.7,
            "lmstudio/mistral-7b-instruct": 4.1,
            "lmstudio/codellama-7b-instruct": 3.8,
            "lmstudio/gemma-2-2b-it": 1.6,
            "lmstudio/gemma-2-9b-it": 5.4,
            "lmstudio/qwen2.5-7b-instruct": 4.3,
            "lmstudio/deepseek-coder-6.7b": 3.9,
            "lmstudio/starcoder2-7b": 4.0,
            
            # vLLM models
            "vllm/microsoft/phi-3-mini": 2.3,
            "vllm/meta-llama/Llama-3.1-8B": 4.7,
            "vllm/mistralai/Mistral-7B-Instruct": 4.1,
            "vllm/Qwen/Qwen2.5-7B-Instruct": 4.3,
            
            # Legacy fallbacks
            "ollama/stable-code:3b": 1.8,
            "ollama/phi:2.7b": 1.5,
            "ollama/gemma3:4b": 2.2,
            "ollama/qwen3:8b": 4.8,
            "ollama/deepseek-r1:latest": 4.0,
            "ollama/mistral-small:latest": 4.1,
            
            "lmstudio/phi-2": 1.4,
            "lmstudio/gemma-2b-it": 1.6,
            "lmstudio/codellama-3.2-3b": 1.8,
            "lmstudio/dolly-v2-3b": 1.9,
            "lmstudio/codellama-7b-instruct": 3.8,
            
            "vllm/microsoft/phi-2": 1.4,
        }
        
        # Start cleanup task
        asyncio.create_task(self.cleanup_unused_models())
    
    async def can_load_model(self, model_id: str) -> bool:
        """Check if model can be loaded without exceeding VRAM limit"""
        model_size = self.model_sizes.get(model_id, 4.0)  # Default 4GB if unknown
        
        if model_id in self.loaded_models:
            return True  # Already loaded
        
        return (self.current_vram_usage + model_size) <= self.max_vram_gb
    
    async def get_optimal_model_for_task(self, task_type: str, agent_type: str, 
                                       model_preferences: List[str]) -> Optional[str]:
        """Get optimal model considering VRAM constraints"""
        
        # First, try already loaded models
        for model_id in model_preferences:
            if model_id in self.loaded_models:
                await self.update_model_activity(model_id)
                logger.info(f"Using already loaded model: {model_id}")
                return model_id
        
        # Then, try to load the best available model
        for model_id in model_preferences:
            if await self.can_load_model(model_id):
                if await self.load_model(model_id):
                    logger.info(f"Loaded new model: {model_id}")
                    return model_id
        
        # If no preferred model can be loaded, try to free space
        logger.warning("⚠️ No preferred model can be loaded, attempting to free VRAM...")
        
        # Unload least recently used models
        await self.free_vram_for_model(model_preferences[0])
        
        # Try again
        for model_id in model_preferences:
            if await self.can_load_model(model_id):
                if await self.load_model(model_id):
                    logger.info(f"Loaded model after cleanup: {model_id}")
                    return model_id
        
        # Fallback to smallest loaded model
        if self.loaded_models:
            smallest_model = min(self.loaded_models.keys(), 
                                key=lambda x: self.model_sizes.get(x, 4.0))
            logger.warning(f"⚠️ Falling back to smallest loaded model: {smallest_model}")
            return smallest_model
        
        logger.error("❌ No models available - VRAM management failed")
        return None
    
    async def load_model(self, model_id: str) -> bool:
        """Load a model if VRAM allows"""
        try:
            if model_id in self.loaded_models:
                await self.update_model_activity(model_id)
                return True
            
            if not await self.can_load_model(model_id):
                logger.warning(f"⚠️ Cannot load {model_id} - insufficient VRAM")
                return False
            
            # Simulate model loading (in real implementation, this would call the actual model API)
            model_size = self.model_sizes.get(model_id, 4.0)
            
            # Check if we need to free space for large models
            if model_size > 5.0:  # Large model threshold
                await self.ensure_single_large_model(model_id)
            
            self.loaded_models[model_id] = {
                'loaded_at': datetime.now(),
                'provider': model_id.split('/')[0],
                'size_gb': model_size
            }
            
            self.current_vram_usage += model_size
            await self.update_model_activity(model_id)
            
            logger.info(f"Loaded model {model_id} ({model_size}GB), total VRAM: {self.current_vram_usage:.1f}GB")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load model {model_id}: {e}")
            return False
    
    async def unload_model(self, model_id: str) -> bool:
        """Unload a model to free VRAM"""
        try:
            if model_id not in self.loaded_models:
                return True
            
            model_info = self.loaded_models[model_id]
            model_size = model_info['size_gb']
            
            # In real implementation, this would call the model provider's unload API
            del self.loaded_models[model_id]
            self.current_vram_usage -= model_size
            
            if model_id in self.last_activity:
                del self.last_activity[model_id]
            
            logger.info(f"Unloaded model {model_id} ({model_size}GB), remaining VRAM: {self.current_vram_usage:.1f}GB")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to unload model {model_id}: {e}")
            return False
    
    async def ensure_single_large_model(self, new_model_id: str):
        """Ensure only one large model (>5GB) is loaded at a time"""
        new_model_size = self.model_sizes.get(new_model_id, 4.0)
        
        if new_model_size <= 5.0:
            return  # Not a large model
        
        # Unload other large models
        large_models_to_unload = []
        for model_id, model_info in self.loaded_models.items():
            if model_info['size_gb'] > 5.0:
                large_models_to_unload.append(model_id)
        
        for model_id in large_models_to_unload:
            await self.unload_model(model_id)
            logger.info(f"Unloaded large model {model_id} to make room for {new_model_id}")
    
    async def free_vram_for_model(self, target_model_id: str):
        """Free VRAM to make space for a target model"""
        target_size = self.model_sizes.get(target_model_id, 4.0)
        needed_space = target_size - (self.max_vram_gb - self.current_vram_usage)
        
        if needed_space <= 0:
            return  # Already enough space
        
        # Sort models by last activity (oldest first)
        models_by_activity = sorted(
            self.last_activity.items(),
            key=lambda x: x[1]
        )
        
        freed_space = 0
        for model_id, _ in models_by_activity:
            if freed_space >= needed_space:
                break
            
            if model_id in self.loaded_models:
                model_size = self.loaded_models[model_id]['size_gb']
                await self.unload_model(model_id)
                freed_space += model_size
        
        logger.info(f"Freed {freed_space:.1f}GB VRAM for {target_model_id}")
    
    async def update_model_activity(self, model_id: str):
        """Update last activity time for a model"""
        self.last_activity[model_id] = datetime.now()
    
    async def cleanup_unused_models(self):
        """Periodically unload unused models"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                cutoff_time = datetime.now() - timedelta(seconds=self.unload_timeout)
                models_to_unload = []
                
                for model_id, last_used in self.last_activity.items():
                    if last_used < cutoff_time and model_id in self.loaded_models:
                        # Don't unload essential models
                        if not self.is_essential_model(model_id):
                            models_to_unload.append(model_id)
                
                for model_id in models_to_unload:
                    await self.unload_model(model_id)
                    logger.info(f"Auto-unloaded unused model: {model_id}")
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
    
    def is_essential_model(self, model_id: str) -> bool:
        """Check if model should always remain loaded"""
        essential_models = [
            "ollama/phi:2.7b",
            "lmstudio/phi-2"
        ]
        return model_id in essential_models
    
    async def get_vram_status(self) -> Dict:
        """Get current VRAM usage status"""
        return {
            'current_usage_gb': self.current_vram_usage,
            'max_usage_gb': self.max_vram_gb,
            'usage_percentage': (self.current_vram_usage / self.max_vram_gb) * 100,
            'available_gb': self.max_vram_gb - self.current_vram_usage,
            'loaded_models': list(self.loaded_models.keys()),
            'model_count': len(self.loaded_models)
        }
    
    async def force_emergency_cleanup(self):
        """Emergency cleanup when VRAM is critically low"""
        logger.warning("🚨 Emergency VRAM cleanup initiated!")
        
        # Keep only essential models
        models_to_keep = ["ollama/phi:2.7b", "lmstudio/phi-2"]
        models_to_unload = [
            model_id for model_id in self.loaded_models.keys()
            if model_id not in models_to_keep
        ]
        
        for model_id in models_to_unload:
            await self.unload_model(model_id)
        
        logger.warning(f"🚨 Emergency cleanup complete. Kept {len(models_to_keep)} essential models.")

    async def get_gpu_memory_info(self) -> Dict[str, float]:
        """Get actual GPU memory information"""
        try:
            import subprocess
            import re
            
            # Try nvidia-smi first
            try:
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=memory.total,memory.used,memory.free", "--format=csv,noheader,nounits"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        total, used, free = map(float, line.split(', '))
                        return {
                            'total_gb': total / 1024,
                            'used_gb': used / 1024,
                            'free_gb': free / 1024,
                            'utilization_percent': (used / total) * 100
                        }
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
            
            # Fallback to estimated values
            return {
                'total_gb': 8.0,  # Assume 8GB system
                'used_gb': self.current_vram_usage,
                'free_gb': 8.0 - self.current_vram_usage,
                'utilization_percent': (self.current_vram_usage / 8.0) * 100
            }
            
        except Exception as e:
            logger.warning(f"Could not get GPU memory info: {e}")
            return {
                'total_gb': 8.0,
                'used_gb': self.current_vram_usage,
                'free_gb': 8.0 - self.current_vram_usage,
                'utilization_percent': (self.current_vram_usage / 8.0) * 100
            }

    async def get_recommended_models_for_system(self) -> List[str]:
        """Get list of models recommended for current VRAM configuration"""
        available_vram = self.max_vram_gb
        recommended = []
        
        # Categorize models by VRAM requirements
        small_models = []  # <2GB
        medium_models = []  # 2-4GB
        large_models = []   # 4-8GB
        
        for model_id, size in self.model_sizes.items():
            if size < 2.0:
                small_models.append((model_id, size))
            elif size < 4.0:
                medium_models.append((model_id, size))
            elif size <= available_vram:
                large_models.append((model_id, size))
        
        # Sort by size (smaller first for each category)
        small_models.sort(key=lambda x: x[1])
        medium_models.sort(key=lambda x: x[1])
        large_models.sort(key=lambda x: x[1])
        
        # Recommend best models for different use cases
        if available_vram >= 7.0:
            recommended.extend([m[0] for m in large_models[:3]])  # Top 3 large models
        
        recommended.extend([m[0] for m in medium_models[:3]])  # Top 3 medium models
        recommended.extend([m[0] for m in small_models[:2]])   # Top 2 small models
        
        return recommended

    async def optimize_for_system(self) -> Dict[str, Any]:
        """Optimize VRAM manager for current system"""
        gpu_info = await self.get_gpu_memory_info()
        
        # Adjust max VRAM based on actual available memory
        actual_total = gpu_info['total_gb']
        if actual_total < 8.0:
            # For systems with less than 8GB, be more conservative
            self.max_vram_gb = actual_total * 0.85
        else:
            # For 8GB+ systems, use 7.5GB as planned
            self.max_vram_gb = min(7.5, actual_total * 0.9)
        
        recommended_models = await self.get_recommended_models_for_system()
        
        optimization_info = {
            'detected_vram_gb': actual_total,
            'configured_max_gb': self.max_vram_gb,
            'recommended_models': recommended_models,
            'optimization_level': 'aggressive' if actual_total <= 8.0 else 'balanced',
            'concurrent_model_limit': 1 if actual_total <= 6.0 else 2
        }
        
        logger.info(f"🎯 VRAM optimization complete: {optimization_info['optimization_level']} mode, "
                   f"max {self.max_vram_gb:.1f}GB, {len(recommended_models)} recommended models")
        
        return optimization_info


class ModelRotationManager:
    """Manages model rotation to optimize performance with limited VRAM"""
    
    def __init__(self, vram_manager: VRAMManager):
        self.vram_manager = vram_manager
        self.rotation_interval = 300  # 5 minutes
        self.last_rotation = datetime.now()
        self.rotation_history = []
        
    async def should_rotate_model(self, current_model: str, task_type: str) -> bool:
        """Determine if model rotation would be beneficial"""
        # Don't rotate if model was recently rotated
        if (datetime.now() - self.last_rotation).seconds < 60:
            return False
        
        # Don't rotate if current model is performing well
        vram_status = await self.vram_manager.get_vram_status()
        if vram_status['usage_percentage'] < 80:
            return False
        
        # Rotate if we're approaching VRAM limit
        return vram_status['usage_percentage'] > 90
    
    async def rotate_to_optimal_model(self, task_type: str, agent_type: str, 
                                    preferences: List[str]) -> Optional[str]:
        """Rotate to a more optimal model for the current task"""
        current_models = list(self.vram_manager.loaded_models.keys())
        
        # Find a better model that's not currently loaded
        for preferred_model in preferences:
            if preferred_model not in current_models:
                if await self.vram_manager.can_load_model(preferred_model):
                    # Unload least important model first
                    await self._unload_least_important_model(task_type)
                    
                    if await self.vram_manager.load_model(preferred_model):
                        self.last_rotation = datetime.now()
                        self.rotation_history.append({
                            'timestamp': datetime.now(),
                            'from_models': current_models.copy(),
                            'to_model': preferred_model,
                            'reason': f'Optimization for {task_type}'
                        })
                        return preferred_model
        
        return None
    
    async def _unload_least_important_model(self, current_task_type: str):
        """Unload the least important model for current task"""
        # Priority: keep models relevant to current task
        task_relevant_models = self._get_task_relevant_models(current_task_type)
        
        for model_id in self.vram_manager.loaded_models.keys():
            if (model_id not in task_relevant_models and 
                not self.vram_manager.is_essential_model(model_id)):
                await self.vram_manager.unload_model(model_id)
                break
    
    def _get_task_relevant_models(self, task_type: str) -> List[str]:
        """Get models that are relevant for the current task type"""
        task_model_map = {
            'code_generation': ['ollama/stable-code:3b', 'ollama/deepseek-r1:latest'],
            'code_review': ['ollama/phi:2.7b', 'lmstudio/phi-2'],
            'architecture': ['ollama/gemma3:4b', 'ollama/qwen3:8b'],
            'testing': ['ollama/phi:2.7b', 'lmstudio/phi-2'],
            'debugging': ['ollama/deepseek-r1:latest', 'ollama/stable-code:3b']
        }
        
        return task_model_map.get(task_type, [])
