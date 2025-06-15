#!/usr/bin/env python3
"""
Test script to verify all agent file creation capabilities
"""

import asyncio
import logging
from agents.architect_agent import ArchitectAgent
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.qa_agent import QAAgent
from agents.orchestrator_agent import OrchestratorAgent
from core.real_llm_manager import RealLLMManager
from core.advanced_memory_manager import AdvancedMemoryManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_agent_file_creation():
    """Test that all agents can create their specific file types"""
      # Initialize managers
    llm_manager = RealLLMManager()
    memory_manager = AdvancedMemoryManager({})
    
    # Test tasks for each agent type
    test_tasks = {
        'architect': {
            'title': 'Design E-commerce Platform Architecture',
            'description': 'Create a scalable e-commerce platform architecture with microservices, API gateway, and cloud deployment strategy.',
            'type': 'system_design'
        },        'qa': {
            'title': 'Create Automated Test Suite for Payment System',
            'description': 'Create automated test scripts for payment processing including unit tests, integration tests, and E2E automation scenarios.',
            'type': 'test_automation'
        },
        'orchestrator': {
            'title': 'Plan E-commerce Development Project',
            'description': 'Break down e-commerce platform development into manageable tasks with dependencies and agent assignments.',
            'type': 'task_planning'
        },
        'backend': {
            'title': 'Implement Order Management API',
            'description': 'Create REST API for order management with CRUD operations, validation, and database integration.',
            'type': 'api_development'
        },
        'frontend': {
            'title': 'Create Product Catalog Component',
            'description': 'Build React component for displaying product catalog with search, filters, and pagination.',
            'type': 'component_development'
        }
    }
    
    # Agent configurations
    agent_configs = {
        'architect': {'role': 'System Architect', 'model': 'default'},
        'qa': {'role': 'QA Engineer', 'model': 'default'},
        'orchestrator': {'role': 'Project Orchestrator', 'model': 'default'},
        'backend': {'role': 'Backend Developer', 'model': 'default'},
        'frontend': {'role': 'Frontend Developer', 'model': 'default'}
    }
      # Create and test each agent
    agents = {}
    
    print("🧪 Testing Agent File Creation Capabilities")
    print("=" * 60)
    
    for agent_type, config in agent_configs.items():
        try:
            print(f"\nTesting {agent_type.title()} Agent...")
            
            # Create agent instance
            agent = None
            if agent_type == 'architect':
                agent = ArchitectAgent(agent_type, config, llm_manager, memory_manager)
            elif agent_type == 'qa':
                agent = QAAgent(agent_type, config, llm_manager, memory_manager)
            elif agent_type == 'orchestrator':
                agent = OrchestratorAgent(agent_type, config, llm_manager, memory_manager)
            elif agent_type == 'backend':
                agent = BackendAgent(agent_type, config, llm_manager, memory_manager)
            elif agent_type == 'frontend':
                agent = FrontendAgent(agent_type, config, llm_manager, memory_manager)
            
            if agent is None:
                print(f"{agent_type.title()} Agent - Unknown agent type")
                continue
            
            # Initialize agent
            await agent.initialize()
            
            # Execute task
            task = test_tasks[agent_type]
            result = await agent.execute_task(task)
            
            print(f"{agent_type.title()} Agent - Task completed: {result.get('summary', 'No summary')}")
            
            agents[agent_type] = agent
            
        except Exception as e:
            print(f"{agent_type.title()} Agent - Error: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 File Creation Test Complete!")
    print("\nCheck the agent_outputs/ directory for generated files:")
    print("- ArchitectAgent/ (architecture docs, diagrams)")
    print("- QAAgent/ (test files, test plans)")
    print("- OrchestratorAgent/ (task breakdowns, workflows)")
    print("- Database/ (backend SQL files)")
    print("- Frontend/ (React components)")

if __name__ == "__main__":
    asyncio.run(test_agent_file_creation())


