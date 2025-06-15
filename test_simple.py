print("Testing basic Python execution...")
print("Python is working correctly!")

try:
    import asyncio
    print("Asyncio imported successfully")
except Exception as e:
    print(f"Asyncio import failed: {e}")

try:
    from advanced_model_manager import AdvancedModelManager
    print("AdvancedModelManager imported successfully")
except Exception as e:
    print(f"AdvancedModelManager import failed: {e}")

print("Test complete")
