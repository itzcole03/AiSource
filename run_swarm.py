#!/usr/bin/env python3
"""
Quick Swarm Launcher - Get the Ultimate Copilot running NOW
This bypasses complex initialization and gets the agents working immediately
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Simple logging setup
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger("SwarmLauncher")

# Import our simple agents for quick testing
from core.simple_agents_fixed import (
    SimpleOrchestratorAgent,
    SimpleArchitectAgent, 
    SimpleBackendAgent,
    SimpleFrontendAgent,
    SimpleQAAgent
)

# Import enhanced agent capabilities
from working_agent_upgrade import dispatch_enhanced_task, dispatch_task_sync

class SimpleSwarmRunner:
    def __init__(self):
        self.agents = {}
        self.running = False
        
    async def initialize_agents(self):
        """Quick agent initialization"""
        logger.info("Initializing agent swarm...")
        
        try:
            self.agents = {
                "orchestrator": SimpleOrchestratorAgent(),
                "architect": SimpleArchitectAgent(),
                "backend": SimpleBackendAgent(),
                "frontend": SimpleFrontendAgent(),
                "qa": SimpleQAAgent()
            }
            
            # Initialize each agent
            for name, agent in self.agents.items():
                try:
                    if hasattr(agent, 'agent_initialize'):
                        await agent.agent_initialize()
                    logger.info(f"{name.title()} agent ready")
                except Exception as e:
                    logger.warning(f"{name} agent had issues: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to initialize agents: {e}")
            
    async def run_autonomous_mode(self):
        """Start autonomous operation"""
        logger.info("Starting autonomous swarm mode...")
        
        # Get workspace info
        workspace = os.getcwd()
        logger.info(f"Working in: {workspace}")
        
        # Create a simple task for the orchestrator
        task = {
            "title": "Autonomous Workspace Analysis",
            "description": f"Analyze the project in {workspace} and start improving it. Look for areas that need development, testing, or optimization.",
            "workspace": workspace,
            "mode": "autonomous"
        }
        
        context = {
            "workspace_path": workspace,
            "available_agents": list(self.agents.keys()),
            "goal": "continuous_improvement"
        }
        
        # Start with orchestrator
        orchestrator = self.agents.get("orchestrator")
        if orchestrator:
            logger.info("Orchestrator taking control...")
            try:
                result = await orchestrator.process_task(task, context)
                logger.info(f"Plan created: {result.get('summary', 'Processing...')}")
                
                # Now distribute work to other agents
                await self.distribute_work(result, context)
                
            except Exception as e:
                logger.error(f"Orchestrator failed: {e}")
        
    async def distribute_work(self, plan, context):
        """Distribute work among agents"""
        logger.info("Distributing work to specialist agents...")
        
        tasks = []
        
        # Architect analyzes structure
        if "architect" in self.agents:
            tasks.append(self.run_agent_task("architect", "analyze_architecture", context))
            
        # Backend checks for improvements
        if "backend" in self.agents:
            tasks.append(self.run_agent_task("backend", "optimize_backend", context))
            
        # Frontend reviews UI/UX
        if "frontend" in self.agents:
            tasks.append(self.run_agent_task("frontend", "improve_frontend", context))
            
        # QA runs analysis
        if "qa" in self.agents:
            tasks.append(self.run_agent_task("qa", "quality_analysis", context))
            
        # Run all tasks concurrently
        if tasks:
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                successful = [r for r in results if not isinstance(r, Exception)]
                logger.info(f"Completed {len(successful)} out of {len(tasks)} tasks")
                  # Print results summary
                for i, result in enumerate(results):
                    if not isinstance(result, Exception) and result and isinstance(result, dict):
                        agent_name = result.get('agent', f'Agent_{i}')
                        summary = result.get('summary', 'Task completed')
                        logger.info(f"{agent_name}: {summary}")
                        
            except Exception as e:
                logger.error(f"Task execution failed: {e}")
    
    async def run_agent_task(self, agent_name, task_type, context):
        """Enhanced agent task with memory and retry logic"""
        agent = self.agents.get(agent_name)
        if not agent:
            return None
            
        # Create descriptive task for enhanced agent
        task_description = f"Perform {task_type} analysis on workspace: {context.get('workspace_path', 'current directory')}"
        
        try:
            # Try enhanced agent first
            logger.info(f"🚀 Running enhanced {agent_name} for {task_type}")
            result = await dispatch_enhanced_task(agent_name, task_description, context)
            
            if result.get("success"):
                logger.info(f"✅ Enhanced {agent_name} completed {task_type}")
                return {
                    "agent": agent_name,
                    "summary": f"Enhanced {task_type} completed successfully",
                    "result": result.get("result", "Task completed"),
                    "plan": result.get("result", "Enhanced analysis provided")
                }
            else:
                logger.warning(f"⚠️ Enhanced {agent_name} had issues, falling back to simple agent")
                # Fallback to original agent logic
                return await self._fallback_agent_task(agent, agent_name, task_type, context)
                
        except Exception as e:
            logger.warning(f"Enhanced agent failed: {e}, using fallback")
            # Fallback to original agent logic
            return await self._fallback_agent_task(agent, agent_name, task_type, context)
    
    async def _fallback_agent_task(self, agent, agent_name, task_type, context):
        """Fallback to original agent logic"""
        task = {
            "type": task_type,
            "workspace": context.get("workspace_path"),
            "mode": "autonomous"
        }
        
        try:
            if hasattr(agent, 'process_task'):
                result = await agent.process_task(task, context)
                logger.info(f"{agent_name} completed {task_type} (fallback)")
                return result
            elif hasattr(agent, 'handle_autonomous_task'):
                result = await agent.handle_autonomous_task()
                logger.info(f"{agent_name} completed autonomous task (fallback)")
                return result
        except Exception as e:
            logger.warning(f"{agent_name} task failed: {e}")
            return None
    
    async def continuous_improvement_loop(self):
        """Keep the swarm running and improving"""
        logger.info("Starting continuous improvement loop...")
        
        iteration = 0
        while self.running:
            iteration += 1
            logger.info(f"Improvement iteration #{iteration}")
            
            try:
                await self.run_autonomous_mode()
                
                # Wait before next iteration
                logger.info("⏱️ Waiting 60 seconds before next improvement cycle...")
                for i in range(60):
                    if not self.running:
                        break
                    await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("🛑 Stopping on user request")
                break
            except Exception as e:
                logger.error(f"Loop error: {e}")
                await asyncio.sleep(10)  # Brief pause on error
    
    async def start(self):
        """Start the swarm"""
        self.running = True
        await self.initialize_agents()
        
        # Choose mode
        print("\n" + "="*50)
        print("  ULTIMATE COPILOT SWARM")
        print("="*50)
        print("1. Run once (single analysis)")
        print("2. Continuous mode (keep improving)")
        print("3. Interactive mode (give commands)")
        
        try:
            choice = input("\nSelect mode (1-3): ").strip()
            
            if choice == "1":
                await self.run_autonomous_mode()
            elif choice == "2":
                await self.continuous_improvement_loop()
            elif choice == "3":
                await self.interactive_mode()
            else:
                logger.info("Running default single analysis...")
                await self.run_autonomous_mode()
                
        except KeyboardInterrupt:
            logger.info("🛑 Swarm stopped by user")
        finally:
            self.running = False
    
    async def interactive_mode(self):
        """Interactive command mode"""
        logger.info("💬 Interactive mode - type 'quit' to exit")
        
        while self.running:
            try:
                user_input = input("\nEnter command: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'stop']:
                    break
                    
                if not user_input:
                    continue
                
                # Send command to orchestrator
                task = {
                    "title": "User Command",
                    "description": user_input,
                    "mode": "interactive"
                }
                
                context = {"workspace_path": os.getcwd()}
                
                orchestrator = self.agents.get("orchestrator")
                if orchestrator:
                    result = await orchestrator.process_task(task, context)
                    print(f"Result: {result.get('summary', 'Task processed')}")
                    
                    # Show the detailed response
                    if 'plan' in result:
                        print("\nDetailed Plan:")
                        print(result['plan'][:500] + "..." if len(result.get('plan', '')) > 500 else result.get('plan', ''))
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Interactive error: {e}")

async def main():
    """Main entry point"""
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    logger.info("Ultimate Copilot Swarm Starting...")
    
    swarm = SimpleSwarmRunner()
    await swarm.start()
    
    logger.info("Swarm session complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Swarm stopped")
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


