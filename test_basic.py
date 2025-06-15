#!/usr/bin/env python3
"""
Simple test without Unicode characters
"""

import asyncio
import sys

async def test_basic():
    try:
        print("Testing imports...")
        from advanced_model_manager import AdvancedModelManager
        print("Advanced model manager imported")
        
        from master_intelligent_completion import IntelligentAppCompleter
        print("Master completion imported")
        
        print("Creating model manager...")
        manager = AdvancedModelManager()
        print("Model manager created")
        
        print("Testing initialization...")
        await manager.initialize()
        print("Model manager initialized successfully!")
        
        print("Getting active models...")
        active_models = await manager.get_active_models()
        
        total_models = sum(len(models) for models in active_models.values())
        print(f"Found {total_models} active models across all providers")
        
        for provider, models in active_models.items():
            print(f"  {provider}: {len(models)} models")
        
        print("Testing best model selection...")
        best_model = await manager.get_best_model_for_task("code_generation", "architect")
        if best_model:
            print(f"Best model for code generation: {best_model}")
        else:
            print("No best model found")
        
        print("SUCCESS: All tests passed!")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_basic())
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
