#!/usr/bin/env python3
"""
Advanced Model Discovery and Management System
Tracks actively loaded models, monitors responsiveness, and can intelligently load/unload models.
"""

import asyncio
import aiohttp
import logging
import time
from typing import Dict, List, Optional, Tuple, Set, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field

@dataclass
class ModelStatus:
    """Tracks detailed status of a specific model"""
    provider: str
    model_id: str
    is_loaded: bool = False
    is_responsive: bool = False
    last_response_time: float = 0.0
    last_check: datetime = field(default_factory=datetime.now)
    response_count: int = 0
    error_count: int = 0
    average_response_time: float = 0.0
    memory_usage: Optional[int] = None
    load_time: Optional[datetime] = None
    capabilities: Dict = field(default_factory=dict)

@dataclass 
class ProviderStatus:
    """Tracks status of a model provider"""
    name: str
    base_url: str
    is_online: bool = False
    loaded_models: Set[str] = field(default_factory=set)
    available_models: Set[str] = field(default_factory=set)
    can_load_models: bool = False
    can_unload_models: bool = False
    max_concurrent_models: int = 1
    last_check: datetime = field(default_factory=datetime.now)

# (Removed duplicate ModelLoadBalancer class definition to resolve name conflict)

class AdvancedModelManager:
    """Advanced Model Discovery and Management System"""

    def __init__(self, check_interval: int = 15):
        self.logger = logging.getLogger("AdvancedModelManager")
        self.check_interval = check_interval

        self.models = {}  # Track all models and their status
        self.currently_loaded_models = []  # Track which models are actually loaded
        self.model_memory_usage = {}  # Track estimated memory per model

        # Initialize load balancer attribute
        self.load_balancer = ModelLoadBalancer(self)

        # Provider configs moved here for global access
        self.provider_configs = {
            'lmstudio': {
                'base_url': 'http://localhost:1234',
                'can_load_models': True,  # LM Studio can load/unload via GUI
                'can_unload_models': True,
                'max_concurrent_models': 1,  # STRICT: Only one model at a time for VRAM
                'memory_limit_gb': 6,  # Reserve 2GB for system
                'endpoints': {
                    'models': '/v1/models',
                    'chat': '/v1/chat/completions',
                    'load': None,  # Would need custom API
                    'unload': None
                }
            },
    'ollama': {
        'base_url': 'http://127.0.0.1:11434',
        'can_load_models': True,  # Ollama can pull/load models
        'can_unload_models': True,  # We'll implement smart unloading
        'max_concurrent_models': 2,  # CONSERVATIVE: Max 2 small models
        'memory_limit_gb': 6,  # Reserve 2GB for system
        'endpoints': {
            'models': '/api/tags',
            'generate': '/api/generate',
            'pull': '/api/pull',
            'delete': '/api/delete'
        }
    },
            'vllm': {
                'base_url': 'http://localhost:8000',
                'can_load_models': False,  # vLLM loads models at server startup
                'can_unload_models': False,  # Server restart required for model change
                'max_concurrent_models': 1,  # Single model per vLLM server instance
                'memory_limit_gb': 6,  # Reserve 2GB for system
                'endpoints': {
                    'models': '/v1/models',
                    'chat': '/v1/chat/completions',
                    'completions': '/v1/completions',
                    'health': '/health'
                }
            }        }
        
        self.providers = {}
        for name, config in self.provider_configs.items():
            self.providers[name] = ProviderStatus(
                name=name,
                base_url=config['base_url'],
                can_load_models=config['can_load_models'],
                can_unload_models=config['can_unload_models'],
                max_concurrent_models=config['max_concurrent_models']
            )

    async def initialize(self):
        """Initialize the model manager and start monitoring."""
        await self._discover_model_states()
        await self._start_monitoring()

    async def _discover_model_states(self):
        """Discover current state of all models"""
        self.logger.info("Discovering model states...")
        for name, config in self.provider_configs.items():
            self.providers[name] = ProviderStatus(
                name=name,
                base_url=config['base_url'],
                can_load_models=config['can_load_models'],
                can_unload_models=config['can_unload_models'],
                max_concurrent_models=config['max_concurrent_models']
            )
        
        # Now check each provider for active models
        for name, provider in self.providers.items():
            if name == 'lmstudio':
                await self._check_lmstudio_models(provider)
            elif name == 'ollama':
                await self._check_ollama_models(provider)
            elif name == 'vllm':
                await self._check_vllm_models(provider)
    
    async def _check_lmstudio_models(self, provider: ProviderStatus):
        """Check LM Studio model states with responsiveness testing"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check if server is online
                async with session.get(f"{provider.base_url}/v1/models", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        provider.is_online = True
                        data = await response.json()
                        models = data.get('data', [])
                        
                        provider.loaded_models.clear()
                        
                        for model_info in models:
                            model_id = model_info.get('id', '')
                            if model_id:
                                provider.loaded_models.add(model_id)
                                
                                # Test if model is actually responsive
                                is_responsive = await self._test_model_responsiveness(
                                    'lmstudio', model_id
                                )
                                
                                # Update model status
                                model_key = f"lmstudio/{model_id}"
                                if model_key not in self.models:
                                    self.models[model_key] = ModelStatus(
                                        provider='lmstudio',
                                        model_id=model_id
                                    )
                                
                                model_status = self.models[model_key]
                                model_status.is_loaded = True
                                model_status.is_responsive = is_responsive
                                model_status.last_check = datetime.now()
                                
                                if not model_status.load_time:
                                    model_status.load_time = datetime.now()
                        
                        self.logger.info(f"LM Studio: {len(provider.loaded_models)} models loaded")
                    else:
                        provider.is_online = False
                        
        except Exception as e:
            provider.is_online = False
            self.logger.warning(f"LM Studio check failed: {e}")
    
    async def _check_ollama_models(self, provider: ProviderStatus):
        """Check Ollama model states with detailed analysis"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get list of installed models
                async with session.get(f"{provider.base_url}/api/tags", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        provider.is_online = True
                        data = await response.json()
                        models = data.get('models', [])
                        
                        provider.available_models.clear()
                        provider.loaded_models.clear()
                        
                        for model_info in models:
                            model_name = model_info.get('name', '')
                            if model_name:
                                provider.available_models.add(model_name)
                                
                                # For Ollama, we need to test if model is actually loaded/responsive
                                is_responsive = await self._test_model_responsiveness(
                                    'ollama', model_name
                                )
                                
                                if is_responsive:
                                    provider.loaded_models.add(model_name)
                                
                                # Update model status
                                model_key = f"ollama/{model_name}"
                                if model_key not in self.models:
                                    self.models[model_key] = ModelStatus(
                                        provider='ollama',
                                        model_id=model_name
                                    )
                                
                                model_status = self.models[model_key]
                                model_status.is_loaded = is_responsive  # Only loaded if responsive
                                model_status.is_responsive = is_responsive
                                model_status.last_check = datetime.now()
                        
                        self.logger.info(f"Ollama: {len(provider.loaded_models)}/{len(provider.available_models)} models active")
                    else:
                        provider.is_online = False
                        
        except Exception as e:
            provider.is_online = False
            self.logger.warning(f"Ollama check failed: {e}")
    
    async def _check_vllm_models(self, provider: ProviderStatus):
        """Check vLLM model states and server responsiveness"""
        try:
            async with aiohttp.ClientSession() as session:
                # Check server health first
                try:
                    async with session.get(f"{provider.base_url}/health", timeout=aiohttp.ClientTimeout(total=3)) as response:
                        if response.status != 200:
                            provider.is_online = False
                            return
                except:
                    # Health endpoint might not exist, try models endpoint
                    pass
                
                # Get list of available models
                async with session.get(f"{provider.base_url}/v1/models", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        provider.is_online = True
                        data = await response.json()
                        models = data.get('data', [])
                        
                        provider.loaded_models.clear()
                        
                        for model_info in models:
                            model_id = model_info.get('id', '')
                            if model_id:
                                provider.loaded_models.add(model_id)
                                
                                # Test if model is actually responsive
                                is_responsive = await self._test_model_responsiveness(
                                    'vllm', model_id
                                )
                                
                                # Update model status
                                model_key = f"vllm/{model_id}"
                                if model_key not in self.models:
                                    self.models[model_key] = ModelStatus(
                                        provider='vllm',
                                        model_id=model_id
                                    )
                                
                        self.logger.info(f"vLLM: {len(provider.loaded_models)} model(s) loaded")
                    else:
                        provider.is_online = False

        except Exception as e:
            provider.is_online = False
            self.logger.warning(f"vLLM check failed: {e}")

    async def _test_model_responsiveness(self, provider: str, model_id: str) -> bool:
        """Test if a specific model is actually responsive"""
        try:
            start_time = time.time()

            if provider == 'lmstudio':
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": model_id,
                        "messages": [{"role": "user", "content": "test"}],
                        "max_tokens": 1,
                        "temperature": 0
                    }
                    async with session.post(
                        f"{self.providers[provider].base_url}/v1/chat/completions",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=8)
                    ) as response:
                        if response.status == 200:
                            response_time = time.time() - start_time
                            await self._update_model_performance(f"{provider}/{model_id}", response_time, True)
                            return True

            elif provider == 'ollama':
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": model_id,
                        "prompt": "test",
                        "stream": False,
                        "options": {"num_predict": 1}
                    }
                    async with session.post(
                        f"{self.providers[provider].base_url}/api/generate",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=8)
                    ) as response:
                        if response.status == 200:
                            response_time = time.time() - start_time
                            await self._update_model_performance(f"{provider}/{model_id}", response_time, True)
                            return True

            elif provider == 'vllm':
                async with aiohttp.ClientSession() as session:
                    payload = {
                        "model": model_id,
                        "messages": [{"role": "user", "content": "test"}],
                        "max_tokens": 1,
                        "temperature": 0
                    }
                    async with session.post(
                        f"{self.providers[provider].base_url}/v1/chat/completions",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=8)
                    ) as response:
                        if response.status == 200:
                            response_time = time.time() - start_time
                            await self._update_model_performance(f"{provider}/{model_id}", response_time, True)
                            return True

            return False

        except Exception:
            await self._update_model_performance(f"{provider}/{model_id}", 0, False)
            return False

    async def _update_model_performance(self, model_key: str, response_time: float, success: bool):
        """Update model performance statistics."""
        model = self.models.get(model_key)
        if not model:
            return
        model.last_response_time = response_time
        model.last_check = datetime.now()
        model.response_count += 1
        if not success:
            model.error_count += 1
        # Update average response time (simple moving average)
        if model.average_response_time == 0:
            model.average_response_time = response_time
        else:
            model.average_response_time = (
                (model.average_response_time * (model.response_count - 1) + response_time) / model.response_count
            )
    
    async def _start_monitoring(self):
        """Start continuous monitoring of model states"""
        self.monitoring_active = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        self.logger.info(f"Started continuous monitoring (interval: {self.check_interval}s)")
    
    async def _monitor_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                await asyncio.sleep(self.check_interval)
                await self._discover_model_states()
                await self._cleanup_stale_models()
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
    
    async def _cleanup_stale_models(self):
        """Remove models that haven't been seen recently"""
        cutoff_time = datetime.now() - timedelta(minutes=5)
        
        stale_models = [
            key for key, model in self.models.items()
            if model.last_check < cutoff_time
        ]
        
        for key in stale_models:
            self.logger.info(f"🧹 Removing stale model: {key}")
            del self.models[key]
    
    async def get_active_models(self) -> Dict[str, ModelStatus]:
        """Get only currently active and responsive models"""
        return {
            key: model for key, model in self.models.items()
            if model.is_loaded and model.is_responsive
        }
    
    async def get_best_model_for_task(self, task_type: str, agent_role: str, priority: str = "balanced") -> Optional[str]:
        """Get the best currently active model for a specific task"""
        active_models = await self.get_active_models()
        
        if not active_models:
            self.logger.warning("No active models available")
            return None
        
        return await self.load_balancer.select_optimal_model(
            active_models, task_type, agent_role, priority
        )
    
    async def trigger_model_load(self, provider: str, model_name: str) -> bool:
        """Attempt to trigger loading of a specific model"""
        if provider not in self.providers:
            return False
            
        provider_info = self.providers[provider]
        
        if not provider_info.can_load_models:
            self.logger.warning(f"{provider} cannot load models programmatically")
            return False
        
        try:
            if provider == 'ollama':
                # Ollama can pull/load models
                async with aiohttp.ClientSession() as session:
                    payload = {"name": model_name}
                    async with session.post(
                        f"{provider_info.base_url}/api/pull",
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=300)  # Model loading can take a while
                    ) as response:
                        if response.status == 200:
                            self.logger.info(f"Successfully triggered loading of {model_name}")
                            # Re-check model states
                            await self._discover_model_states()
                            return True
            
            elif provider == 'lmstudio':
                # LM Studio requires manual loading via GUI
                self.logger.info(f"💡 Please manually load {model_name} in LM Studio")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to load {model_name}: {e}")
            
        return False
    
    async def get_status_report(self) -> Dict:
        """Generate comprehensive status report"""
        active_models = await self.get_active_models()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'providers': {},
            'active_models': len(active_models),
            'total_models': len(self.models),
            'models': {}
        }
        
        # Provider status
        for name, provider in self.providers.items():
            report['providers'][name] = {
                'online': provider.is_online,
                'loaded_models': len(provider.loaded_models),
                'available_models': len(provider.available_models),
                'can_load_models': provider.can_load_models,
                'max_concurrent': provider.max_concurrent_models
            }
        
        # Model details
        for key, model in self.models.items():
            report['models'][key] = {
                'loaded': model.is_loaded,
                'responsive': model.is_responsive,
                'avg_response_time': model.average_response_time,
                'response_count': model.response_count,
                'error_count': model.error_count,
                'last_check': model.last_check.isoformat()
            }
        
        return report
    
    async def stop_monitoring(self):
        """Stop the monitoring system"""
        self.monitoring_active = False
        if hasattr(self, 'monitor_task') and self.monitor_task:
            self.monitor_task.cancel()
            self.logger.info("Monitoring stopped")
    
    async def get_memory_usage(self) -> Dict[str, float]:
        """Get estimated memory usage of loaded models"""
        memory_usage = {}
        
        # Check Ollama models and their sizes
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.providers['ollama'].base_url}/api/tags",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        for model in data.get('models', []):
                            model_name = model['name']
                            size_bytes = model.get('size', 0)
                            size_gb = size_bytes / (1024**3)  # Convert to GB
                            memory_usage[f"ollama/{model_name}"] = size_gb
        except Exception as e:
            self.logger.warning(f"Failed to get Ollama memory usage: {e}")
        
        # LM Studio - estimate based on loaded models (we can't get exact size via API)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.providers['lmstudio'].base_url}/v1/models",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        for model in data.get('data', []):
                            model_name = model['id']
                            # Estimate based on model name patterns
                            estimated_gb = self._estimate_model_size(model_name)
                            memory_usage[f"lmstudio/{model_name}"] = estimated_gb
        except Exception as e:
            self.logger.warning(f"Failed to get LM Studio memory usage: {e}")
        
        return memory_usage
    
    def _estimate_model_size(self, model_name: str) -> float:
        """Estimate model size based on name patterns"""
        model_name_lower = model_name.lower()
        
        # Size estimation based on common patterns
        if any(x in model_name_lower for x in ['7b', '8b']):
            return 4.5  # ~4.5GB for 7B models
        elif any(x in model_name_lower for x in ['3b', '2.7b']):
            return 2.0  # ~2GB for 3B models
        elif any(x in model_name_lower for x in ['1b', '1.5b']):
            return 1.0  # ~1GB for 1B models
        elif any(x in model_name_lower for x in ['13b', '14b']):
            return 8.0  # ~8GB for 13B models (likely too big for 8GB VRAM)
        elif any(x in model_name_lower for x in ['24b', '22b']):
            return 15.0  # Way too big for 8GB VRAM
        else:
            return 3.0  # Conservative default
    
    async def check_memory_constraints(self) -> Dict[str, Any]:
        """Check if current memory usage is within 8GB VRAM limits"""
        memory_usage = await self.get_memory_usage()
        total_usage = sum(memory_usage.values())
        
        return {
            'total_usage_gb': total_usage,
            'vram_limit_gb': 8.0,
            'usage_percentage': (total_usage / 8.0) * 100,
            'memory_safe': total_usage <= 6.0,  # Leave 2GB buffer
            'models_loaded': len(memory_usage),
            'memory_by_model': memory_usage,
            'needs_unloading': total_usage > 6.0
        }
    
    async def smart_model_selection_with_memory(self, task_type: str, agent_role: str) -> Optional[str]:
        """Select best model while considering memory constraints"""
        # Check current memory usage
        memory_status = await self.check_memory_constraints()
        
        if memory_status['needs_unloading']:
            self.logger.warning(f"Memory usage too high: {memory_status['total_usage_gb']:.1f}GB, need to unload models")
            await self.smart_unload_models()
        
        # Get available models that fit in memory
        available_models = await self.get_active_models()
        suitable_models = {}
        
        for model_id, model_status in available_models.items():
            if model_status.is_responsive:
                estimated_size = self._estimate_model_size(model_id)

                # Check if this model would fit
                current_usage = memory_status['total_usage_gb']
                if current_usage + estimated_size <= 6.0:  # 6GB limit with 2GB buffer
                    suitable_models[model_id] = {
                        'provider': model_status.provider,
                        'status': model_status,
                        'estimated_size_gb': estimated_size,
                        'performance_score': self._calculate_model_score(model_status, task_type, agent_role)
                    }

    
    async def smart_unload_models(self):
        """Intelligently unload models to free memory"""
        memory_usage = await self.get_memory_usage()
        
        # Sort models by size (largest first) and last usage
        models_by_priority = []
        
        for model_full_name, size_gb in memory_usage.items():
            provider, model_name = model_full_name.split('/', 1)
            model_status = self.models.get(model_full_name)

            # Priority for unloading: larger models with older last_check times
            if model_status:
                priority_score = size_gb * 10 + (
                    (datetime.now() - model_status.last_check).total_seconds() / 3600
                )  # Size weight + hours since last use

                models_by_priority.append({
                    'model_name': model_name,
                    'provider': provider,
                    'size_gb': size_gb,
                    'priority_score': priority_score
                })

        # Sort by priority score descending (largest and oldest first)
        models_by_priority.sort(key=lambda x: x['priority_score'], reverse=True)

    # (Removed duplicate definition; now only inside AdvancedModelManager)
    
    def _calculate_model_score(self, model_status: 'ModelStatus', task_type: str, agent_role: str) -> float:
        """Calculate performance score for model selection"""
        base_score = 1.0
        
        # Response time factor (faster is better)
        if model_status.average_response_time > 0:
            time_score = max(0.1, 1.0 / model_status.average_response_time)
            base_score *= time_score
        
        # Reliability factor
        if model_status.response_count > 0:
            reliability = 1.0 - (model_status.error_count / max(1, model_status.response_count))
            base_score *= reliability
        
        # Task-specific preferences
        model_name_lower = model_status.model_id.lower()
        
        if task_type == "code_generation":
            if any(x in model_name_lower for x in ['code', 'codellama', 'starcoder']):
                base_score *= 1.5
        elif task_type == "reasoning":
            if any(x in model_name_lower for x in ['mistral', 'qwen', 'gemma']):
                base_score *= 1.3
        
        return base_score

