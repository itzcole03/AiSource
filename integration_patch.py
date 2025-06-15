#!/usr/bin/env python3
"""
Integration patch for run_swarm.py

This file shows you exactly how to integrate the working agent upgrade system
into your existing run_swarm.py without breaking anything.
"""

# At the top of your run_swarm.py, add this import:
from working_agent_upgrade import dispatch_task, dispatch_enhanced_task

# Then, in your run_agent_task method (around line 138), replace this:
#
# OLD CODE:
# if hasattr(agent, 'process_task'):
#     result = await agent.process_task(task, context)
#     logger.info(f"{agent_name} completed {task_type}")
#     return result
#
# NEW CODE:
async def enhanced_run_agent_task(agent_name, task_type, context):
    """Enhanced version of run_agent_task with memory and retry"""
    
    # Create a descriptive task
    task_description = f"Perform {task_type} analysis on workspace: {context.get('workspace_path', 'current directory')}"
    
    try:
        # Use the enhanced dispatcher
        result = await dispatch_enhanced_task(agent_name, task_description, context)
        
        if result.get("success"):
            logger.info(f"✅ {agent_name} completed {task_type}")
            return {
                "agent": agent_name,
                "summary": f"Completed {task_type} successfully",
                "result": result.get("result", "Task completed"),
                "plan": result.get("result", "No detailed plan available")
            }
        else:
            logger.warning(f"⚠️ {agent_name} had issues with {task_type}")
            return {
                "agent": agent_name,
                "summary": f"Issues with {task_type}: {result.get('error', 'Unknown error')}",
                "error": result.get('error')
            }
            
    except Exception as e:
        logger.error(f"❌ {agent_name} failed {task_type}: {e}")
        return {
            "agent": agent_name,
            "summary": f"Failed {task_type}: {str(e)}",
            "error": str(e)
        }

# For immediate testing, you can also patch the distribute_work method:
async def enhanced_distribute_work(plan, context):
    """Enhanced work distribution with memory-aware agents"""
    logger.info("🚀 Distributing work to enhanced agent swarm...")
    
    tasks = []
    
    # Define specific tasks for each agent
    agent_tasks = {
        "architect": "Analyze the project architecture and identify areas for improvement. Look for design patterns, code organization, and suggest architectural enhancements.",
        "backend": "Review backend code for performance optimizations, security improvements, and code quality. Check API endpoints, database queries, and error handling.",
        "frontend": "Examine frontend code for UI/UX improvements, performance optimizations, and modern best practices. Look for component structure and user experience.",
        "qa": "Perform comprehensive quality analysis including code coverage, test completeness, security vulnerabilities, and performance bottlenecks."
    }
    
    # Run enhanced tasks
    for agent_name, task_description in agent_tasks.items():
        if agent_name in ["architect", "backend", "frontend", "qa"]:  # Only run available agents
            tasks.append(dispatch_enhanced_task(agent_name, task_description, context))
      # Execute all tasks
    if tasks:
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            successful = [r for r in results if not isinstance(r, Exception) and isinstance(r, dict) and r.get("success")]
            
            logger.info(f"✅ Enhanced swarm completed {len(successful)} out of {len(tasks)} tasks")
            
            # Print enhanced results
            for result in results:
                if not isinstance(result, Exception) and isinstance(result, dict):
                    agent_name = result.get('agent', 'Unknown')
                    summary = result.get('result', 'Task completed')[:200]
                    logger.info(f"🤖 {agent_name.title()}: {summary}...")
                else:
                    logger.warning(f"⚠️ Task failed: {result}")
                
        except Exception as e:
            logger.error(f"❌ Enhanced task execution failed: {e}")

# Simple test function you can call
async def test_enhanced_agents():
    """Test the enhanced agent system"""
    print("\n🧪 Testing Enhanced Agent System...")
    
    context = {"workspace_path": os.getcwd()}
    
    # Test individual agents
    test_tasks = [
        ("architect", "Create an overview of this project's architecture"),
        ("backend", "Analyze backend code quality and suggest improvements"),
        ("qa", "Identify potential testing gaps and quality issues")
    ]
    
    for agent_name, task in test_tasks:
        print(f"\n🤖 Testing {agent_name}...")
        result = await dispatch_enhanced_task(agent_name, task, context)
        
        if result.get("success"):
            print(f"✅ {agent_name} succeeded")
            print(f"📄 Result: {result['result'][:150]}...")
        else:
            print(f"❌ {agent_name} failed: {result.get('error')}")

if __name__ == "__main__":
    """
    To integrate this into your run_swarm.py:
    
    1. Copy the imports to the top of run_swarm.py
    2. Replace your run_agent_task method with enhanced_run_agent_task
    3. Optionally replace distribute_work with enhanced_distribute_work
    4. Test with: python integration_patch.py
    """
    
    import asyncio
    import os
    import logging
    
    # Setup logging for testing
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    logger = logging.getLogger("TestEnhanced")
    
    print("🚀 Enhanced Agent Integration Test")
    asyncio.run(test_enhanced_agents())
