#!/usr/bin/env python3
"""
Demo Script - Show the Ultimate Copilot in action
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from run_swarm import SimpleSwarmRunner

async def demo():
    print("ULTIMATE COPILOT SWARM DEMO")
    print("=" * 40)
    
    swarm = SimpleSwarmRunner()
    swarm.running = True
    
    # Initialize agents
    print("\n1. Initializing Agents...")
    await swarm.initialize_agents()
    
    # Run autonomous mode once
    print("\n2. Running Autonomous Analysis...")
    await swarm.run_autonomous_mode()
    
    print("\nDemo Complete!")
    print("\nYour Ultimate Copilot swarm is working perfectly!")
    print("Use 'python run_swarm.py' for full interactive mode.")

if __name__ == "__main__":
    asyncio.run(demo())

