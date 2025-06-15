"""
Real LLM Manager for connecting to local models
Supports Ollama, LM Studio, and vLLM with intelligent model routing
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

class RealLLMManager:
    """Real LLM Manager that connects to actual local models with optimized single-instance sharing"""
    
    # Class-level connection pool for sharing single vLLM instance
    _vllm_session = None
    _vllm_model_name = None
    _request_queue = asyncio.Queue()
    _processing_requests = False
    
    def __init__(self, config_path: str = "config/models_config.yaml"):
        self.logger = logging.getLogger("RealLLM")
        self.config_path = Path(config_path)
        self.config = {}
        self.active_providers = {}
        self.agent_model_map = {}
        self._session = None
        
        # OpenAI clients for different providers
        self.lmstudio_client = None
        self.ollama_client = None
        
    async def initialize(self):
        """Initialize the real LLM manager with single-instance optimization"""
        self.logger.info("Initializing Real LLM Manager for 8GB VRAM optimization...")
        
        # Create shared session for all requests
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        
        # Load configuration
        await self._load_config()
        
        # Test provider connections
        await self._test_providers()
        
        # Initialize OpenAI clients for compatible providers
        await self._setup_openai_clients()
        
        # Set up agent model assignments with single vLLM sharing
        await self._setup_agent_assignments_optimized()
        
        # Start request processing queue for vLLM
        if not RealLLMManager._processing_requests and "vllm" in self.active_providers:
            RealLLMManager._processing_requests = True
            asyncio.create_task(self._process_vllm_requests())
        
        self.logger.info("Real LLM Manager initialized with 8GB VRAM optimization")
        
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
        
        for provider_name, provider_config in providers.items():
            if not provider_config.get('enabled', False):
                continue
                
            base_url = provider_config.get('base_url')
            if await self._test_provider_connection(provider_name, base_url):
                self.active_providers[provider_name] = provider_config
                self.logger.info(f"{provider_name} available at {base_url}")
            else:
                self.logger.warning(f"{provider_name} not available at {base_url}")
    
    async def _test_provider_connection(self, provider: str, base_url: str) -> bool:
        """Test if a provider is available"""
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                if provider == "ollama":
                    async with session.get(f"{base_url}/api/tags") as response:
                        return response.status == 200
                elif provider in ["vllm", "lmstudio"]:
                    async with session.get(f"{base_url}/v1/models") as response:
                        return response.status == 200
                return False
        except Exception:
            return False
    
    async def _setup_agent_assignments(self):
        """Set up agent-to-model assignments"""
        assignments = self.config.get('agent_assignments', {})
        
        for agent_role, assignment in assignments.items():
            primary_models = assignment.get('primary', [])
            fallback_models = assignment.get('fallback', [])
            
            # Find first available model
            selected_model = None
            for model in primary_models + fallback_models:
                provider, model_name = model.split('/', 1) if '/' in model else ('ollama', model)
                if provider in self.active_providers:
                    selected_model = f"{provider}/{model_name}"
                    break
            
            if selected_model:
                self.agent_model_map[agent_role] = selected_model
                self.logger.info(f"{agent_role} -> {selected_model}")
            else:
                self.logger.warning(f"No model available for {agent_role}")
    
    async def _setup_agent_assignments_optimized(self):
        """Set up agent-to-model assignments optimized for single vLLM instance"""
        assignments = self.config.get('agent_assignments', {})
        
        # Check if vLLM is available - if so, all agents will share it
        if "vllm" in self.active_providers:
            # Get the vLLM model name for shared instance
            vllm_config = self.active_providers['vllm']
            available_models = vllm_config.get('models', [])
            if available_models:
                shared_model = f"vllm/{available_models[0]['id']}"
                RealLLMManager._vllm_model_name = available_models[0]['id']
                
                # Assign vLLM model to all agents for optimal sharing
                for agent_role in assignments.keys():
                    self.agent_model_map[agent_role] = shared_model
                    self.logger.info(f"🧬 {agent_role} → {shared_model} (shared instance)")
                return
        
        # Fallback to individual assignments if vLLM not available
        await self._setup_agent_assignments()
      async def _process_vllm_requests(self):
        """Process vLLM requests in queue to avoid overwhelming single instance"""
        while True:
            try:
                if not self._request_queue.empty():
                    request_data = await self._request_queue.get()
                    
                    # Process the request - using fallback for now
                    result = await self._generate_fallback_response(request_data['prompt'])
                    
                    # Set result in the future
                    request_data['future'].set_result(result)
                    
                    # Small delay to prevent overwhelming
                    await asyncio.sleep(0.1)
                else:
                    # Wait for new requests
                    await asyncio.sleep(0.5)
                    
            except Exception as e:
                self.logger.error(f"Error processing vLLM request queue: {e}")
                await asyncio.sleep(1)
    
    async def generate_response(self, agent_role: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using appropriate model for agent role"""
        
        # Get model for agent role
        model = self.agent_model_map.get(agent_role)
        if not model:
            return await self._generate_fallback_response(prompt)
        
        provider, model_name = model.split('/', 1)
        
        try:
            if provider == "ollama":
                return await self._generate_ollama_response_openai(model_name, prompt, **kwargs)
            elif provider == "lmstudio":
                return await self._generate_lmstudio_response_openai(model_name, prompt, **kwargs)
            elif provider == "vllm":
                return await self._generate_openai_compatible_response(
                    self.active_providers['vllm']['base_url'], model_name, prompt, **kwargs
                )
            else:
                return await self._generate_fallback_response(prompt)
                
        except Exception as e:
            self.logger.error(f"Error generating response with {model}: {e}")
            return await self._generate_fallback_response(prompt)
    
    async def _generate_ollama_response(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using Ollama"""
        base_url = self.active_providers['ollama']['base_url']
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get('temperature', 0.7),
                "top_p": kwargs.get('top_p', 0.9),
                "max_tokens": kwargs.get('max_tokens', 2048)
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
    
    async def _generate_openai_compatible_response(self, base_url: str, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using OpenAI-compatible API (vLLM, LM Studio)"""
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get('temperature', 0.7),
            "top_p": kwargs.get('top_p', 0.9),
            "max_tokens": kwargs.get('max_tokens', 2048)
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{base_url}/v1/chat/completions", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    content = data["choices"][0]["message"]["content"]
                    return {
                        "content": content,
                        "model": model,
                        "provider": "openai_compatible",
                        "success": True
                    }
                else:
                    raise Exception(f"API error: {response.status}")
    
    async def _generate_fallback_response(self, prompt: str) -> Dict[str, Any]:
        """Generate a fallback response when no models are available"""
        self.logger.warning("Using fallback response - no models available")
        
        # Analyze prompt for intelligent fallback
        if "code" in prompt.lower() or "function" in prompt.lower():
            content = "# TODO: Implement this functionality\n# Real model unavailable, needs implementation"
        elif "analyze" in prompt.lower():
            content = "Analysis requires local model - please ensure models are running"
        elif "create" in prompt.lower() or "generate" in prompt.lower():
            content = "Content generation requires local model - please start Ollama/LM Studio"
        else:
            content = "Local models not available. Please start your model servers."
        
        return {
            "content": content,
            "model": "fallback",
            "provider": "fallback",
            "success": False
        }
    
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get fallback configuration"""
        return {
            "providers": {
                "ollama": {
                    "base_url": "http://localhost:11434",
                    "enabled": True
                }
            },
            "agent_assignments": {
                "architect": {"primary": ["ollama/llama3"], "fallback": []},
                "backend_dev": {"primary": ["ollama/codellama"], "fallback": []},
                "frontend_dev": {"primary": ["ollama/codellama"], "fallback": []},
                "qa_analyst": {"primary": ["ollama/llama3"], "fallback": []},
                "orchestrator": {"primary": ["ollama/llama3"], "fallback": []}
            }
        }
    
    async def analyze_code(self, agent_role: str, code: str, task: str) -> Dict[str, Any]:
        """Analyze code and provide intelligent insights"""
        prompt = f"""
As a {agent_role}, analyze this code and provide specific, actionable insights for: {task}

Code:
```
{code}
```

Please provide:
1. Current analysis
2. Specific improvements needed
3. Concrete next steps
4. Priority recommendations

Be specific and actionable in your response.
"""
        
        return await self.generate_response(agent_role, prompt, temperature=0.3)
    
    async def generate_code(self, agent_role: str, requirements: str, context: str = "") -> Dict[str, Any]:
        """Generate code based on requirements"""
        prompt = f"""
As a {agent_role}, generate high-quality code for the following requirements:

Requirements: {requirements}

Context: {context}

Please provide:
1. Complete, working code
2. Clear comments explaining the logic
3. Error handling where appropriate
4. Any necessary imports or dependencies

Generate production-ready code that follows best practices.
"""
        
        return await self.generate_response(agent_role, prompt, temperature=0.2)
    
    async def make_decision(self, agent_role: str, situation: str, options: List[str]) -> Dict[str, Any]:
        """Make intelligent decisions based on situation and options"""
        options_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
        
        prompt = f"""
As a {agent_role}, analyze this situation and make the best decision:

Situation: {situation}

Available Options:
{options_text}

Please:
1. Analyze each option
2. Choose the best option and explain why
3. Provide the specific steps to implement your choice
4. Identify any potential risks or considerations

Make a clear, decisive recommendation.
"""
        
        return await self.generate_response(agent_role, prompt, temperature=0.4)
    
    async def shutdown(self):
        """Clean shutdown"""
        self.logger.info("🧊 Real LLM Manager shutdown complete")
    
    async def _setup_openai_clients(self):
        """Set up OpenAI clients for compatible providers"""
        if not OPENAI_AVAILABLE:
            self.logger.warning("OpenAI library not available - some providers may not work")
            return
              # Set up LM Studio client
        if "lmstudio" in self.active_providers and OPENAI_AVAILABLE:
            try:
                self.lmstudio_client = OpenAI(
                    base_url=self.active_providers["lmstudio"]["base_url"] + "/v1",
                    api_key="not-needed"  # LM Studio doesn't require API key
                )
                self.logger.info("LM Studio OpenAI client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize LM Studio client: {e}")
        
        # Set up Ollama client (if using OpenAI compatibility)
        if "ollama" in self.active_providers and OPENAI_AVAILABLE:
            try:
                # Ollama also supports OpenAI-compatible API
                self.ollama_client = OpenAI(
                    base_url=self.active_providers["ollama"]["base_url"] + "/v1",
                    api_key="not-needed"  # Ollama doesn't require API key
                )
                self.logger.info("Ollama OpenAI client initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Ollama client: {e}")
      async def _generate_lmstudio_response_openai(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using LM Studio with OpenAI client"""
        if not OPENAI_AVAILABLE:
            return await self._generate_fallback_response(prompt)
        
        try:
            # Create LM Studio client
            client = OpenAI(
                base_url="http://localhost:1234/v1",
                api_key="not-needed"
            )
            
            # Run the synchronous OpenAI call in a thread pool
            import asyncio
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=kwargs.get('temperature', 0.7),
                    top_p=kwargs.get('top_p', 0.9),
                    max_tokens=kwargs.get('max_tokens', 2048)
                )
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": model,
                "provider": "lmstudio",
                "success": True
            }
        except Exception as e:
            self.logger.error(f"LM Studio OpenAI client error: {e}")
            return await self._generate_fallback_response(prompt)

    async def _generate_ollama_response_openai(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using Ollama with direct API (OpenAI client not working)"""
        # For now, fallback to direct API since Ollama OpenAI compatibility seems to have issues
        return await self._generate_ollama_response(model, prompt, **kwargs)
