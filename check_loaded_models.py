#!/usr/bin/env python3
"""
Quick validation of loaded model detection
"""

import asyncio
import aiohttp
import json

async def check_loaded_models():
    """Quick check of what models are actually loaded"""
    
    print("Checking currently loaded models...")
    
    # Check LM Studio
    print("\n=== LM Studio Check ===")
    try:
        async with aiohttp.ClientSession() as session:
            # Get available models
            async with session.get("http://localhost:1234/v1/models") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = data.get('data', [])
                    print(f"Available models: {len(models)}")
                    
                    loaded_count = 0
                    for model in models:
                        model_id = model.get('id', '')
                        print(f"  Testing {model_id}...")
                        
                        # Test if responsive
                        try:
                            payload = {
                                "model": model_id,
                                "messages": [{"role": "user", "content": "hi"}],
                                "max_tokens": 1
                            }
                            async with session.post(
                                "http://localhost:1234/v1/chat/completions",
                                json=payload,
                                timeout=aiohttp.ClientTimeout(total=3)
                            ) as test_resp:
                                if test_resp.status == 200:
                                    print(f"    ✓ LOADED and responsive")
                                    loaded_count += 1
                                else:
                                    print(f"    ✗ Not responsive (status: {test_resp.status})")
                        except Exception as e:
                            print(f"    ✗ Not responsive (error: {e})")
                    
                    print(f"\nLM Studio Summary: {loaded_count}/{len(models)} models loaded")
                else:
                    print(f"LM Studio not responding (status: {resp.status})")
    except Exception as e:
        print(f"LM Studio check failed: {e}")
    
    # Check Ollama
    print("\n=== Ollama Check ===")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:11434/api/tags") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    models = data.get('models', [])
                    print(f"Available models: {len(models)}")
                    
                    loaded_count = 0
                    for model in models:
                        model_name = model.get('name', '')
                        print(f"  Testing {model_name}...")
                        
                        # Test if responsive
                        try:
                            payload = {
                                "model": model_name,
                                "prompt": "hi",
                                "stream": False
                            }
                            async with session.post(
                                "http://127.0.0.1:11434/api/generate",
                                json=payload,
                                timeout=aiohttp.ClientTimeout(total=3)
                            ) as test_resp:
                                if test_resp.status == 200:
                                    print(f"    ✓ LOADED and responsive")
                                    loaded_count += 1
                                else:
                                    print(f"    ✗ Not responsive (status: {test_resp.status})")
                        except Exception as e:
                            print(f"    ✗ Not responsive (error: {e})")
                    
                    print(f"\nOllama Summary: {loaded_count}/{len(models)} models loaded")
                else:
                    print(f"Ollama not responding (status: {resp.status})")
    except Exception as e:
        print(f"Ollama check failed: {e}")

if __name__ == "__main__":
    asyncio.run(check_loaded_models())
