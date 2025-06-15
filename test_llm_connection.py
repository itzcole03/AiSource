#!/usr/bin/env python3
"""
Test script to verify LLM connections are working
"""

import asyncio
from openai import OpenAI

async def test_lmstudio():
    """Test LM Studio connection"""
    try:
        client = OpenAI(
            base_url="http://localhost:1234/v1",
            api_key="not-needed"
        )
        
        response = client.chat.completions.create(
            model="mistral-small-3.1-24b-instruct-2503",  # Using a model we saw in the list
            messages=[{"role": "user", "content": "Hello! Can you respond with a simple greeting?"}],
            temperature=0.7,
            max_tokens=100
        )
        
        print("LM Studio Response:")
        print(f"Content: {response.choices[0].message.content}")
        print(f"Model: {response.model}")
        return True
        
    except Exception as e:
        print(f"LM Studio Error: {e}")
        return False

async def test_ollama():
    """Test Ollama connection using direct API"""
    import aiohttp
    try:
        payload = {
            "model": "mistral",
            "prompt": "Hello! Can you respond with a simple greeting?",
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": 100
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post("http://127.0.0.1:11434/api/generate", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    print("Ollama Response:")
                    print(f"Content: {data.get('response', '')}")
                    print(f"Model: mistral")
                    return True
                else:
                    print(f"Ollama HTTP Error: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"Ollama Error: {e}")
        return False

async def main():
    print("Testing LLM Connections...")
    print("=" * 50)
    
    # Test LM Studio
    lm_success = await test_lmstudio()
    print()
    
    # Test Ollama
    ollama_success = await test_ollama()
    print()
    
    if lm_success or ollama_success:
        print("✅ At least one LLM provider is working!")
    else:
        print("❌ No LLM providers are working")

if __name__ == "__main__":
    asyncio.run(main())
