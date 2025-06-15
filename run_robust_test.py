#!/usr/bin/env python3
"""
Robust Autonomous AI Workflow with Timeouts and Error Handling
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.working_llm_manager import WorkingLLMManager

class RobustAutonomousWorkflow:
    """Robust autonomous AI workflow with timeout handling"""
    
    def __init__(self):
        self.setup_logging()
        self.llm_manager = None
        
    def setup_logging(self):
        """Setup enhanced logging"""
        log_file = f"logs/robust_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        os.makedirs("logs", exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("RobustAI")
        
    async def initialize_llm_system(self):
        """Initialize LLM system with health checks"""
        self.logger.info("Initializing LLM System...")
        
        try:
            self.llm_manager = WorkingLLMManager()
            await asyncio.wait_for(self.llm_manager.initialize(), timeout=15.0)
            
            # Test connectivity
            await self.test_llm_connectivity()
            
            self.logger.info("LLM System ready for robust operation")
            return True
            
        except asyncio.TimeoutError:
            self.logger.error("LLM initialization timed out after 15 seconds")
            return False
        except Exception as e:
            self.logger.error(f"LLM initialization failed: {e}")
            return False
    
    async def test_llm_connectivity(self):
        """Test LLM connectivity with timeouts"""
        test_roles = ["architect", "orchestrator"]
        
        for role in test_roles:
            try:
                self.logger.info(f"Testing {role} connectivity...")
                response = await asyncio.wait_for(
                    self.llm_manager.generate_response(
                        agent_role=role,
                        prompt="Hello, respond with 'OK'",
                        max_tokens=10
                    ),
                    timeout=8.0
                )
                
                if response.get('success'):
                    self.logger.info(f"✓ {role} responsive: {response.get('content', '')[:50]}")
                else:
                    self.logger.warning(f"⚠ {role} using fallback")
                    
            except asyncio.TimeoutError:
                self.logger.error(f"✗ {role} timed out after 8 seconds")
                raise Exception(f"{role} not responsive")
            except Exception as e:
                self.logger.error(f"✗ {role} error: {e}")
                raise e
    
    async def create_simple_project_plan(self):
        """Create a simple project plan with timeout"""
        self.logger.info("Creating project plan...")
        
        try:
            response = await asyncio.wait_for(
                self.llm_manager.generate_response(
                    agent_role="orchestrator",
                    prompt="""Create a simple project plan for building a basic web app. 
                    Include 5 main tasks with brief descriptions. Format as numbered list.""",
                    max_tokens=500
                ),
                timeout=15.0
            )
            
            if response.get('success'):
                plan_content = response.get('content', '')
                self.logger.info("✓ Project plan created successfully")
                
                # Save the plan
                os.makedirs("agent_outputs/RobustTest", exist_ok=True)
                with open("agent_outputs/RobustTest/project_plan.txt", "w", encoding='utf-8') as f:
                    f.write(f"# Robust AI Project Plan - {datetime.now()}\n\n")
                    f.write(f"Model: {response.get('model', 'unknown')}\n")
                    f.write(f"Provider: {response.get('provider', 'unknown')}\n\n")
                    f.write(plan_content)
                
                return True
            else:
                self.logger.warning("Project plan using fallback response")
                return False
                
        except asyncio.TimeoutError:
            self.logger.error("Project plan generation timed out after 15 seconds")
            return False
        except Exception as e:
            self.logger.error(f"Project plan generation failed: {e}")
            return False
    
    async def run_robust_test(self):
        """Run robust test workflow"""
        self.logger.info("🚀 Starting Robust AI Test Workflow")
        
        # Step 1: Initialize LLM
        if not await self.initialize_llm_system():
            self.logger.error("❌ LLM initialization failed - aborting")
            return False
        
        # Step 2: Create project plan
        if not await self.create_simple_project_plan():
            self.logger.error("❌ Project plan creation failed")
            return False
        
        self.logger.info("✅ Robust AI Test completed successfully!")
        return True

async def main():
    """Main execution function"""
    workflow = RobustAutonomousWorkflow()
    
    try:
        success = await workflow.run_robust_test()
        if success:
            print("\n🎉 SUCCESS: Robust AI workflow completed!")
            print("Check agent_outputs/RobustTest/project_plan.txt for results")
        else:
            print("\n❌ FAILED: Robust AI workflow failed")
            print("Check logs for details")
            
    except KeyboardInterrupt:
        print("\n⚠ Workflow interrupted by user")
    except Exception as e:
        print(f"\n💥 Workflow crashed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