class ModelLoadBalancer:
    """Intelligent load balancing for model selection"""
    
    def __init__(self, model_manager):
        self.model_manager = model_manager
        self.logger = logging.getLogger("ModelLoadBalancer")
    
    async def select_optimal_model(self, active_models: Dict[str, ModelStatus], 
                                 task_type: str, agent_role: str, priority: str) -> Optional[str]:
        """Select optimal model based on current load and performance"""
        
        if not active_models:
            return None
        
        # Score each model
        model_scores = {}
        
        for model_key, model_status in active_models.items():
            score = await self._score_model(model_status, task_type, agent_role, priority)
            model_scores[model_key] = score
        
        # Select best model
        if model_scores:
            best_model = max(model_scores.keys(), key=lambda k: model_scores[k])
            self.logger.info(f"Load balancer selected: {best_model} (score: {model_scores[best_model]:.2f})")
            return best_model
        
        return None
    
    async def _score_model(self, model: ModelStatus, task_type: str, agent_role: str, priority: str) -> float:
        """Score a model for selection"""
        score = 0.0
        
        # Base responsiveness score
        if model.is_responsive:
            score += 10.0
        
        # Performance-based scoring
        if model.average_response_time > 0:
            if priority == "speed":
                # Prefer faster models
                score += max(0, 5.0 - model.average_response_time)
            elif priority == "quality":
                # Slightly prefer slower (presumably larger) models
                score += min(5.0, model.average_response_time * 0.5)
            else:  # balanced
                score += max(0, 3.0 - model.average_response_time * 0.5)
        
        # Reliability scoring
        if model.response_count > 0:
            success_rate = (model.response_count - model.error_count) / model.response_count
            score += success_rate * 3.0
        
        # Provider preference (LM Studio tends to be more stable)
        if model.provider == 'lmstudio':
            score += 1.0
        
        return score

