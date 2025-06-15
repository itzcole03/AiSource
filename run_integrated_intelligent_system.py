#!/usr/bin/env python3
"""
Integrated Intelligent System Runner
Combines advanced model management with intelligent agent workflows
"""

import asyncio
import logging
import os
import json
from datetime import datetime
from pathlib import Path

from memory_aware_model_manager import MemoryAwareModelManager
from master_intelligent_completion import IntelligentAppCompleter
from intelligent_llm_manager import IntelligentLLMManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/integrated_system.log')
    ]
)
logger = logging.getLogger("IntegratedSystem")

class IntegratedIntelligentSystem:
    """Integrated system combining all intelligent components"""
    
    def __init__(self):
        self.model_manager = None
        self.app_completer = None
        self.llm_manager = None
        self.status = "initializing"
        
    async def initialize(self):
        """Initialize all system components"""
        logger.info("Initializing Integrated Intelligent System...")
        
        try:
            # Initialize advanced model manager
            logger.info("Starting Advanced Model Manager...")
            self.model_manager = MemoryAwareModelManager(max_vram_mb=7000)  # 8GB VRAM system
            await self.model_manager.initialize()
            
            # Wait for initial model discovery
            await asyncio.sleep(5)
            
            # Initialize intelligent LLM manager
            logger.info("Starting Intelligent LLM Manager...")
            self.llm_manager = IntelligentLLMManager()
            await self.llm_manager.initialize()
            
            # Initialize app completer with model manager
            logger.info("Starting Intelligent App Completer...")
            self.app_completer = IntelligentAppCompleter()
            self.app_completer.model_manager = self.model_manager
            
            self.status = "ready"
            logger.info("All components initialized successfully!")
            
            # Show system status
            await self.show_system_status()
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            self.status = "error"
            raise
    
    async def show_system_status(self):
        """Display comprehensive system status"""
        logger.info("=== INTEGRATED SYSTEM STATUS ===")
        
        # Model Manager Status
        if self.model_manager:
            active_models = await self.model_manager.get_active_models()
            logger.info(f"Active Models: {len(active_models)}")
            
            for provider, models in active_models.items():
                logger.info(f"  {provider}: {len(models)} models")
                for model_id, status in models.items()[:3]:  # Show first 3
                    response_time = status.average_response_time
                    logger.info(f"    {model_id}: {response_time:.2f}s avg")
        
        # LLM Manager Status
        if self.llm_manager:
            logger.info(f"LLM Manager: {self.llm_manager.status}")
        
        # App Completer Status  
        if self.app_completer:
            logger.info(f"App Completer: Ready")
        
        logger.info("==============================")
    
    async def run_intelligent_completion(self):
        """Run the intelligent app completion workflow"""
        logger.info("Starting Intelligent App Completion...")
        
        try:
            # Analyze current state
            analysis = await self.app_completer.analyze_current_state()
            logger.info(f"System Analysis: {analysis.get('overall_completion', 0):.1f}% complete")
            
            # Identify gaps
            gaps = await self.app_completer.identify_critical_gaps(analysis)
            logger.info(f"Found {len(gaps)} critical gaps to address")
            
            # Address gaps using advanced model management
            for gap in gaps[:3]:  # Address top 3 priorities
                component = gap['component']
                missing_files = gap['missing_files']
                
                logger.info(f"Addressing {component} gaps...")
                
                for filename in missing_files[:2]:  # Limit for demo
                    logger.info(f"Creating {filename}...")
                    
                    # Get best model for this task
                    best_model = await self.model_manager.get_best_model_for_task(
                        "code_generation", 
                        "architect"
                    )
                    
                    if best_model:
                        logger.info(f"Using model {best_model} for {filename}")
                        
                        # Create the component
                        success = await self.app_completer.create_missing_component(
                            component, 
                            filename
                        )
                        
                        if success:
                            logger.info(f"Successfully created {filename}")
                        else:
                            logger.warning(f"Failed to create {filename}")
                    else:
                        logger.warning(f"No models available for {filename}")
            
            # Final status
            final_analysis = await self.app_completer.analyze_current_state()
            logger.info(f"Completion increased to {final_analysis.get('overall_completion', 0):.1f}%")
            
        except Exception as e:
            logger.error(f"Intelligent completion failed: {e}")
            raise
    
    async def run_model_performance_test(self):
        """Run comprehensive model performance testing"""
        logger.info("Running Model Performance Test...")
        
        try:
            # Get all active models
            active_models = await self.model_manager.get_active_models()
            
            test_prompts = [
                "Write a Python function to calculate factorial",
                "Explain the concept of machine learning in simple terms",
                "Create a REST API endpoint for user authentication"
            ]
            
            results = {}
            
            for provider, models in active_models.items():
                results[provider] = {}
                
                for model_id, status in list(models.items())[:2]:  # Test first 2 models
                    logger.info(f"Testing {provider}/{model_id}...")
                    
                    model_results = []
                    
                    for prompt in test_prompts:
                        start_time = asyncio.get_event_loop().time()
                        
                        try:
                            # Use model manager's internal method to test
                            response = await self.model_manager._test_model_responsiveness(
                                provider, model_id, prompt
                            )
                            
                            end_time = asyncio.get_event_loop().time()
                            response_time = end_time - start_time
                            
                            model_results.append({
                                "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                                "success": response is not None,
                                "response_time": response_time,
                                "response_length": len(str(response)) if response else 0
                            })
                            
                        except Exception as e:
                            model_results.append({
                                "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                                "success": False,
                                "error": str(e),
                                "response_time": 0
                            })
                    
                    results[provider][model_id] = model_results
                    
                    # Calculate average performance
                    successful_tests = [r for r in model_results if r["success"]]
                    if successful_tests:
                        avg_time = sum(r["response_time"] for r in successful_tests) / len(successful_tests)
                        success_rate = len(successful_tests) / len(model_results) * 100
                        
                        logger.info(f"  {model_id}: {success_rate:.1f}% success, {avg_time:.2f}s avg")
                    else:
                        logger.warning(f"  {model_id}: All tests failed")
            
            # Save results
            results_file = f"reports/model_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("reports", exist_ok=True)
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Performance test results saved to {results_file}")
            
        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            raise
    
    async def shutdown(self):
        """Graceful shutdown of all components"""
        logger.info("Shutting down Integrated System...")
        
        try:
            if self.model_manager:
                await self.model_manager.shutdown()
            
            if self.llm_manager:
                await self.llm_manager.shutdown()
            
            logger.info("System shutdown complete")
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")

async def main():
    """Main execution function"""
    system = IntegratedIntelligentSystem()
    
    try:
        # Initialize system
        await system.initialize()
        
        # Run performance test
        await system.run_model_performance_test()
        
        # Run intelligent completion
        await system.run_intelligent_completion()
        
        # Keep system running for monitoring
        logger.info("System running... Press Ctrl+C to stop")
        
        # Monitor for 30 seconds
        await asyncio.sleep(30)
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"System error: {e}")
    finally:
        await system.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
