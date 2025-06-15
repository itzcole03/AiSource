#!/usr/bin/env python3
"""
Test Critical Thinking and Real Model Detection
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.real_time_model_detector import RealTimeModelDetector
from core.critical_thinking_engine import CriticalThinkingEngine

async def test_critical_thinking_and_models():
    """Test the new critical thinking and model detection capabilities"""
    print("🧪 Testing Critical Thinking & Real-Time Model Detection...")
    
    # Test model detection
    print("\nTesting Real-Time Model Detection:")
    detector = RealTimeModelDetector()
    available_models = await detector.detect_available_models()
    
    print(f"Available providers: {list(available_models.keys())}")
    for provider, models in available_models.items():
        print(f"  {provider}: {models}")
    
    # Test intelligent model selection
    print(f"\nTesting Intelligent Model Selection:")
    intelligence_levels = [2.0, 6.0, 9.0]
    task_types = ["coding", "analysis", "decision"]
    
    for intel in intelligence_levels:
        print(f"  Intelligence Level {intel}:")
        for task_type in task_types:
            best_model = detector.get_best_model_for_task(task_type, intel)
            print(f"    {task_type}: {best_model}")
    
    # Test critical thinking
    print(f"\n🤔 Testing Critical Thinking Engine:")
    thinking = CriticalThinkingEngine("TestAgent", "Backend Developer")
    
    # Simulate a task and result
    test_task = {
        "title": "Create User Authentication Module",
        "type": "create_component",
        "complexity": 7
    }
    
    # Simulate poor quality result
    poor_result = """
def login():
    # TODO: implement login
    pass
"""
    
    quality_analysis = await thinking.analyze_completion_quality(test_task, poor_result)
    print(f"Quality Analysis:")
    print(f"  Score: {quality_analysis['quality_score']:.2f}")
    print(f"  Concerns: {len(quality_analysis['concerns'])}")
    for concern in quality_analysis['concerns']:
        print(f"    • {concern}")
    print(f"  Refinement needed: {quality_analysis['refinement_needed']}")
    
    # Test enhancement reasoning
    enhancement_reasoning = await thinking.reason_about_enhancement_opportunities(poor_result, 7.0)
    print(f"Enhancement Opportunities:")
    print(f"  Potential: {enhancement_reasoning['enhancement_potential']:.2f}")
    print(f"  Opportunities: {len(enhancement_reasoning['specific_opportunities'])}")
    for opportunity in enhancement_reasoning['specific_opportunities'][:3]:
        print(f"    • {opportunity['description']} (Priority: {opportunity['priority']})")
    
    # Test decision making
    decision = await thinking.should_continue_working(test_task, poor_result, 7.0)
    print(f"Continue Working Decision:")
    print(f"  Should continue: {decision['continue_working']}")
    print(f"  Reasoning: {decision['reasoning']}")
    
    print(f"\nCritical thinking and model detection working!")

if __name__ == "__main__":
    try:
        asyncio.run(test_critical_thinking_and_models())
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

