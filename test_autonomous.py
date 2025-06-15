#!/usr/bin/env python3
"""
Test the overnight autonomous system (5 minute demo)
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger("AutonomousDemo")

from core.autonomous_agents import AutonomousImprovementCoordinator

async def demo_autonomous_operation():
    """Demo the autonomous operation for 5 minutes"""
    
    os.makedirs("logs", exist_ok=True)
    os.makedirs("logs/agents", exist_ok=True)
    
    logger.info("🌙 AUTONOMOUS SYSTEM 5-MINUTE DEMO")
    logger.info("="*50)
    
    # Initialize the coordinator
    coordinator = AutonomousImprovementCoordinator()
    await coordinator.initialize()
    
    logger.info("Starting autonomous operation for 5 minutes...")
    
    # Run for 5 minutes (300 seconds)
    start_time = asyncio.get_event_loop().time()
    
    # Create tasks but limit runtime
    tasks = [
        asyncio.create_task(coordinator.agents['orchestrator'].continuous_orchestration()),
        asyncio.create_task(coordinator.agents['architect'].continuous_architecture_improvement()),
        asyncio.create_task(coordinator.agents['backend'].continuous_backend_optimization())
    ]
    
    try:
        # Wait for 5 minutes or until all tasks complete
        await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=300)
    except asyncio.TimeoutError:
        logger.info("⏰ 5-minute demo completed!")
        
        # Cancel remaining tasks
        for task in tasks:
            task.cancel()
            
        # Give tasks a moment to clean up
        await asyncio.sleep(1)
        
    logger.info("Autonomous demo completed successfully!")
    logger.info("📂 Check logs/agents/ for detailed work logs")

if __name__ == "__main__":
    print("Testing Autonomous System (5 minutes)")
    print("The agents will analyze and improve the system...")
    print()
    
    try:
        asyncio.run(demo_autonomous_operation())
    except KeyboardInterrupt:
        print("\n🛑 Demo stopped")
    except Exception as e:
        print(f"Demo error: {e}")
        sys.exit(1)


