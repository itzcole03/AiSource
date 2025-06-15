#!/usr/bin/env python3
"""
Enhanced LLM Manager with Intelligent Model Selection
Dynamically discovers models and intelligently selects the best one for each task.
"""

import asyncio
import aiohttp
import yaml
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

# Try to import OpenAI client
OPENAI_AVAILABLE = False
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    pass

from intelligent_model_selector import IntelligentModelSelector

class IntelligentLLMManager:
    """Enhanced LLM Manager with intelligent model selection"""
    
    def __init__(self, config_path: str = "config/models_config.yaml"):
        self.logger = logging.getLogger("IntelligentLLM")
        self.config_path = config_path
        self.config = {}
        self.active_providers = {}
        self.model_selector = IntelligentModelSelector()
        self.performance_cache = {}
        
    async def initialize(self):
        """Initialize with intelligent model discovery"""
        self.logger.info("🚀 Initializing Intelligent LLM Manager...")
        
        # Load configuration
        await self._load_config()
        
        # Discover available models dynamically
        await self._discover_and_analyze_models()
        
        # Test connectivity
        await self._test_provider_connectivity()
        
        self.logger.info("✅ Intelligent LLM Manager ready with dynamic model selection")
        
    async def _load_config(self):
        """Load base configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            self.logger.info(f"📁 Loaded config from {self.config_path}")
        except Exception as e:
            self.logger.warning(f"⚠️ Config load failed: {e}")
            self.config = {'providers': {}}
    
    async def _discover_and_analyze_models(self):
        """Discover and analyze all available models"""
        self.logger.info("🔍 Discovering available models...")
        
        models = await self.model_selector.discover_all_models()
        
        # Set up active providers based on discovered models
        if models.get('lmstudio'):
            self.active_providers['lmstudio'] = {
                'base_url': 'http://localhost:1234',
                'models': models['lmstudio']
            }
            
        if models.get('ollama'):
            self.active_providers['ollama'] = {
                'base_url': 'http://127.0.0.1:11434', 
                'models': models['ollama']
            }
        
        self.logger.info(f"🎯 Active providers: {list(self.active_providers.keys())}")
    
    async def _test_provider_connectivity(self):
        """Test connectivity to all providers"""
        for provider_name, config in self.active_providers.items():
            try:
                if provider_name == "lmstudio":
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{config['base_url']}/v1/models", timeout=5) as response:
                            if response.status == 200:
                                self.logger.info(f"✅ {provider_name} connectivity verified")
                            else:
                                self.logger.warning(f"⚠️ {provider_name} responded with {response.status}")
                                
                elif provider_name == "ollama":
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f"{config['base_url']}/api/tags", timeout=5) as response:
                            if response.status == 200:
                                self.logger.info(f"✅ {provider_name} connectivity verified")
                            else:
                                self.logger.warning(f"⚠️ {provider_name} responded with {response.status}")
                                
            except Exception as e:
                self.logger.warning(f"⚠️ {provider_name} connectivity failed: {e}")
    
    async def generate_response(self, agent_role: str, prompt: str, task_type: str = "general_tasks", priority: str = "balanced", **kwargs) -> Dict[str, Any]:
        """Generate response using intelligently selected model"""
        
        # Intelligently select the best model for this specific task
        selected_model, model_info = await self.model_selector.select_best_model(
            agent_role=agent_role,
            task_type=task_type, 
            priority=priority
        )
        
        if not selected_model:
            self.logger.warning(f"❌ No suitable model found for {agent_role} doing {task_type}")
            return await self._generate_fallback_response(prompt)
        
        provider, model_name = selected_model.split('/', 1)
        
        # Log the intelligent selection
        self.logger.info(f"🧠 Intelligent selection: {agent_role} → {selected_model}")
        self.logger.debug(f"📝 Reasoning: {model_info.get('reasoning', '')}")
        
        # Track performance for future optimization
        start_time = datetime.now()
        
        try:
            if provider == "lmstudio":
                response = await self._generate_lmstudio_response(model_name, prompt, **kwargs)
            elif provider == "ollama":
                response = await self._generate_ollama_response(model_name, prompt, **kwargs)
            else:
                return await self._generate_fallback_response(prompt)
            
            # Record performance metrics
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            await self._record_performance(selected_model, duration, response.get('success', False))
            
            # Add selection metadata to response
            response['selected_model'] = selected_model
            response['selection_reasoning'] = model_info.get('reasoning', '')
            response['response_time'] = duration
            
            return response
            
        except Exception as e:
            self.logger.error(f"❌ Error with {selected_model}: {e}")
            return await self._generate_fallback_response(prompt)
    
    async def _generate_lmstudio_response(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using LM Studio with optimized settings"""
        if not OPENAI_AVAILABLE:
            return await self._generate_fallback_response(prompt)
        
        try:
            # Create LM Studio client with timeout
            client = OpenAI(
                base_url="http://localhost:1234/v1",
                api_key="not-needed",
                timeout=30.0
            )
            
            # Optimize generation settings based on task
            max_tokens = min(kwargs.get('max_tokens', 512), 1024)
            temperature = kwargs.get('temperature', 0.3)
            
            # Run with timeout
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=False
                    )
                ),
                timeout=25.0
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": model,
                "provider": "lmstudio",
                "success": True
            }
            
        except asyncio.TimeoutError:
            self.logger.error(f"⏱️ LM Studio timeout for model {model}")
            return await self._generate_fallback_response(prompt)
        except Exception as e:
            self.logger.error(f"❌ LM Studio error: {e}")
            return await self._generate_fallback_response(prompt)
    
    async def _generate_ollama_response(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response using Ollama with optimized settings"""
        try:
            base_url = self.active_providers['ollama']['base_url']
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', 0.3),
                    "num_predict": min(kwargs.get('max_tokens', 512), 1024)
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{base_url}/api/generate", 
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=25)
                ) as response:
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
                        
        except asyncio.TimeoutError:
            self.logger.error(f"⏱️ Ollama timeout for model {model}")
            return await self._generate_fallback_response(prompt)
        except Exception as e:
            self.logger.error(f"❌ Ollama error: {e}")
            return await self._generate_fallback_response(prompt)
    
    async def _generate_fallback_response(self, prompt: str) -> Dict[str, Any]:
        """Generate fallback response when models fail"""
        return {
            "content": f"""# AI Response

**Input:** {prompt[:100]}...

**Analysis:** This request requires AI model processing for optimal results.

**Recommendation:** 
- Ensure LM Studio or Ollama is running with loaded models
- Verify model compatibility and performance
- Check network connectivity

**Fallback Status:** Active - Real model integration needed""",
            "model": "fallback",
            "provider": "system",
            "success": False
        }
    
    async def _record_performance(self, model: str, duration: float, success: bool):
        """Record performance metrics for model optimization"""
        if model not in self.performance_cache:
            self.performance_cache[model] = {
                'total_calls': 0,
                'successful_calls': 0,
                'total_time': 0.0,
                'average_time': 0.0
            }
        
        metrics = self.performance_cache[model]
        metrics['total_calls'] += 1
        if success:
            metrics['successful_calls'] += 1
        metrics['total_time'] += duration
        metrics['average_time'] = metrics['total_time'] / metrics['total_calls']
    
    async def get_intelligent_status_report(self) -> Dict[str, Any]:
        """Get comprehensive intelligent status report"""
        report = await self.model_selector.get_model_status_report()
        
        report['performance_metrics'] = self.performance_cache
        report['active_providers'] = list(self.active_providers.keys())
        
        return report
    
    async def optimize_model_selection(self):
        """Optimize model selection based on performance data"""
        self.logger.info("🔧 Optimizing model selection based on performance...")
        
        # Update model selector with performance data
        for model, metrics in self.performance_cache.items():
            success_rate = metrics['successful_calls'] / max(metrics['total_calls'], 1)
            avg_time = metrics['average_time']
            
            # Update model capabilities with real performance data
            if model in self.model_selector.model_capabilities:
                capabilities = self.model_selector.model_capabilities[model]
                
                # Adjust speed score based on actual performance
                if avg_time < 2.0:
                    capabilities['speed_score'] = 5
                elif avg_time < 5.0:
                    capabilities['speed_score'] = 4
                elif avg_time < 10.0:
                    capabilities['speed_score'] = 3
                else:
                    capabilities['speed_score'] = 2
                
                # Adjust reliability based on success rate
                capabilities['reliability_score'] = int(success_rate * 5)
        
        self.logger.info("✅ Model selection optimization complete")

# Usage example and test
async def test_intelligent_llm():
    """Test the intelligent LLM manager"""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    manager = IntelligentLLMManager()
    await manager.initialize()
    
    # Test different agent scenarios
    test_scenarios = [
        {
            'agent_role': 'architect',
            'prompt': 'Design a microservices architecture for an e-commerce platform',
            'task_type': 'system_design',
            'priority': 'quality'
        },
        {
            'agent_role': 'backend_dev',
            'prompt': 'Write a Python function to validate user input',
            'task_type': 'code_generation',
            'priority': 'speed'
        },
        {
            'agent_role': 'orchestrator',
            'prompt': 'Create a project timeline for web app development',
            'task_type': 'planning',
            'priority': 'balanced'
        }
    ]
    
    print(f"\n🧪 TESTING INTELLIGENT MODEL SELECTION")
    print("=" * 60)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- Test {i}: {scenario['agent_role'].upper()} ---")
        print(f"Task: {scenario['task_type']} ({scenario['priority']} priority)")
        print(f"Prompt: {scenario['prompt'][:60]}...")
        
        response = await manager.generate_response(**scenario)
        
        print(f"Selected Model: {response.get('selected_model', 'unknown')}")
        print(f"Success: {response.get('success', False)}")
        print(f"Response Time: {response.get('response_time', 0):.2f}s")
        print(f"Content Length: {len(response.get('content', ''))}")
        print(f"Reasoning: {response.get('selection_reasoning', '')}")
        
        if response.get('success'):
            print(f"Content Preview: {response.get('content', '')[:100]}...")
        
    # Get status report
    print(f"\n📊 INTELLIGENT STATUS REPORT")
    print("=" * 60)
    
    report = await manager.get_intelligent_status_report()
    print(f"Total Models: {report.get('total_models', 0)}")
    print(f"Active Providers: {report.get('active_providers', [])}")
    
    print(f"\nRecommendations:")
    for role, rec in report.get('recommendations', {}).items():
        print(f"  {role}: {rec.get('model', 'none')}")

if __name__ == "__main__":
    asyncio.run(test_intelligent_llm())