# Test the advanced model manager
async def test_advanced_model_manager():
    """Test the advanced model management system"""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

    manager = AdvancedModelManager(check_interval=10)  # Check every 10 seconds

    print("ADVANCED MODEL MANAGER TEST")
    print("=" * 50)

    try:
        # Initialize
        await manager.initialize()

        # Wait a bit for initial discovery
        await asyncio.sleep(2)

        # Get status report
        report = await manager.get_status_report()

        print(f"\nSTATUS REPORT")
        print(f"Active Models: {report['active_models']}")
        print(f"Total Models: {report['total_models']}")

        print(f"\nProviders:")
        for name, info in report['providers'].items():
            status = "ONLINE" if info['online'] else "OFFLINE"
            print(f"  {name}: {status} - {info['loaded_models']} loaded")

        print(f"\nActive Models:")
        active_models = await manager.get_active_models()
        for key, model in active_models.items():
            print(f"  {key}: {model.average_response_time:.2f}s avg, {model.response_count} calls")

        # Test model selection
        print(f"\n🎯 MODEL SELECTION TEST")

        test_scenarios = [
            ('architect', 'system_design', 'quality'),
            ('backend_dev', 'code_generation', 'speed'),
            ('orchestrator', 'planning', 'balanced')
        ]

        for agent_role, task_type, priority in test_scenarios:
            best_model = await manager.get_best_model_for_task(task_type, agent_role, priority)
            print(f"  {agent_role} + {task_type} ({priority}): {best_model}")

        # Monitor for a bit
        print(f"\n📊 Monitoring for 30 seconds...")
        await asyncio.sleep(30)

    finally:
        await manager.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(test_advanced_model_manager())
