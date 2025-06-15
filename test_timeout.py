#!/usr/bin/env python3
"""
Quick test to verify LM Studio is responsive
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.working_llm_manager import WorkingLLMManager

async def quick_test():
    """Quick test of LM Studio responsiveness"""
    print("=== Quick LM Studio Test ===")
    
    llm_manager = WorkingLLMManager()
    await llm_manager.initialize()
    
    print(f"Active providers: {list(llm_manager.active_providers.keys())}")
    
    try:
        print("\nTesting orchestrator role...")
        response = await asyncio.wait_for(
            llm_manager.generate_response(
                agent_role="orchestrator",
                prompt="Create a simple task list with 3 items",
                max_tokens=100
            ),
            timeout=10.0
        )
        print(f"Success: {response['content'][:200]}...")
        
    except asyncio.TimeoutError:
        print("ERROR: LM Studio call timed out after 10 seconds")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(quick_test())
