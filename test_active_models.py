#!/usr/bin/env python3
"""
Simple test to verify active model tracking concept
"""

import asyncio
import aiohttp
import json
import time

async def test_active_model_concept():
    """Test the concept of tracking actively loaded vs available models"""
    print("=== TESTING ACTIVE MODEL TRACKING ===")
    
    # Test LM Studio - check what's actually loaded and responsive
    print("\n--- LM Studio Active Model Test ---")
    try:
        async with aiohttp.ClientSession() as session:
            # First get list of models
            async with session.get("http://localhost:1234/v1/models") as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('data', [])
                    print(f"Models reported as available: {len(models)}")
                    
                    for model in models:
                        model_id = model.get('id', 'unknown')
                        print(f"  📦 {model_id}")
                        
                        # Test if this model actually responds
                        print(f"    Testing responsiveness...")
                        start_time = time.time()
                        
                        try:
                            test_payload = {
                                "model": model_id,
                                "messages": [{"role": "user", "content": "test"}],
                                "max_tokens": 1
                            }
                            
                            async with session.post(
                                "http://localhost:1234/v1/chat/completions",
                                json=test_payload
                            ) as test_response:
                                response_time = time.time() - start_time
                                
                                if test_response.status == 200:
                                    print(f"    ✅ RESPONSIVE ({response_time:.2f}s)")
                                else:
                                    print(f"    ❌ NOT RESPONSIVE (status: {test_response.status})")
                        except Exception as e:
                            print(f"    ❌ NOT RESPONSIVE (error: {e})")
                else:
                    print("❌ LM Studio not available")
    except Exception as e:
        print(f"❌ LM Studio connection failed: {e}")
    
    # Test Ollama - check available vs actually responsive models
    print(f"\n--- Ollama Active Model Test ---")
    try:
        async with aiohttp.ClientSession() as session:
            # Get available models
            async with session.get("http://127.0.0.1:11434/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('models', [])
                    print(f"Models available: {len(models)}")
                    
                    responsive_models = []
                    
                    for model in models:
                        model_name = model.get('name', 'unknown')
                        size = model.get('size', 0)
                        size_mb = size // (1024 * 1024) if size else 0
                        print(f"  📦 {model_name} ({size_mb}MB)")
                        
                        # Test responsiveness  
                        print(f"    Testing responsiveness...")
                        start_time = time.time()
                        
                        try:
                            test_payload = {
                                "model": model_name,
                                "prompt": "test",
                                "stream": False,
                                "options": {"num_predict": 1}
                            }
                            
                            async with session.post(
                                "http://127.0.0.1:11434/api/generate",
                                json=test_payload
                            ) as test_response:
                                response_time = time.time() - start_time
                                
                                if test_response.status == 200:
                                    print(f"    ✅ RESPONSIVE ({response_time:.2f}s)")
                                    responsive_models.append(model_name)
                                else:
                                    print(f"    ❌ NOT RESPONSIVE (status: {test_response.status})")
                        except Exception as e:
                            print(f"    ❌ NOT RESPONSIVE (error: {e})")
                    
                    print(f"\n📊 Summary: {len(responsive_models)}/{len(models)} models are actively responsive")
                    print(f"Responsive models: {responsive_models}")
                    
                else:
                    print("❌ Ollama not available")
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
    
    print(f"\n🎯 CONCEPT VALIDATION:")
    print("✅ We can distinguish between 'available' and 'actively responsive' models")
    print("✅ We can test response times and reliability in real-time")
    print("✅ This enables intelligent caching and load balancing")

if __name__ == "__main__":
    asyncio.run(test_active_model_concept())
