#!/usr/bin/env python3
"""
Test vLLM integration with the fixed memory manager
"""
import asyncio
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.append(str(Path(__file__).parent))

async def test_vllm_integration():
    """Test vLLM integration"""
    print("Testing vLLM Integration with Fixed Memory Manager...")
    
    try:
        from fixed_memory_manager import MemoryAwareModelManager
          # Initialize the manager
        manager = MemoryAwareModelManager()
        print("✓ Fixed memory manager imported successfully")
        
        # Initialize and discover all models including vLLM
        await manager.initialize()
        print("✓ Model discovery completed")
        
        # Get current state
        memory_status = await manager.get_memory_status()
        active_models = await manager.get_active_models()
        
        print(f"\n--- System Summary ---")
        print(f"VRAM usage: {memory_status['used_vram_mb']}MB / {memory_status['max_vram_mb']}MB")
        print(f"Available models: {memory_status['total_available']}")
        print(f"Currently loaded models: {len(active_models)}")
        
        # Show models by provider
        print(f"\n--- Models by Provider ---")
        for provider in ['lmstudio', 'ollama', 'vllm']:
            provider_models = [m for m in manager.available_models.values() if m.provider == provider]
            loaded_count = sum(1 for m in provider_models if m.is_loaded)
            print(f"{provider.upper()}: {len(provider_models)} total, {loaded_count} loaded")
            
            for model in provider_models:
                status = "LOADED" if model.is_loaded else "available"
                print(f"  - {model.model_id} ({status})")
        
        print("\n✓ vLLM integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Error during vLLM integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_vllm_integration())
    sys.exit(0 if result else 1)
