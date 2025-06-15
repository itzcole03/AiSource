#!/usr/bin/env python3
"""
Check which models are available in LM Studio
"""

import asyncio
import aiohttp
import json

async def check_lm_studio_models():
    """Check available models in LM Studio"""
    print("=== Checking LM Studio Models ===")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:1234/v1/models", timeout=5) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('data', [])
                    
                    print(f"✅ LM Studio is running")
                    print(f"📋 Available models ({len(models)}):")
                    
                    required_models = [
                        "mistral-small-3.1-24b-instruct-2503",
                        "codellama-7b-instruct", 
                        "gemma-2b-it"
                    ]
                    
                    available_model_ids = [model.get('id', '') for model in models]
                    
                    for model in models:
                        model_id = model.get('id', 'Unknown')
                        print(f"  - {model_id}")
                    
                    print(f"\n🔍 Checking required models:")
                    for req_model in required_models:
                        # Check if any available model contains the required model name
                        found = any(req_model.lower() in available_id.lower() for available_id in available_model_ids)
                        status = "✅ FOUND" if found else "❌ MISSING"
                        print(f"  {status}: {req_model}")
                        
                        if found:
                            # Show which specific model matches
                            matches = [aid for aid in available_model_ids if req_model.lower() in aid.lower()]
                            for match in matches:
                                print(f"         → {match}")
                    
                    if not models:
                        print("⚠️  No models loaded. Please load models in LM Studio.")
                        
                else:
                    print(f"❌ LM Studio responded with status: {response.status}")
                    
    except Exception as e:
        print(f"❌ Cannot connect to LM Studio: {e}")
        print("💡 Make sure LM Studio is running with local server on port 1234")

if __name__ == "__main__":
    asyncio.run(check_lm_studio_models())
