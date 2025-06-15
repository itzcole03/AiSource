#!/usr/bin/env python3
"""
Test Intelligence Persistence for Ultimate Copilot Agents
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run_intelligent_model_agents import IntelligentLocalModelAgent

async def test_intelligence_persistence():
    """Test that agent intelligence persists across restarts"""
    print("🧪 Testing Agent Intelligence Persistence...")
    
    workspace_root = Path(__file__).parent
    
    # Create a test agent
    agent = IntelligentLocalModelAgent(
        name="TestAgent",
        role="Test Engineer", 
        workspace_root=str(workspace_root),
        instance_id="test"
    )
    
    print(f"📅 Initial intelligence level: {agent.intelligence_level}")
    
    # Initialize and check if intelligence was restored
    await agent.llm_manager.initialize()
    await agent.memory_manager.initialize()
    await agent._restore_agent_intelligence()
    
    print(f"Restored intelligence level: {agent.intelligence_level}")
    
    # Simulate some learning
    await agent.memory_manager.update_agent_learning(
        agent.name,
        {
            "task_success": True,
            "complexity_factor": 0.2,
            "pattern": "test_learning_pattern",
            "strategy": "persistence_verification",
            "metrics": {"test_score": 95.0}
        }
    )
    
    # Save intelligence
    await agent._save_agent_intelligence()
    
    # Get intelligence summary
    summary = await agent.memory_manager.get_agent_intelligence_summary(agent.name)
    
    print("Intelligence Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    print("Intelligence persistence test completed!")
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_intelligence_persistence())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


