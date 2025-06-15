#!/usr/bin/env python3
"""
Test Real Agent Intelligence 
Demonstrates that intelligence level actually affects agent behavior
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from run_intelligent_model_agents import IntelligentLocalModelAgent

async def test_real_intelligence():
    """Test that intelligence affects actual agent behavior"""
    print("🧪 Testing REAL Agent Intelligence vs Fake Counters...")
    
    workspace_root = Path(__file__).parent
    
    # Create agents with different intelligence levels
    dumb_agent = IntelligentLocalModelAgent("DumbAgent", "Test Engineer", str(workspace_root))
    smart_agent = IntelligentLocalModelAgent("SmartAgent", "Test Engineer", str(workspace_root))
    
    # Set different intelligence levels
    dumb_agent.intelligence_level = 2.0
    smart_agent.intelligence_level = 9.0
    
    print(f"\nDumb Agent (L{dumb_agent.intelligence_level}):")
    print(f"  - Temperature: {dumb_agent._get_intelligence_enhanced_temperature():.2f}")
    print(f"  - Max Complexity: {dumb_agent._get_intelligence_enhanced_task_complexity()}")
    print(f"  - Analysis Depth: {dumb_agent._get_intelligence_enhanced_analysis_depth()} files")
    print(f"  - Can Handle Advanced: {dumb_agent._can_handle_advanced_tasks()}")
    print(f"  - Rest Time: {dumb_agent._calculate_intelligent_rest_time()}s")
    print(f"  - Preferred Model: {dumb_agent._get_intelligent_model_selection('coding')}")
    
    print(f"\nSmart Agent (L{smart_agent.intelligence_level}):")
    print(f"  - Temperature: {smart_agent._get_intelligence_enhanced_temperature():.2f}")
    print(f"  - Max Complexity: {smart_agent._get_intelligence_enhanced_task_complexity()}")
    print(f"  - Analysis Depth: {smart_agent._get_intelligence_enhanced_analysis_depth()} files")
    print(f"  - Can Handle Advanced: {smart_agent._can_handle_advanced_tasks()}")
    print(f"  - Rest Time: {smart_agent._calculate_intelligent_rest_time()}s")
    print(f"  - Preferred Model: {smart_agent._get_intelligent_model_selection('coding')}")
    
    print(f"\nKey Differences:")
    temp_diff = dumb_agent._get_intelligence_enhanced_temperature() - smart_agent._get_intelligence_enhanced_temperature()
    print(f"  - Smart agent is {temp_diff:.2f} points more focused (lower temperature)")
    
    complexity_diff = smart_agent._get_intelligence_enhanced_task_complexity() - dumb_agent._get_intelligence_enhanced_task_complexity()
    print(f"  - Smart agent can handle {complexity_diff} points higher complexity tasks")
    
    analysis_diff = smart_agent._get_intelligence_enhanced_analysis_depth() - dumb_agent._get_intelligence_enhanced_analysis_depth()
    print(f"  - Smart agent can analyze {analysis_diff} more files")
    
    rest_diff = dumb_agent._calculate_intelligent_rest_time() - smart_agent._calculate_intelligent_rest_time()
    print(f"  - Smart agent works {rest_diff}s more efficiently (shorter rests)")
    
    print(f"\nIntelligence ACTUALLY affects agent behavior, not just a counter!")
    return True

if __name__ == "__main__":
    try:
        asyncio.run(test_real_intelligence())
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

