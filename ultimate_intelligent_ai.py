#!/usr/bin/env python3
"""
Ultimate Autonomous AI System with Intelligent Model Selection
Final integration that discovers models dynamically and selects optimally for each task.
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

from intelligent_llm_manager import IntelligentLLMManager
from core.advanced_memory_manager import AdvancedMemoryManager
from agents.architect_agent import ArchitectAgent
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.qa_agent import QAAgent
from agents.orchestrator_agent import OrchestratorAgent

class UltimateAutonomousAI:
    """Ultimate autonomous AI with intelligent model selection"""
    
    def __init__(self):
        self.setup_logging()
        self.agents = {}
        self.llm_manager = None
        self.memory_manager = None
        
    def setup_logging(self):
        """Setup logging without Unicode characters"""
        log_file = f"logs/ultimate_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        os.makedirs("logs", exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("UltimateAI")
        
    async def initialize_intelligent_systems(self):
        """Initialize with intelligent model discovery"""
        self.logger.info("INITIALIZING ULTIMATE AUTONOMOUS AI")
        self.logger.info("=" * 50)
        
        # Initialize Intelligent LLM Manager
        try:
            self.llm_manager = IntelligentLLMManager()
            await self.llm_manager.initialize()
            self.logger.info("SUCCESS: Intelligent LLM Manager ready")
        except Exception as e:
            self.logger.error(f"FAILED: LLM Manager initialization - {e}")
            return False
        
        # Initialize Memory Manager
        try:
            memory_config = {
                'vector_db_path': 'memory/vector_store',
                'persistent': True,
                'collection_name': 'agent_memories'
            }
            self.memory_manager = AdvancedMemoryManager(memory_config)
            await self.memory_manager.initialize()
            self.logger.info("SUCCESS: Memory Manager ready")
        except Exception as e:
            self.logger.warning(f"WARNING: Memory Manager using fallback - {e}")
            # Create a simple fallback memory manager
            self.memory_manager = type('MockMemory', (), {
                'store_experience': lambda *args: asyncio.sleep(0),
                'query_memory': lambda *args: [],
                'get_agent_context': lambda *args: {'experiences': []}
            })()
        
        return True
        
    async def create_intelligent_agents(self):
        """Create agents with intelligent model selection"""
        self.logger.info("CREATING INTELLIGENT AGENTS")
        self.logger.info("=" * 50)
        
        # Agent configurations
        agent_configs = {
            'architect': {
                'role': 'System Architect',
                'capabilities': ['system_design', 'architecture_review', 'planning'],
                'preferred_tasks': ['system_design', 'architecture_review']
            },
            'backend': {
                'role': 'Backend Developer',
                'capabilities': ['api_development', 'database_design', 'code_generation'],
                'preferred_tasks': ['api_development', 'code_generation']
            },
            'frontend': {
                'role': 'Frontend Developer', 
                'capabilities': ['ui_development', 'component_design', 'code_generation'],
                'preferred_tasks': ['ui_development', 'code_generation']
            },
            'qa': {
                'role': 'QA Analyst',
                'capabilities': ['testing_strategy', 'quality_assurance', 'analysis'],
                'preferred_tasks': ['testing_strategy', 'analysis']
            },
            'orchestrator': {
                'role': 'Project Orchestrator',
                'capabilities': ['project_planning', 'coordination', 'management'],
                'preferred_tasks': ['planning', 'coordination']
            }
        }
        
        for agent_id, config in agent_configs.items():
            try:
                # Create agent instance
                if agent_id == 'architect':
                    agent = ArchitectAgent(agent_id, config, self.llm_manager, self.memory_manager)
                elif agent_id == 'backend':
                    agent = BackendAgent(agent_id, config, self.llm_manager, self.memory_manager)
                elif agent_id == 'frontend':
                    agent = FrontendAgent(agent_id, config, self.llm_manager, self.memory_manager)
                elif agent_id == 'qa':
                    agent = QAAgent(agent_id, config, self.llm_manager, self.memory_manager)
                elif agent_id == 'orchestrator':
                    agent = OrchestratorAgent(agent_id, config, self.llm_manager, self.memory_manager)
                
                # Initialize agent
                await agent.initialize()
                self.agents[agent_id] = agent
                
                self.logger.info(f"SUCCESS: {agent_id} agent created and ready")
                
            except Exception as e:
                self.logger.error(f"FAILED: {agent_id} agent creation - {e}")
                
        self.logger.info(f"TOTAL AGENTS CREATED: {len(self.agents)}")
        return len(self.agents) > 0
    
    async def run_intelligent_workflow(self):
        """Run intelligent workflow with dynamic model selection"""
        self.logger.info("STARTING INTELLIGENT WORKFLOW")
        self.logger.info("=" * 50)
        
        # Test intelligent model selection with different scenarios
        test_scenarios = [
            {
                'agent': 'orchestrator',
                'task': 'Create a project plan for building a modern web application',
                'task_type': 'planning',
                'priority': 'quality',
                'timeout': 20
            },
            {
                'agent': 'architect',
                'task': 'Design a REST API architecture for user management',
                'task_type': 'system_design', 
                'priority': 'balanced',
                'timeout': 15
            },
            {
                'agent': 'backend',
                'task': 'Write a Python function to hash passwords securely',
                'task_type': 'code_generation',
                'priority': 'speed',
                'timeout': 10
            }
        ]
        
        results = []
        
        for i, scenario in enumerate(test_scenarios, 1):
            self.logger.info(f"SCENARIO {i}: {scenario['agent']} - {scenario['task_type']}")
            
            try:
                # Generate response with intelligent model selection
                response = await asyncio.wait_for(
                    self.llm_manager.generate_response(
                        agent_role=scenario['agent'],
                        prompt=scenario['task'],
                        task_type=scenario['task_type'],
                        priority=scenario['priority'],
                        max_tokens=300
                    ),
                    timeout=scenario['timeout']
                )
                
                # Log results
                success = response.get('success', False)
                model = response.get('selected_model', 'unknown')
                content_length = len(response.get('content', ''))
                response_time = response.get('response_time', 0)
                
                self.logger.info(f"RESULT: {'SUCCESS' if success else 'FALLBACK'}")
                self.logger.info(f"MODEL: {model}")
                self.logger.info(f"TIME: {response_time:.2f}s")
                self.logger.info(f"CONTENT: {content_length} chars")
                
                # Save result to file
                if success and content_length > 50:
                    filename = f"outputs/intelligent_{scenario['agent']}_{datetime.now().strftime('%H%M%S')}.md"
                    os.makedirs("outputs", exist_ok=True)
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(f"# {scenario['task']}\n\n")
                        f.write(f"**Agent:** {scenario['agent']}\n")
                        f.write(f"**Model:** {model}\n")
                        f.write(f"**Task Type:** {scenario['task_type']}\n")
                        f.write(f"**Priority:** {scenario['priority']}\n")
                        f.write(f"**Response Time:** {response_time:.2f}s\n")
                        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
                        f.write("## Content\n\n")
                        f.write(response.get('content', ''))
                    
                    self.logger.info(f"SAVED: {filename}")
                
                results.append({
                    'scenario': i,
                    'success': success,
                    'model': model,
                    'time': response_time,
                    'content_length': content_length
                })
                
            except asyncio.TimeoutError:
                self.logger.error(f"TIMEOUT: Scenario {i} timed out")
                results.append({'scenario': i, 'success': False, 'error': 'timeout'})
            except Exception as e:
                self.logger.error(f"ERROR: Scenario {i} failed - {e}")
                results.append({'scenario': i, 'success': False, 'error': str(e)})
        
        return results
    
    async def generate_status_report(self):
        """Generate comprehensive status report"""
        self.logger.info("GENERATING STATUS REPORT")
        self.logger.info("=" * 50)
        
        try:
            report = await self.llm_manager.get_intelligent_status_report()
            
            self.logger.info(f"TOTAL MODELS: {report.get('total_models', 0)}")
            self.logger.info(f"ACTIVE PROVIDERS: {report.get('active_providers', [])}")
            
            # Save detailed report
            report_file = f"reports/intelligent_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs("reports", exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"REPORT SAVED: {report_file}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"REPORT GENERATION FAILED: {e}")
            return {}

async def main():
    """Main function to run the ultimate autonomous AI"""
    print("ULTIMATE AUTONOMOUS AI WITH INTELLIGENT MODEL SELECTION")
    print("=" * 60)
    print(f"Started at: {datetime.now().isoformat()}")
    print()
    
    ai = UltimateAutonomousAI()
    
    # Initialize systems
    if not await ai.initialize_intelligent_systems():
        print("CRITICAL ERROR: System initialization failed")
        return
    
    # Create agents
    if not await ai.create_intelligent_agents():
        print("CRITICAL ERROR: Agent creation failed")
        return
    
    # Run intelligent workflow
    results = await ai.run_intelligent_workflow()
    
    # Generate status report
    report = await ai.generate_status_report()
    
    # Summary
    print(f"\nWORKFLOW COMPLETE")
    print("=" * 60)
    
    successful = sum(1 for r in results if r.get('success'))
    total = len(results)
    
    print(f"SUCCESSFUL SCENARIOS: {successful}/{total}")
    print(f"TOTAL MODELS AVAILABLE: {report.get('total_models', 0)}")
    print(f"ACTIVE PROVIDERS: {', '.join(report.get('active_providers', []))}")
    
    if successful > 0:
        print(f"\nSUCCESS: Real AI content generation working!")
        print("Check 'outputs/' directory for generated content")
        print("Check 'reports/' directory for detailed analysis")
    else:
        print(f"\nISSUE: No successful content generation")
        print("Check logs and ensure models are loaded and responsive")

if __name__ == "__main__":
    asyncio.run(main())
