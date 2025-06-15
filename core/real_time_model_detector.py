#!/usr/bin/env python3
"""
Real-time Model Detection and Intelligence
Detects which local models are actually available and working
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Set
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RealTimeModelDetector:
    """Detects available models in real-time"""
    
    def __init__(self):
        self.endpoints = {
            "ollama": {
                "base_url": "http://127.0.0.1:11434",
                "models_endpoint": "/api/tags",
                "health_endpoint": "/api/version"
            },
            "vllm": {
                "base_url": "http://localhost:8000",
                "models_endpoint": "/v1/models",
                "health_endpoint": "/health"
            },
            "lm_studio": {
                "base_url": "http://localhost:1234", 
                "models_endpoint": "/v1/models",
                "health_endpoint": "/v1/models"
            }
        }
        self.available_models = {}
        self.last_check = None
        self.check_interval = 30  # seconds
        
    async def detect_available_models(self, force_refresh: bool = False) -> Dict[str, List[str]]:
        """Detect which models are actually available right now"""
        current_time = datetime.now()
        
        # Use cache if recent
        if (not force_refresh and self.last_check and 
            (current_time - self.last_check).seconds < self.check_interval):
            return self.available_models
        
        self.available_models = {}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
            for provider, config in self.endpoints.items():
                try:
                    models = await self._check_provider_models(session, provider, config)
                    if models:
                        self.available_models[provider] = models
                        logger.info(f"✅ {provider}: {len(models)} models available")
                    else:
                        logger.debug(f"⚠️ {provider}: No models available")
                except Exception as e:
                    logger.debug(f"❌ {provider}: {str(e)}")
        
        self.last_check = current_time
        return self.available_models
    
    async def _check_provider_models(self, session: aiohttp.ClientSession, 
                                   provider: str, config: Dict) -> List[str]:
        """Check what models a specific provider has available"""
        try:
            # First check if provider is alive
            health_url = f"{config['base_url']}{config['health_endpoint']}"
            async with session.get(health_url) as response:
                if response.status != 200:
                    return []
            
            # Get available models
            models_url = f"{config['base_url']}{config['models_endpoint']}"
            async with session.get(models_url) as response:
                if response.status != 200:
                    return []
                
                data = await response.json()
                return self._extract_model_names(provider, data)
                
        except Exception as e:
            logger.debug(f"Error checking {provider}: {e}")
            return []
    
    def _extract_model_names(self, provider: str, data: Dict) -> List[str]:
        """Extract model names from provider response"""
        models = []
        
        if provider == "ollama":
            # Ollama format: {"models": [{"name": "llama3:latest"}, ...]}
            for model in data.get("models", []):
                name = model.get("name", "").split(":")[0]  # Remove version tags
                if name:
                    models.append(name)
        
        elif provider in ["vllm", "lm_studio"]:
            # OpenAI format: {"data": [{"id": "model-name"}, ...]}
            for model in data.get("data", []):
                name = model.get("id", "")
                if name and not name.startswith("gpt-"):  # Filter out placeholder names
                    models.append(name)
        
        return list(set(models))  # Remove duplicates
    
    def get_best_model_for_task(self, task_type: str, intelligence_level: float) -> Optional[str]:
        """Get the best available model for a specific task type and intelligence level"""
        if not self.available_models:
            return None
        
        # Define model preferences based on task type and intelligence
        preferences = self._get_model_preferences(task_type, intelligence_level)
        
        # Find first available model from preferences
        for provider, models in preferences:
            if provider in self.available_models:
                available = self.available_models[provider]
                for preferred_model in models:
                    if preferred_model in available:
                        return f"{provider}/{preferred_model}"
        
        # Fallback to any available model
        for provider, models in self.available_models.items():
            if models:
                return f"{provider}/{models[0]}"
        
        return None
    
    def _get_model_preferences(self, task_type: str, intelligence_level: float) -> List[tuple]:
        """Get ordered model preferences based on task and intelligence"""
        if intelligence_level >= 8.0:
            # Genius level - prefer best models
            if task_type == "coding":
                return [
                    ("lm_studio", ["deepseek-coder", "codellama", "code-model"]),
                    ("ollama", ["codellama", "deepseek-coder"]),
                    ("vllm", ["microsoft/CodeGPT-small-py", "gpt2-medium"])
                ]
            elif task_type == "analysis":
                return [
                    ("lm_studio", ["chat-model", "local-model"]),
                    ("ollama", ["mistral", "llama3", "llama2"]),
                    ("vllm", ["gpt2-medium", "gpt2"])
                ]
        
        elif intelligence_level >= 6.0:
            # Advanced level - balanced models
            if task_type == "coding":
                return [
                    ("ollama", ["codellama", "llama3"]),
                    ("vllm", ["microsoft/CodeGPT-small-py", "gpt2-medium"]),
                    ("lm_studio", ["code-model", "local-model"])
                ]
            elif task_type == "analysis":
                return [
                    ("ollama", ["mistral", "llama3"]),
                    ("vllm", ["gpt2-medium", "gpt2"]),
                    ("lm_studio", ["chat-model"])
                ]
        
        else:
            # Learning level - simpler models
            return [
                ("vllm", ["gpt2-medium", "gpt2"]),
                ("ollama", ["llama3", "mistral"]),
                ("lm_studio", ["local-model"])
            ]
        
        # Default fallback
        return [
            ("ollama", ["llama3", "mistral", "codellama"]),
            ("vllm", ["gpt2", "gpt2-medium"]),
            ("lm_studio", ["local-model", "chat-model"])
        ]
    
    def get_available_providers(self) -> Set[str]:
        """Get set of currently available providers"""
        return set(self.available_models.keys())
    
    def is_provider_available(self, provider: str) -> bool:
        """Check if a specific provider is available"""
        return provider in self.available_models and len(self.available_models[provider]) > 0
