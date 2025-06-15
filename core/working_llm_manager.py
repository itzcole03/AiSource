"""
Working Real LLM Manager for connecting to local models
Focuses on LM Studio with OpenAI client compatibility
"""

import asyncio
import aiohttp
import json
import logging
import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class WorkingLLMManager:
    """Working LLM Manager that connects to actual local models"""
    
    def __init__(self, config_path: str = "config/models_config.yaml"):
        self.logger = logging.getLogger("WorkingLLM")
        self.config_path = Path(config_path)
        self.config = {}
        self.active_providers = {}
        self.agent_model_map = {}
        
    async def initialize(self):
        """Initialize the working LLM manager"""
        self.logger.info("Initializing Working LLM Manager...")
        
        # Load configuration
        await self._load_config()
        
        # Test provider connections
        await self._test_providers()
        
        # Set up agent model assignments
        await self._setup_agent_assignments()
        
        self.logger.info("Working LLM Manager initialized successfully")
        
    async def _load_config(self):
        """Load models configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            self.logger.info(f"Loaded config from {self.config_path}")
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            # Use fallback config
            self.config = self._get_fallback_config()
    
    async def _test_providers(self):
        """Test connections to available providers"""
        providers = self.config.get('providers', {})
        
        for provider_name, config in providers.items():
            if not config.get('enabled', False):
                continue
                
            base_url = config.get('base_url')
            try:
                if provider_name == "lmstudio":
                    # Test LM Studio models endpoint
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{base_url}/v1/models", timeout=5) as response:
                            if response.status == 200:
                                self.active_providers[provider_name] = {
                                    'base_url': base_url,
                                    'config': config
                                }
                                self.logger.info(f"{provider_name} available at {base_url}")
                            else:
                                self.logger.warning(f"{provider_name} not available at {base_url}")
                                
                elif provider_name == "ollama":
                    # Test Ollama tags endpoint
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{base_url}/api/tags", timeout=5) as response:
                            if response.status == 200:
                                self.active_providers[provider_name] = {
                                    'base_url': base_url,
                                    'config': config
                                }
                                self.logger.info(f"{provider_name} available at {base_url}")
                            else:
                                self.logger.warning(f"{provider_name} not available at {base_url}")
                                
            except Exception as e:
                self.logger.warning(f"{provider_name} not available: {e}")
    
    async def _setup_agent_assignments(self):
        """Set up agent-to-model assignments"""
        assignments = self.config.get('agent_assignments', {})
        
        for agent_role, config in assignments.items():
            primary_models = config.get('primary', [])
              # Find first available model
            selected_model = None
            for model in primary_models:
                provider, model_name = model.split('/', 1)
                if provider in self.active_providers:
                    selected_model = model
                    break
            
            if selected_model:
                self.agent_model_map[agent_role] = selected_model
                self.logger.info(f"{agent_role} -> {selected_model}")
            else:
                self.logger.warning(f"No model available for {agent_role}")

    async def generate_response(self, agent_role: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using appropriate model for agent role"""
        
        # Map descriptive role names to config keys
        role_mapping = {
            'System Architect': 'architect',
            'Architect Agent': 'architect', 
            'architect': 'architect',
            'Backend Developer': 'backend_dev',
            'Backend Agent': 'backend_dev',
            'backend': 'backend_dev',
            'Frontend Developer': 'frontend_dev', 
            'Frontend Agent': 'frontend_dev',
            'frontend': 'frontend_dev',
            'QA Analyst': 'qa_analyst',
            'QA Agent': 'qa_analyst',
            'qa': 'qa_analyst',
            'Project Orchestrator': 'orchestrator',
            'Orchestrator Agent': 'orchestrator',
            'orchestrator': 'orchestrator'
        }
        
        # Get the config key for this role
        config_key = role_mapping.get(agent_role, agent_role)
        
        # Get model for agent role
        model = self.agent_model_map.get(config_key)
        if not model:
            self.logger.warning(f"No model found for role '{agent_role}' (mapped to '{config_key}')")
            return await self._generate_fallback_response(prompt)
        
        provider, model_name = model.split('/', 1)
        
        try:
            if provider == "lmstudio":
                return await self._generate_lmstudio_response(model_name, prompt, **kwargs)
            elif provider == "ollama":
                return await self._generate_ollama_response(model_name, prompt, **kwargs)
            else:
                return await self._generate_fallback_response(prompt)
                
        except Exception as e:
            self.logger.error(f"Error generating response with {model}: {e}")
            return await self._generate_fallback_response(prompt)

    async def _generate_lmstudio_response(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using LM Studio with OpenAI client"""
        if not OPENAI_AVAILABLE:
            return await self._generate_fallback_response(prompt)
        
        try:            # Create LM Studio client with timeout
            client = OpenAI(
                base_url="http://localhost:1234/v1",
                api_key="not-needed",
                timeout=30.0  # 30 second timeout
            )
            
            # Optimize generation settings for faster responses
            max_tokens = min(kwargs.get('max_tokens', 512), 1024)  # Limit max tokens
            temperature = kwargs.get('temperature', 0.3)  # Lower temperature for faster generation
            
            # Run the synchronous OpenAI call in a thread pool with timeout
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,                        max_tokens=max_tokens,
                        stream=False  # Ensure no streaming
                    )
                ),
                timeout=25.0  # 25 second async timeout
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": model,
                "provider": "lmstudio", 
                "success": True
            }
            
        except asyncio.TimeoutError:
            self.logger.error(f"LM Studio timeout for model {model}")
            return await self._generate_fallback_response(prompt)
        except Exception as e:
            self.logger.error(f"LM Studio error: {e}")
            return await self._generate_fallback_response(prompt)

    async def _generate_ollama_response(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using Ollama direct API"""
        try:
            base_url = self.active_providers['ollama']['base_url']
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', 0.7),
                    "num_predict": kwargs.get('max_tokens', 2048)
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{base_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "content": data.get("response", ""),
                            "model": model,
                            "provider": "ollama",
                            "success": True
                        }
                    else:
                        raise Exception(f"Ollama API error: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Ollama error: {e}")
            return await self._generate_fallback_response(prompt)

    async def _generate_fallback_response(self, prompt: str) -> Dict[str, Any]:
        """Generate a fallback response when no models are available"""
        self.logger.warning("Using fallback response - no models available")
        
        # Analyze prompt for intelligent fallback
        if "plan" in prompt.lower() or "design" in prompt.lower():
            content = f"""# Project Planning Response

## Overview
This is a structured planning response for: {prompt[:100]}...

## Key Components
1. **Requirements Analysis** - Analyze project needs
2. **System Architecture** - Design scalable solution
3. **Implementation Plan** - Step-by-step approach
4. **Quality Assurance** - Testing and validation

## Next Steps
- Detailed technical specification
- Resource allocation
- Timeline development
- Risk assessment

*Note: This is a fallback response. Real AI model integration needed for detailed content.*"""
        elif "code" in prompt.lower() or "implement" in prompt.lower():
            content = f"""# Implementation Response

```python
# TODO: Implement functionality for: {prompt[:100]}...
class ProjectImplementation:
    def __init__(self):
        self.status = "planned"
    
    def execute(self):
        # Implementation details needed
        pass
```

**Notes:** 
- Real AI model needed for actual code generation
- This is a placeholder structure
- LM Studio connection recommended for code tasks"""
        else:
            content = f"""# AI Response

**Input:** {prompt[:100]}...

**Analysis:** This request requires AI model processing for optimal results.

**Recommendation:** 
- Ensure LM Studio is running on port 1234
- Verify model is loaded and available
- Check network connectivity

**Fallback Status:** Active - Real model integration needed"""
        
        return {
            "content": content,
            "model": "fallback",
            "provider": "system",
            "success": False
        }

    def _get_fallback_config(self):
        """Get fallback configuration"""
        return {
            "providers": {
                "lmstudio": {
                    "base_url": "http://localhost:1234",
                    "enabled": True
                },
                "ollama": {
                    "base_url": "http://127.0.0.1:11434",
                    "enabled": True
                }
            },
            "agent_assignments": {
                "architect": {"primary": ["lmstudio/mistral-small-3.1-24b-instruct-2503"]},
                "backend": {"primary": ["lmstudio/codellama-7b-instruct"]},
                "frontend": {"primary": ["lmstudio/codellama-7b-instruct"]},
                "orchestrator": {"primary": ["lmstudio/mistral-small-3.1-24b-instruct-2503"]},
                "qa": {"primary": ["lmstudio/mistral-small-3.1-24b-instruct-2503"]}
            }
        }
