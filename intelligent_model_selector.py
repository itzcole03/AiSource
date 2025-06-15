#!/usr/bin/env python3
"""
Intelligent Model Discovery and Selection System
Dynamically discovers models from LM Studio and Ollama, then intelligently selects the best model for each task.
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re

class IntelligentModelSelector:
    """Intelligently discovers and selects optimal models for tasks"""
    
    def __init__(self):
        self.logger = logging.getLogger("ModelSelector")
        self.available_models = {}
        self.model_capabilities = {}
        self.performance_metrics = {}
        
    async def discover_all_models(self) -> Dict[str, List[Dict]]:
        """Discover all available models from all providers"""
        self.logger.info("🔍 Discovering available models...")
        
        discovered = {
            'lmstudio': [],
            'ollama': []
        }
        
        # Discover LM Studio models
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:1234/v1/models", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get('data', [])
                        discovered['lmstudio'] = models
                        self.logger.info(f"✅ LM Studio: {len(models)} models available")
                        for model in models:
                            self.logger.info(f"  📦 {model.get('id', 'unknown')}")
                    else:
                        self.logger.warning("⚠️ LM Studio not available")
        except Exception as e:
            self.logger.warning(f"⚠️ LM Studio connection failed: {e}")
        
        # Discover Ollama models
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://127.0.0.1:11434/api/tags", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get('models', [])
                        discovered['ollama'] = models
                        self.logger.info(f"✅ Ollama: {len(models)} models available")
                        for model in models:
                            self.logger.info(f"  📦 {model.get('name', 'unknown')}")
                    else:
                        self.logger.warning("⚠️ Ollama not available")
        except Exception as e:
            self.logger.warning(f"⚠️ Ollama connection failed: {e}")
        
        self.available_models = discovered
        await self._analyze_model_capabilities()
        return discovered
    
    async def _analyze_model_capabilities(self):
        """Analyze and categorize model capabilities"""
        self.logger.info("🧠 Analyzing model capabilities...")
        
        # LM Studio models
        for model in self.available_models.get('lmstudio', []):
            model_id = model.get('id', '')
            capabilities = self._infer_capabilities(model_id)
            self.model_capabilities[f"lmstudio/{model_id}"] = capabilities
        
        # Ollama models  
        for model in self.available_models.get('ollama', []):
            model_name = model.get('name', '')
            capabilities = self._infer_capabilities(model_name)
            self.model_capabilities[f"ollama/{model_name}"] = capabilities
    
    def _infer_capabilities(self, model_name: str) -> Dict[str, any]:
        """Infer model capabilities from name and size"""
        name_lower = model_name.lower()
        
        # Model type detection
        model_type = "general"
        if any(x in name_lower for x in ['code', 'llama', 'starcoder', 'wizardcoder']):
            model_type = "coding"
        elif any(x in name_lower for x in ['instruct', 'chat', 'assistant']):
            model_type = "conversational"
        elif any(x in name_lower for x in ['math', 'reasoning']):
            model_type = "analytical"
        
        # Size estimation (affects speed/quality trade-off)
        size_category = "medium"
        if any(x in name_lower for x in ['1b', '2b', '3b']):
            size_category = "small"  # Fast but lower quality
        elif any(x in name_lower for x in ['7b', '8b']):
            size_category = "medium"  # Good balance
        elif any(x in name_lower for x in ['13b', '20b', '24b', '70b']):
            size_category = "large"  # High quality but slower
        
        # Speed estimation
        speed_score = 3  # Default medium
        if size_category == "small":
            speed_score = 5  # Very fast
        elif size_category == "medium":
            speed_score = 3  # Good speed
        elif size_category == "large":
            speed_score = 1  # Slower
        
        # Quality estimation
        quality_score = 3  # Default medium
        if size_category == "small":
            quality_score = 2  # Lower quality
        elif size_category == "medium":
            quality_score = 3  # Good quality
        elif size_category == "large":
            quality_score = 5  # High quality
        
        return {
            'type': model_type,
            'size_category': size_category,
            'speed_score': speed_score,
            'quality_score': quality_score,
            'best_for': self._determine_best_tasks(model_type, size_category)
        }
    
    def _determine_best_tasks(self, model_type: str, size_category: str) -> List[str]:
        """Determine what tasks this model is best suited for"""
        tasks = []
        
        if model_type == "coding":
            tasks.extend(['code_generation', 'api_development', 'debugging', 'code_review'])
        elif model_type == "conversational":
            tasks.extend(['planning', 'documentation', 'user_interaction', 'requirements'])
        elif model_type == "analytical":
            tasks.extend(['architecture_design', 'system_analysis', 'testing_strategy'])
        else:  # general
            tasks.extend(['general_tasks', 'brainstorming', 'content_creation'])
        
        # Add speed-sensitive tasks for smaller models
        if size_category == "small":
            tasks.extend(['quick_responses', 'simple_tasks', 'prototyping'])
        elif size_category == "large":
            tasks.extend(['complex_analysis', 'detailed_planning', 'comprehensive_docs'])
            
        return tasks
    
    async def select_best_model(self, agent_role: str, task_type: str, priority: str = "balanced") -> Tuple[str, Dict]:
        """Intelligently select the best model for a specific agent and task"""
        
        if not self.model_capabilities:
            await self.discover_all_models()
        
        self.logger.info(f"🎯 Selecting model for {agent_role} doing {task_type} (priority: {priority})")
        
        # Score all available models
        model_scores = {}
        
        for model_key, capabilities in self.model_capabilities.items():
            score = self._score_model_for_task(model_key, capabilities, agent_role, task_type, priority)
            if score > 0:
                model_scores[model_key] = {
                    'score': score,
                    'capabilities': capabilities,
                    'reasoning': self._explain_model_choice(model_key, capabilities, agent_role, task_type)
                }
        
        if not model_scores:
            self.logger.warning("❌ No suitable models found")
            return None, {}
        
        # Select best model
        best_model = max(model_scores.keys(), key=lambda k: model_scores[k]['score'])
        best_info = model_scores[best_model]
        
        self.logger.info(f"🏆 Selected: {best_model}")
        self.logger.info(f"📝 Reason: {best_info['reasoning']}")
        
        return best_model, best_info
    
    def _score_model_for_task(self, model_key: str, capabilities: Dict, agent_role: str, task_type: str, priority: str) -> float:
        """Score how well a model fits a specific task"""
        score = 0.0
        
        # Base score from model type alignment
        if task_type in capabilities.get('best_for', []):
            score += 5.0
        elif capabilities.get('type') == 'general':
            score += 2.0
        
        # Agent role alignment
        role_preferences = {
            'architect': ['analytical', 'conversational'],
            'backend_dev': ['coding'],
            'frontend_dev': ['coding'],
            'qa_analyst': ['analytical', 'conversational'],
            'orchestrator': ['conversational', 'analytical']
        }
        
        if capabilities.get('type') in role_preferences.get(agent_role, []):
            score += 3.0
        
        # Priority adjustments
        if priority == "speed":
            score += capabilities.get('speed_score', 0) * 0.8
        elif priority == "quality":
            score += capabilities.get('quality_score', 0) * 0.8
        else:  # balanced
            score += (capabilities.get('speed_score', 0) + capabilities.get('quality_score', 0)) * 0.4
        
        # Provider preference (slight boost for LM Studio due to better OpenAI compatibility)
        if model_key.startswith('lmstudio/'):
            score += 0.5
        
        return score
    
    def _explain_model_choice(self, model_key: str, capabilities: Dict, agent_role: str, task_type: str) -> str:
        """Generate human-readable explanation for model choice"""
        provider, model_name = model_key.split('/', 1)
        
        reasons = []
        reasons.append(f"{model_name} is a {capabilities.get('size_category')} {capabilities.get('type')} model")
        
        if task_type in capabilities.get('best_for', []):
            reasons.append(f"optimized for {task_type}")
        
        reasons.append(f"speed score: {capabilities.get('speed_score')}/5")
        reasons.append(f"quality score: {capabilities.get('quality_score')}/5")
        
        return ", ".join(reasons)
    
    async def get_model_status_report(self) -> Dict:
        """Generate comprehensive model status report"""
        await self.discover_all_models()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_models': len(self.model_capabilities),
            'providers': {
                'lmstudio': len(self.available_models.get('lmstudio', [])),
                'ollama': len(self.available_models.get('ollama', []))
            },
            'model_types': {},
            'recommendations': {}
        }
        
        # Analyze model type distribution
        for model_key, caps in self.model_capabilities.items():
            model_type = caps.get('type', 'unknown')
            if model_type not in report['model_types']:
                report['model_types'][model_type] = []
            report['model_types'][model_type].append(model_key)
        
        # Generate role-specific recommendations
        roles = ['architect', 'backend_dev', 'frontend_dev', 'qa_analyst', 'orchestrator']
        for role in roles:
            best_model, info = await self.select_best_model(role, 'general_tasks', 'balanced')
            if best_model:
                report['recommendations'][role] = {
                    'model': best_model,
                    'reasoning': info.get('reasoning', '')
                }
        
        return report

# Test the intelligent model selector
async def main():
    """Test the intelligent model selection system"""
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
    
    selector = IntelligentModelSelector()
    
    print("🤖 INTELLIGENT MODEL DISCOVERY & SELECTION")
    print("=" * 50)
    
    # Discover all models
    models = await selector.discover_all_models()
    
    # Test model selection for different scenarios
    test_scenarios = [
        ('architect', 'system_design', 'quality'),
        ('backend_dev', 'api_development', 'speed'),
        ('frontend_dev', 'code_generation', 'balanced'),
        ('qa_analyst', 'testing_strategy', 'quality'),
        ('orchestrator', 'planning', 'balanced')
    ]
    
    print(f"\n🎯 INTELLIGENT MODEL SELECTION")
    print("=" * 50)
    
    for agent_role, task_type, priority in test_scenarios:
        print(f"\n--- {agent_role.upper()} for {task_type} ({priority}) ---")
        best_model, info = await selector.select_best_model(agent_role, task_type, priority)
        if best_model:
            print(f"✅ Selected: {best_model}")
            print(f"📊 Score: {info.get('score', 0):.2f}")
            print(f"📝 Reasoning: {info.get('reasoning', '')}")
        else:
            print("❌ No suitable model found")
    
    # Generate comprehensive report
    print(f"\n📊 MODEL STATUS REPORT")
    print("=" * 50)
    
    report = await selector.get_model_status_report()
    print(f"Total Models: {report['total_models']}")
    print(f"LM Studio: {report['providers']['lmstudio']}")
    print(f"Ollama: {report['providers']['ollama']}")
    
    print(f"\nModel Types:")
    for model_type, models in report['model_types'].items():
        print(f"  {model_type}: {len(models)} models")
    
    print(f"\nRecommendations:")
    for role, rec in report['recommendations'].items():
        print(f"  {role}: {rec['model']}")

if __name__ == "__main__":
    asyncio.run(main())
