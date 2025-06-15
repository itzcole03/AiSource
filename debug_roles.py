#!/usr/bin/env python3
"""
Debug script to test role mapping and LLM responses
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.working_llm_manager import WorkingLLMManager

async def test_roles():
    """Test role-to-model mapping"""
    print("=== Testing Role-to-Model Mapping ===")
    
    llm_manager = WorkingLLMManager()
    await llm_manager.initialize()
    
    print(f"Active providers: {list(llm_manager.active_providers.keys())}")
    print(f"Agent model map: {llm_manager.agent_model_map}")
    
    # Test common role names
    test_roles = ['architect', 'Architect Agent', 'backend_dev', 'Backend Developer']
    
    for role in test_roles:
        print(f"\n--- Testing role: '{role}' ---")
        try:
            response = await llm_manager.generate_response(
                agent_role=role,
                prompt="Hello, what is your role?",
                max_tokens=50
            )
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_roles())
