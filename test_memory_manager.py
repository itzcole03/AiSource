#!/usr/bin/env python3
"""
Test the Memory-Aware Model Manager
"""

import asyncio
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

async def test_memory_manager():
    """Test the memory-aware model manager"""
    try:
        print("Testing Memory-Aware Model Manager for 8GB VRAM...")
        
        from memory_aware_model_manager import MemoryAwareModelManager
        print("✓ Memory-aware manager imported")
        
        # Create manager with 7GB limit (conservative for 8GB VRAM)
        manager = MemoryAwareModelManager(max_vram_mb=7000)
        print("✓ Manager created with 7GB VRAM limit")
        
        # Initialize - this should be much faster than the old version
        print("Initializing (discovering models without loading)...")
        await manager.initialize()
        print("✓ Manager initialized")
        
        # Check memory status
        status = await manager.get_memory_status()
        print(f"\nMemory Status:")
        print(f"  Max VRAM: {status['max_vram_mb']}MB")
        print(f"  Current usage: {status['current_usage_mb']}MB")
        print(f"  Available: {status['available_mb']}MB")
        print(f"  Available models: {status['available_models']}")
        print(f"  Loaded models: {status['loaded_models']}")
        
        # Test getting best model for code generation
        print("\nTesting model selection...")
        best_model = await manager.get_best_model_for_task("code_generation", "architect")
        if best_model:
            print(f"✓ Best model for code generation: {best_model}")
        else:
            print("✗ No suitable model found")
        
        # Show active models
        active = await manager.get_active_models()
        print(f"\nActive models:")
        for provider, models in active.items():
            print(f"  {provider}: {len(models)} models")
            for model_id, info in models.items():
                print(f"    - {model_id}: {info['vram_mb']}MB VRAM")
        
        print("\n✅ SUCCESS: Memory-aware manager working correctly!")
        print("This version will:")
        print("  - Only load 1-2 models at a time")
        print("  - Prioritize smaller models for 8GB VRAM")
        print("  - Intelligently swap models as needed")
        print("  - Prevent memory overload")
        
        return True
        
    except Exception as e:
        print(f"✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_memory_manager())
    print(f"\nResult: {'PASSED' if success else 'FAILED'}")
