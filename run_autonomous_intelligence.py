#!/usr/bin/env python3
"""
Autonomous AI Workflow Runner
Enhanced multi-agent system with real intelligence and memory
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
from core.advanced_memory_manager import AdvancedMemoryManager
from agents.architect_agent import ArchitectAgent
from agents.backend_agent import BackendAgent
from agents.frontend_agent import FrontendAgent
from agents.qa_agent import QAAgent
from agents.orchestrator_agent import OrchestratorAgent

class AutonomousAIWorkflow:
    """Enhanced autonomous AI workflow with memory and intelligence"""
    
    def __init__(self):
        self.setup_logging()
        self.agents = {}
        self.llm_manager = None
        self.memory_manager = None
        self.active_projects = []
        
    def setup_logging(self):
        """Setup enhanced logging"""
        log_file = f"logs/autonomous_ai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        os.makedirs("logs", exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger("AutonomousAI")
        
    async def initialize_ai_systems(self):
        """Initialize AI systems with enhanced capabilities"""
        self.logger.info("Initializing Autonomous AI Systems...")
          # Initialize LLM Manager with fallback
        try:
            self.llm_manager = WorkingLLMManager()
            await self.llm_manager.initialize()
            self.logger.info("LLM Manager with model integration ready")
        except Exception as e:
            self.logger.warning(f"LLM Manager using fallback mode: {e}")
            self.llm_manager = WorkingLLMManager()
        
        # Initialize Memory Manager with persistence
        try:
            memory_config = {
                'vector_db_path': 'memory/vector_store',
                'persistent': True,
                'collection_name': 'agent_memories',
                'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2'
            }
            self.memory_manager = AdvancedMemoryManager(memory_config)
            await self.memory_manager.initialize()
            self.logger.info("Memory Manager with vector storage ready")
        except Exception as e:
            self.logger.warning(f"Memory Manager using fallback: {e}")
            self.memory_manager = AdvancedMemoryManager({})
        
        return True
        
    async def create_autonomous_agents(self):
        """Create enhanced autonomous agents"""
        self.logger.info("Creating Autonomous AI Agents...")
        
        # Load agent profiles from memory
        agent_configs = await self.load_agent_profiles()
        
        for agent_id, config in agent_configs.items():
            try:
                # Create agent instance based on type
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
                
                # Initialize with memory context
                await agent.initialize()
                
                # Load agent's historical context
                agent_context = await self.memory_manager.get_agent_context(agent_id)
                if agent_context:
                    self.logger.info(f"Loaded {len(agent_context.get('experiences', []))} past experiences for {agent_id}")
                
                self.agents[agent_id] = agent
                self.logger.info(f"{agent_id.title()} agent autonomous and ready")
                
            except Exception as e:
                self.logger.error(f"Failed to create {agent_id} agent: {e}")
    
    async def load_agent_profiles(self):
        """Load agent profiles from memory system"""
        profiles = {}
        profiles_dir = "memory/agent_profiles"
        
        if os.path.exists(profiles_dir):
            for profile_file in os.listdir(profiles_dir):
                if profile_file.endswith('_profile.json'):
                    agent_id = profile_file.replace('_profile.json', '')
                    with open(os.path.join(profiles_dir, profile_file), 'r') as f:
                        profile = json.load(f)
                        
                        # Enhanced config with memory integration
                        profiles[agent_id] = {
                            'role': profile['role'],
                            'expertise': profile['expertise'],
                            'memory_focus': profile['memory_focus'],
                            'learning_style': profile['learning_style'],
                            'collaboration_patterns': profile['collaboration_patterns'],
                            'model': self.get_optimal_model_for_agent(agent_id),
                            'capabilities': profile['expertise'],
                            'memory_enabled': True                        }
        
        return profiles
    
    def get_optimal_model_for_agent(self, agent_id: str) -> str:
        """Get optimal model for each agent type from configuration"""
        try:
            # Load models config
            import yaml
            with open('config/models_config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            
            agent_assignments = config.get('agent_assignments', {})
            
            # Map agent_id to config keys
            mapping = {
                'architect': 'architect',
                'backend': 'backend_dev', 
                'frontend': 'frontend_dev',
                'qa': 'qa_analyst',
                'orchestrator': 'orchestrator'
            }
            
            config_key = mapping.get(agent_id, agent_id)
            if config_key in agent_assignments:
                primary_models = agent_assignments[config_key].get('primary', [])
                if primary_models:
                    return primary_models[0]  # Return first primary model
            
        except Exception as e:
            self.logger.warning(f"Failed to load model config: {e}")
        
        # Fallback model assignments 
        model_assignments = {
            'architect': 'lmstudio/mistral-small-3.1-24b-instruct-2503',
            'backend': 'lmstudio/codellama-7b-instruct',
            'frontend': 'lmstudio/codellama-7b-instruct', 
            'qa': 'lmstudio/mistral-small-3.1-24b-instruct-2503',
            'orchestrator': 'lmstudio/mistral-small-3.1-24b-instruct-2503'
        }
        
        return model_assignments.get(agent_id, 'lmstudio/mistral-small-3.1-24b-instruct-2503')
    
    async def run_autonomous_intelligence_workflow(self):
        """Run autonomous intelligence workflow with real AI capabilities"""
        self.logger.info("Starting Autonomous Intelligence Workflow...")
        
        # Define complex, realistic projects
        autonomous_projects = [
            {
                'id': 'ai_ecommerce_platform',
                'title': 'AI-Powered E-commerce Platform',
                'description': 'Build a complete AI-driven e-commerce platform with microservices architecture, real-time recommendations, dynamic pricing, inventory management, and advanced analytics.',
                'complexity': 'enterprise',
                'priority': 'high',
                'estimated_duration': '6_weeks',
                'required_agents': ['orchestrator', 'architect', 'backend', 'frontend', 'qa']
            },
            {
                'id': 'intelligent_content_cms',
                'title': 'Intelligent Content Management System',
                'description': 'Create an AI-enhanced CMS with automatic content generation, SEO optimization, user behavior analysis, and personalized content delivery.',
                'complexity': 'advanced',
                'priority': 'medium',
                'estimated_duration': '4_weeks',
                'required_agents': ['architect', 'backend', 'frontend', 'qa']
            },
            {
                'id': 'realtime_collaboration_platform',
                'title': 'Real-time Collaboration Platform',
                'description': 'Develop a collaborative workspace with real-time editing, video conferencing, AI-powered meeting summaries, and intelligent task management.',
                'complexity': 'advanced',
                'priority': 'medium',
                'estimated_duration': '5_weeks',
                'required_agents': ['orchestrator', 'architect', 'backend', 'frontend', 'qa']
            }
        ]
        
        # Execute projects with autonomous coordination
        project_results = []
        
        for project in autonomous_projects:
            self.logger.info(f"Starting autonomous project: {project['title']}")
            
            # Let orchestrator plan the project
            if 'orchestrator' in self.agents:
                planning_task = {
                    'id': f"plan_{project['id']}",
                    'title': f"Plan {project['title']}",
                    'description': f"Create comprehensive project plan for: {project['description']}",
                    'project_context': project,
                    'type': 'task_planning'
                }
                
                plan_result = await self.execute_autonomous_task('orchestrator', planning_task)
                project['plan'] = plan_result
            
            # Execute coordinated development
            development_tasks = await self.generate_development_tasks(project)
            task_results = await self.execute_coordinated_tasks(development_tasks)
            
            project_result = {
                'project': project,
                'tasks_completed': len(task_results),
                'success_rate': sum(1 for r in task_results if r.get('success', False)) / len(task_results),
                'outputs_generated': self.count_project_outputs(project['id']),
                'completion_time': datetime.now().isoformat()
            }
            
            project_results.append(project_result)
            self.logger.info(f"Project completed: {project['title']} - {project_result['success_rate']*100:.1f}% success")
        
        return project_results
    
    async def generate_development_tasks(self, project: Dict) -> List[Dict]:
        """Generate development tasks based on project requirements"""
        tasks = []
        
        base_tasks = {
            'architect': {
                'title': f"Design Architecture for {project['title']}",
                'description': f"Create scalable architecture design for: {project['description']}",
                'type': 'system_design'
            },
            'backend': {
                'title': f"Implement Backend for {project['title']}",
                'description': f"Develop robust backend systems for: {project['description']}",
                'type': 'api_development'
            },
            'frontend': {
                'title': f"Create Frontend for {project['title']}",
                'description': f"Build intuitive user interface for: {project['description']}",
                'type': 'component_development'
            },
            'qa': {
                'title': f"Test {project['title']}",
                'description': f"Design comprehensive testing strategy for: {project['description']}",
                'type': 'test_automation'
            }
        }
        
        for agent_id in project['required_agents']:
            if agent_id in base_tasks and agent_id in self.agents:
                task = base_tasks[agent_id].copy()
                task['id'] = f"{project['id']}_{agent_id}_task"
                task['project_id'] = project['id']
                task['agent'] = agent_id
                task['priority'] = project['priority']
                tasks.append(task)
        
        return tasks
    
    async def execute_coordinated_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """Execute tasks with intelligent coordination"""
        results = []
        
        # Execute high-priority tasks first
        high_priority_tasks = [t for t in tasks if t.get('priority') == 'high']
        medium_priority_tasks = [t for t in tasks if t.get('priority') == 'medium']
        
        # Execute in coordinated batches
        for task_batch in [high_priority_tasks, medium_priority_tasks]:
            if task_batch:
                batch_tasks = []
                for task in task_batch:
                    agent_id = task['agent']
                    batch_tasks.append(self.execute_autonomous_task(agent_id, task))
                
                batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, Exception):
                        self.logger.error(f"Task failed: {result}")
                        results.append({'success': False, 'error': str(result)})
                    else:
                        results.append(result)
        
        return results
    
    async def execute_autonomous_task(self, agent_id: str, task: Dict) -> Dict:
        """Execute task with autonomous intelligence"""
        agent = self.agents.get(agent_id)
        if not agent:
            return {'success': False, 'error': f'Agent {agent_id} not available'}
        
        try:
            # Get memory context for intelligent execution
            context = await self.memory_manager.get_agent_context(agent_id)
            
            # Execute task with full context
            self.logger.info(f"{agent_id.title()} executing: {task['title']}")
            result = await agent.execute_task(task)
            
            # Store experience in memory for learning
            await self.memory_manager.store_experience(
                agent_id,
                task,
                result,
                {
                    'success': True,
                    'autonomous': True,
                    'project_id': task.get('project_id'),
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            result['success'] = True
            return result
            
        except Exception as e:
            self.logger.error(f"Autonomous task failed for {agent_id}: {e}")
            return {'success': False, 'error': str(e)}
    
    def count_project_outputs(self, project_id: str) -> int:
        """Count output files generated for a project"""
        total_files = 0
        
        # Count files in agent outputs
        outputs_dir = "agent_outputs"
        if os.path.exists(outputs_dir):
            for agent_dir in os.listdir(outputs_dir):
                agent_path = os.path.join(outputs_dir, agent_dir)
                if os.path.isdir(agent_path):
                    project_files = [f for f in os.listdir(agent_path) if project_id in f.lower()]
                    total_files += len(project_files)
        
        return total_files
    
    async def generate_intelligence_report(self, project_results: List[Dict]) -> Dict:
        """Generate comprehensive intelligence report"""
        self.logger.info("Generating Autonomous Intelligence Report...")
        
        total_projects = len(project_results)
        total_tasks = sum(p['tasks_completed'] for p in project_results)
        average_success = sum(p['success_rate'] for p in project_results) / total_projects if total_projects > 0 else 0
        total_outputs = sum(p['outputs_generated'] for p in project_results)
        
        # Memory system statistics
        memory_stats = await self.get_memory_statistics()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'autonomous_session': {
                'projects_completed': total_projects,
                'tasks_executed': total_tasks,
                'average_success_rate': round(average_success * 100, 2),
                'files_generated': total_outputs,
                'agents_active': len(self.agents)
            },
            'memory_intelligence': memory_stats,
            'agent_performance': await self.get_agent_performance(),
            'project_details': project_results,
            'system_status': 'autonomous_operational'
        }
        
        # Save report
        report_file = f"reports/autonomous_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("reports", exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Intelligence report saved: {report_file}")
        return report
    
    async def get_memory_statistics(self) -> Dict:
        """Get memory system statistics"""
        try:
            stats = {
                'profiles_loaded': len(os.listdir('memory/agent_profiles')) if os.path.exists('memory/agent_profiles') else 0,
                'experiences_stored': len(os.listdir('memory/experiences')) if os.path.exists('memory/experiences') else 0,
                'knowledge_base_active': os.path.exists('memory/knowledge_base/core_knowledge.json'),
                'vector_db_connected': await self.check_vector_db_connection()
            }
            return stats
        except Exception as e:
            return {'error': str(e)}
    
    async def check_vector_db_connection(self) -> bool:
        """Check vector database connection"""
        try:
            import requests
            response = requests.get("http://localhost:6333/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    async def get_agent_performance(self) -> Dict:
        """Get agent performance metrics"""
        performance = {}
        
        for agent_id, agent in self.agents.items():
            try:
                # Get agent context for performance metrics
                context = await self.memory_manager.get_agent_context(agent_id)
                experiences = context.get('experiences', []) if context else []
                
                performance[agent_id] = {
                    'experiences_count': len(experiences),
                    'successful_tasks': len([e for e in experiences if e.get('metadata', {}).get('success')]),
                    'specialization': agent.config.get('expertise', []),
                    'status': 'active'
                }
            except Exception as e:
                performance[agent_id] = {'status': 'error', 'error': str(e)}
        
        return performance

async def main():
    """Main autonomous AI workflow"""
    workflow = AutonomousAIWorkflow()
    
    try:
        # Initialize AI systems
        await workflow.initialize_ai_systems()
        
        # Create autonomous agents
        await workflow.create_autonomous_agents()
        
        # Run autonomous intelligence workflow
        project_results = await workflow.run_autonomous_intelligence_workflow()
        
        # Generate intelligence report
        report = await workflow.generate_intelligence_report(project_results)
        
        # Display results
        print("\n" + "="*80)
        print("AUTONOMOUS AI WORKFLOW COMPLETED!")
        print("="*80)
        print(f"Projects Completed: {report['autonomous_session']['projects_completed']}")
        print(f"Tasks Executed: {report['autonomous_session']['tasks_executed']}")
        print(f"Success Rate: {report['autonomous_session']['average_success_rate']}%")
        print(f"Files Generated: {report['autonomous_session']['files_generated']}")
        print(f"Active Agents: {report['autonomous_session']['agents_active']}")
        print(f"Memory System: {'Active' if report['memory_intelligence']['vector_db_connected'] else 'Fallback'}")
        print("="*80)
        print("AUTONOMOUS INTELLIGENCE SUCCESSFULLY DEMONSTRATED!")
        print("="*80)
        
    except Exception as e:
        workflow.logger.error(f"Autonomous workflow failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())


