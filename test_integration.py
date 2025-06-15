#!/usr/bin/env python3
"""
Simple integration test for the Ultimate Copilot system
"""

import asyncio
import logging
import sys

# Setup simple logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger("IntegrationTest")

async def test_advanced_model_manager():
    """Test the advanced model manager"""
    logger.info("Testing Advanced Model Manager...")
    
    try:
        from advanced_model_manager import AdvancedModelManager
        
        manager = AdvancedModelManager()
        logger.info("✅ Advanced Model Manager created")
        
        # Initialize with timeout
        await asyncio.wait_for(manager.initialize(), timeout=30)
        logger.info("✅ Advanced Model Manager initialized")
        
        # Get active models
        active_models = await manager.get_active_models()
        logger.info(f"✅ Found {sum(len(models) for models in active_models.values())} active models")
        
        # Test best model selection
        best_model = await manager.get_best_model_for_task("code_generation", "architect")
        if best_model:
            logger.info(f"✅ Best model for code generation: {best_model}")
        else:
            logger.warning("⚠️ No best model found")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Advanced Model Manager test failed: {e}")
        return False

async def test_master_completion():
    """Test the master completion system"""
    logger.info("Testing Master Completion System...")
    
    try:
        from master_intelligent_completion import IntelligentAppCompleter
        
        completer = IntelligentAppCompleter()
        logger.info("✅ Intelligent App Completer created")
        
        # Test analysis
        analysis = await completer.analyze_current_state()
        completion_pct = analysis.get('overall_completion', 0)
        logger.info(f"✅ System analysis complete: {completion_pct:.1f}% completion")
        
        # Test gap identification
        gaps = await completer.identify_critical_gaps(analysis)
        logger.info(f"✅ Found {len(gaps)} critical gaps")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Master Completion test failed: {e}")
        return False

async def test_integration():
    """Test the full integration"""
    logger.info("Testing Full Integration...")
    
    try:
        from advanced_model_manager import AdvancedModelManager
        from master_intelligent_completion import IntelligentAppCompleter
        
        # Create components
        model_manager = AdvancedModelManager()
        app_completer = IntelligentAppCompleter()
        
        # Initialize model manager
        await asyncio.wait_for(model_manager.initialize(), timeout=30)
        logger.info("✅ Model manager ready")
        
        # Connect to app completer
        app_completer.model_manager = model_manager
        logger.info("✅ Components connected")
        
        # Test integrated workflow
        analysis = await app_completer.analyze_current_state()
        completion_pct = analysis.get('overall_completion', 0)
        
        active_models = await model_manager.get_active_models()
        total_models = sum(len(models) for models in active_models.values())
        
        logger.info(f"✅ Integration test complete:")
        logger.info(f"    - System completion: {completion_pct:.1f}%")
        logger.info(f"    - Active models: {total_models}")
        
        # Test model selection for a specific task
        best_model = await model_manager.get_best_model_for_task("code_generation", "architect")
        if best_model:
            logger.info(f"    - Best model available: {best_model}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    logger.info("🚀 Starting Ultimate Copilot Integration Tests")
    
    tests = [
        ("Advanced Model Manager", test_advanced_model_manager),
        ("Master Completion", test_master_completion),
        ("Full Integration", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name} Test")
        logger.info(f"{'='*50}")
        
        try:
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name} test PASSED")
            else:
                logger.error(f"❌ {test_name} test FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name} test ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST RESULTS SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! System is ready for production!")
    else:
        logger.warning("⚠️ Some tests failed. Check logs for details.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
