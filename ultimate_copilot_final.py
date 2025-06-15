#!/usr/bin/env python3
"""
Ultimate Copilot - Final Integration

This is the complete Ultimate Copilot system with all enhanced features:
- Intelligent multi-provider model management
- Advanced agent orchestration
- Persistent cross-workspace learning
- Real-time system monitoring
- Comprehensive completion system
"""

import asyncio
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

class UltimateCopilotSystem:
    """
    The complete Ultimate Copilot system integrating all components
    """
    
    def __init__(self, config_file: str = "ultimate_copilot_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        
        # Core components
        self.memory_manager = None
        self.unified_intelligence = None
        self.orchestrator = None
        self.completion_system = None
        self.persistent_intelligence = None
        
        # System state
        self.is_initialized = False
        self.startup_time = None
        self.stats = {
            "total_completions": 0,
            "successful_completions": 0,
            "total_workflows": 0,
            "models_loaded": 0,
            "agents_active": 0
        }
        
        # Setup logging
        self.logger = logging.getLogger("UltimateCopilot")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def _load_config(self) -> Dict:
        """Load system configuration"""
        default_config = {
            "providers": {
                "lmstudio": {
                    "enabled": True,
                    "endpoint": "http://localhost:1234",
                    "priority": 1
                },
                "ollama": {
                    "enabled": True,
                    "endpoint": "http://localhost:11434",
                    "priority": 2
                },
                "vllm": {
                    "enabled": True,
                    "endpoint": "http://localhost:8000",
                    "priority": 3
                }
            },
            "memory": {
                "max_vram_mb": 7168,  # 7GB for 8GB cards
                "safety_margin_mb": 512
            },
            "agents": {
                "max_concurrent_workflows": 3,
                "default_timeout": 300
            },
            "completion": {
                "default_quality": "standard",
                "enable_learning": True,
                "save_history": True
            },
            "monitoring": {
                "refresh_interval": 5,
                "save_reports": True
            }
        }
        
        config_path = Path(self.config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                default_config.update(config)
                return default_config
            except Exception as e:
                self.logger.warning(f"Failed to load config, using defaults: {e}")
                return default_config
        else:
            # Save default config
            try:
                with open(config_path, 'w') as f:
                    json.dump(default_config, f, indent=2)
                self.logger.info(f"Created default config: {config_path}")
            except Exception as e:
                self.logger.warning(f"Failed to save default config: {e}")
            
            return default_config
    
    async def initialize(self) -> bool:
        """Initialize the complete Ultimate Copilot system"""
        try:
            self.logger.info("="*60)
            self.logger.info("INITIALIZING ULTIMATE COPILOT SYSTEM")
            self.logger.info("="*60)
            
            self.startup_time = datetime.now()
            
            # Initialize memory manager
            self.logger.info("Initializing Memory Manager...")
            from fixed_memory_manager import MemoryAwareModelManager
            self.memory_manager = MemoryAwareModelManager()
            await self.memory_manager.initialize()
            self.logger.info("✓ Memory Manager initialized")
            
            # Initialize unified intelligence
            self.logger.info("Initializing Unified Model Intelligence...")
            from unified_model_intelligence import UnifiedModelIntelligence
            self.unified_intelligence = UnifiedModelIntelligence(self.memory_manager)
            self.logger.info("✓ Unified Model Intelligence initialized")
            
            # Initialize persistent intelligence
            self.logger.info("Initializing Persistent Intelligence...")
            from persistent_agent_intelligence import PersistentAgentIntelligence
            self.persistent_intelligence = PersistentAgentIntelligence()
            self.logger.info("✓ Persistent Intelligence initialized")
            
            # Initialize orchestrator
            self.logger.info("Initializing Agent Orchestrator...")
            from intelligent_agent_orchestrator_fixed import IntelligentAgentOrchestrator
            self.orchestrator = IntelligentAgentOrchestrator()
            await self.orchestrator.initialize()
            self.logger.info("✓ Agent Orchestrator initialized")
            
            # Initialize completion system
            self.logger.info("Initializing Completion System...")
            from ultimate_ai_completion import UltimateAICompletion
            self.completion_system = UltimateAICompletion()
            await self.completion_system.initialize()
            self.logger.info("✓ Completion System initialized")
            
            # Update stats
            await self._update_stats()
            
            self.is_initialized = True
            initialization_time = (datetime.now() - self.startup_time).total_seconds()
            
            self.logger.info("="*60)
            self.logger.info("ULTIMATE COPILOT SYSTEM READY")
            self.logger.info(f"Initialization completed in {initialization_time:.1f} seconds")
            self.logger.info(f"Models available: {self.stats['models_loaded']}")
            self.logger.info(f"Agents active: {self.stats['agents_active']}")
            self.logger.info("="*60)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Ultimate Copilot system: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _update_stats(self):
        """Update system statistics"""
        try:
            # Model stats
            if self.memory_manager:
                memory_status = await self.memory_manager.get_memory_status()
                self.stats['models_loaded'] = len(memory_status.get('loaded_models', []))
            
            # Agent stats
            if self.orchestrator:
                self.stats['agents_active'] = len(self.orchestrator.agent_pool)
            
            # Completion stats
            if self.completion_system:
                comp_status = await self.completion_system.get_system_status()
                comp_metrics = comp_status.get('completion_system', {}).get('performance_metrics', {})
                self.stats['total_completions'] = comp_metrics.get('total_completions', 0)
                self.stats['successful_completions'] = comp_metrics.get('successful_completions', 0)
            
            # Workflow stats
            if self.orchestrator:
                self.stats['total_workflows'] = len(self.orchestrator.execution_results)
                
        except Exception as e:
            self.logger.warning(f"Failed to update stats: {e}")
    
    async def run_completion(self, prompt: str, completion_type: str = "code", 
                           quality_level: str = "standard", use_agents: bool = True) -> Dict:
        """Run a completion request"""
        if not self.is_initialized:
            raise RuntimeError("System not initialized")
        
        try:
            from ultimate_ai_completion import CompletionRequest, CompletionType, QualityLevel
            
            # Map string types to enums
            type_map = {
                "code": CompletionType.CODE,
                "documentation": CompletionType.DOCUMENTATION,
                "analysis": CompletionType.ANALYSIS,
                "research": CompletionType.RESEARCH,
                "planning": CompletionType.PLANNING,
                "optimization": CompletionType.OPTIMIZATION,
                "testing": CompletionType.TESTING,
                "review": CompletionType.REVIEW
            }
            
            quality_map = {
                "draft": QualityLevel.DRAFT,
                "standard": QualityLevel.STANDARD,
                "high": QualityLevel.HIGH,
                "premium": QualityLevel.PREMIUM
            }
            
            request_id = f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            request = CompletionRequest(
                request_id=request_id,
                completion_type=type_map.get(completion_type, CompletionType.CODE),
                prompt=prompt,
                quality_level=quality_map.get(quality_level, QualityLevel.STANDARD),
                use_agents=use_agents
            )
            
            response = await self.completion_system.complete(request)
            
            return {
                "success": response.success,
                "content": response.content,
                "quality_score": response.quality_score,
                "processing_time": response.processing_time,
                "model_used": response.model_used,
                "agent_used": response.agent_used,
                "error": response.error
            }
            
        except Exception as e:
            self.logger.error(f"Completion failed: {e}")
            return {
                "success": False,
                "content": "",
                "error": str(e)
            }    async def run_workflow(self, workflow_type: str = "development", 
                          context: Optional[Dict] = None) -> Dict:
        """Run a workflow"""
        if not self.is_initialized:
            raise RuntimeError("System not initialized")
        
        try:
            if self.orchestrator:
                workflow = await self.orchestrator.create_workflow_from_template(
                    workflow_type, context or {}
                )
                
                results = await self.orchestrator.execute_workflow(workflow)
                
                success_count = sum(1 for r in results if r.success)
                
                return {
                    "success": success_count > 0,
                    "workflow_id": workflow.workflow_id,
                    "total_tasks": len(results),
                    "successful_tasks": success_count,
                    "results": [
                        {
                            "task_id": r.task_id,
                            "success": r.success,
                            "duration": (r.end_time - r.start_time).total_seconds(),
                            "agent": r.agent_id,
                            "model": r.model_used
                        }
                        for r in results
                    ]
                }
            else:
                raise RuntimeError("Orchestrator not available")
            
        except Exception as e:
            self.logger.error(f"Workflow execution failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        if not self.is_initialized:
            return {"status": "not_initialized"}
        
        try:
            await self._update_stats()
            
            # Get component statuses
            memory_status = await self.memory_manager.get_memory_status()
            ui_status = await self.unified_intelligence.get_system_status()
            comp_status = await self.completion_system.get_system_status()
            
            uptime_seconds = (datetime.now() - self.startup_time).total_seconds()
            
            return {
                "status": "ready",
                "uptime_seconds": uptime_seconds,
                "initialization_time": self.startup_time.isoformat(),
                "stats": self.stats,
                "memory": memory_status,
                "intelligence": ui_status,
                "completion": comp_status["completion_system"],
                "orchestrator": {
                    "active_workflows": len(self.orchestrator.active_workflows),
                    "agent_pool_size": len(self.orchestrator.agent_pool)
                }
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {"status": "error", "error": str(e)}
    
    async def run_interactive_demo(self):
        """Run an interactive demonstration"""
        print("\n" + "="*60)
        print("ULTIMATE COPILOT - INTERACTIVE DEMO")
        print("="*60)
        
        while True:
            try:
                print("\nAvailable commands:")
                print("  1. Run completion")
                print("  2. Run workflow")
                print("  3. Show system status")
                print("  4. Show models")
                print("  5. Test all components")
                print("  6. Exit")
                
                choice = input("\nEnter choice (1-6): ").strip()
                
                if choice == "1":
                    await self._demo_completion()
                elif choice == "2":
                    await self._demo_workflow()
                elif choice == "3":
                    await self._demo_status()
                elif choice == "4":
                    await self._demo_models()
                elif choice == "5":
                    await self._demo_all_components()
                elif choice == "6":
                    break
                else:
                    print("Invalid choice")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
        
        print("\nDemo ended.")
    
    async def _demo_completion(self):
        """Demo completion functionality"""
        print("\n--- Completion Demo ---")
        prompt = input("Enter prompt: ").strip()
        if not prompt:
            return
        
        completion_type = input("Type (code/docs/analysis) [code]: ").strip() or "code"
        quality = input("Quality (draft/standard/high/premium) [standard]: ").strip() or "standard"
        
        print(f"\nRunning completion...")
        result = await self.run_completion(prompt, completion_type, quality)
        
        if result["success"]:
            print(f"✓ Success (Quality: {result['quality_score']:.1f}/10, Time: {result['processing_time']:.1f}s)")
            print(f"Model: {result['model_used']}, Agent: {result['agent_used']}")
            print(f"\nContent:\n{result['content'][:500]}{'...' if len(result['content']) > 500 else ''}")
        else:
            print(f"✗ Failed: {result['error']}")
    
    async def _demo_workflow(self):
        """Demo workflow functionality"""
        print("\n--- Workflow Demo ---")
        workflow_type = input("Workflow type (development/research) [development]: ").strip() or "development"
        
        print(f"\nRunning {workflow_type} workflow...")
        result = await self.run_workflow(workflow_type)
        
        if result["success"]:
            print(f"✓ Workflow completed: {result['successful_tasks']}/{result['total_tasks']} tasks successful")
            for task_result in result["results"]:
                status = "✓" if task_result["success"] else "✗"
                print(f"  {status} {task_result['task_id']} ({task_result['duration']:.1f}s)")
        else:
            print(f"✗ Workflow failed: {result['error']}")
    
    async def _demo_status(self):
        """Demo system status"""
        print("\n--- System Status ---")
        status = await self.get_system_status()
        
        print(f"Status: {status['status']}")
        if status['status'] == 'ready':
            print(f"Uptime: {status['uptime_seconds']:.0f} seconds")
            print(f"Models loaded: {status['stats']['models_loaded']}")
            print(f"Agents active: {status['stats']['agents_active']}")
            print(f"Total completions: {status['stats']['total_completions']}")
            print(f"VRAM usage: {status['memory']['current_usage_mb']}MB / {status['memory']['max_vram_mb']}MB")
    
    async def _demo_models(self):
        """Demo model information"""
        print("\n--- Available Models ---")
        memory_status = await self.memory_manager.get_memory_status()
        
        print(f"{'Provider':<12} {'Model':<30} {'Status':<10} {'VRAM':<8}")
        print("-" * 65)
        
        for model_key, model_info in memory_status['available_models'].items():
            status = "Loaded" if model_info.get('is_loaded', False) else "Available"
            model_id = model_info.get('model_id', model_key)
            if len(model_id) > 30:
                model_id = model_id[:27] + "..."
            
            print(f"{model_info.get('provider', 'Unknown'):<12} "
                  f"{model_id:<30} "
                  f"{status:<10} "
                  f"{model_info.get('estimated_vram_mb', 0)}MB")
    
    async def _demo_all_components(self):
        """Demo all components working together"""
        print("\n--- Complete System Test ---")
        
        # Test completion
        print("1. Testing completion system...")
        comp_result = await self.run_completion(
            "Create a Python function to calculate prime numbers",
            "code", "standard"
        )
        print(f"   Completion: {'✓' if comp_result['success'] else '✗'}")
        
        # Test workflow
        print("2. Testing workflow system...")
        workflow_result = await self.run_workflow("development")
        print(f"   Workflow: {'✓' if workflow_result['success'] else '✗'}")
        
        # Test status
        print("3. Testing system monitoring...")
        status = await self.get_system_status()
        print(f"   Status: {'✓' if status['status'] == 'ready' else '✗'}")
        
        print("\nSystem test completed!")

async def main():
    """Main entry point"""
    system = UltimateCopilotSystem()
    
    # Initialize
    success = await system.initialize()
    if not success:
        print("Failed to initialize Ultimate Copilot system")
        return
    
    # Run interactive demo
    await system.run_interactive_demo()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nUltimate Copilot stopped by user")
    except Exception as e:
        print(f"Ultimate Copilot error: {e}")
        import traceback
        traceback.print_exc()
