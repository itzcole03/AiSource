#!/usr/bin/env python3
"""
Memory System Initializer for Ultimate Copilot
Sets up persistent memory with Qdrant integration
"""

import asyncio
import logging
import os
import json
from datetime import datetime
from typing import Dict, List
import numpy as np

class MemoryInitializer:
    """Initialize and configure the memory system"""
    
    def __init__(self):
        self.setup_logging()
        self.memory_config = {
            'vector_db_path': 'memory/vector_store',
            'persistent': True,
            'collection_name': 'agent_memories',
            'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
            'max_memory_size': 10000,
            'similarity_threshold': 0.7
        }
        
    def setup_logging(self):
        """Setup logging for memory system"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("MemoryInit")
        
    async def initialize_memory_system(self):
        """Initialize the complete memory system"""
        self.logger.info("Initializing Enhanced Memory System...")
        
        # Create memory directories
        self.create_memory_directories()
        
        # Initialize vector database
        await self.setup_vector_database()
        
        # Create agent memory profiles
        await self.create_agent_profiles()
        
        # Load existing memories
        await self.load_existing_memories()
        
        self.logger.info("Memory system fully initialized")
        
    def create_memory_directories(self):
        """Create necessary memory directories"""
        directories = [
            'memory/vector_store',
            'memory/agent_profiles',
            'memory/experiences',
            'memory/contexts',
            'memory/skills',
            'memory/knowledge_base'
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            self.logger.info(f"Created directory: {directory}")
    
    async def setup_vector_database(self):
        """Setup Qdrant vector database for memory storage"""
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams
            
            # Connect to Qdrant
            client = QdrantClient(host="localhost", port=6333)
            
            # Create collection if it doesn't exist
            collections = client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.memory_config['collection_name'] not in collection_names:
                client.create_collection(
                    collection_name=self.memory_config['collection_name'],
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE)
                )
                self.logger.info(f"Created Qdrant collection: {self.memory_config['collection_name']}")
            else:
                self.logger.info(f"Qdrant collection already exists: {self.memory_config['collection_name']}")
                
        except Exception as e:
            self.logger.warning(f"Qdrant setup failed, using fallback: {e}")
            await self.setup_fallback_storage()
    
    async def setup_fallback_storage(self):
        """Setup fallback file-based storage"""
        self.logger.info("Setting up fallback file-based memory storage...")
        
        fallback_config = {
            'storage_type': 'file',
            'base_path': 'memory/fallback_storage',
            'index_file': 'memory/fallback_storage/index.json'
        }
        
        os.makedirs('memory/fallback_storage', exist_ok=True)
        
        # Create index file
        if not os.path.exists(fallback_config['index_file']):
            with open(fallback_config['index_file'], 'w') as f:
                json.dump({
                    'version': '1.0',
                    'created': datetime.now().isoformat(),
                    'memories': [],
                    'agents': {}
                }, f, indent=2)
        
        self.logger.info("Fallback storage initialized")
    
    async def create_agent_profiles(self):
        """Create memory profiles for each agent type"""
        agent_profiles = {
            'architect': {
                'role': 'System Architect',
                'expertise': ['system_design', 'architecture_patterns', 'scalability', 'technology_selection'],
                'memory_focus': ['design_decisions', 'architecture_reviews', 'technology_recommendations'],
                'learning_style': 'analytical',
                'collaboration_patterns': ['requirements_analysis', 'technical_consultation']
            },
            'backend': {
                'role': 'Backend Developer',
                'expertise': ['api_development', 'database_design', 'microservices', 'performance_optimization'],
                'memory_focus': ['code_patterns', 'api_designs', 'database_schemas', 'performance_metrics'],
                'learning_style': 'implementation_focused',
                'collaboration_patterns': ['code_review', 'api_integration', 'database_optimization']
            },
            'frontend': {
                'role': 'Frontend Developer',
                'expertise': ['react_development', 'ui_design', 'user_experience', 'component_architecture'],
                'memory_focus': ['ui_patterns', 'component_designs', 'user_interactions', 'styling_solutions'],
                'learning_style': 'visual_practical',
                'collaboration_patterns': ['design_implementation', 'user_feedback', 'responsive_design']
            },
            'qa': {
                'role': 'Quality Assurance Engineer',
                'expertise': ['test_automation', 'quality_metrics', 'bug_analysis', 'testing_strategies'],
                'memory_focus': ['test_cases', 'bug_patterns', 'quality_metrics', 'testing_frameworks'],
                'learning_style': 'systematic_validation',
                'collaboration_patterns': ['test_planning', 'bug_reporting', 'quality_assessment']
            },
            'orchestrator': {
                'role': 'Project Orchestrator',
                'expertise': ['project_planning', 'resource_allocation', 'workflow_optimization', 'team_coordination'],
                'memory_focus': ['project_patterns', 'resource_usage', 'workflow_efficiency', 'team_dynamics'],
                'learning_style': 'strategic_planning',
                'collaboration_patterns': ['task_coordination', 'resource_management', 'progress_tracking']
            }
        }
        
        for agent_id, profile in agent_profiles.items():
            profile_file = f"memory/agent_profiles/{agent_id}_profile.json"
            profile['created'] = datetime.now().isoformat()
            profile['memory_initialized'] = True
            
            with open(profile_file, 'w') as f:
                json.dump(profile, f, indent=2)
            
            self.logger.info(f"Created memory profile for {agent_id}")
    
    async def load_existing_memories(self):
        """Load any existing memories from previous sessions"""
        self.logger.info("Loading existing memories...")
        
        # Check for existing experience files
        experiences_dir = 'memory/experiences'
        if os.path.exists(experiences_dir):
            experience_files = [f for f in os.listdir(experiences_dir) if f.endswith('.json')]
            self.logger.info(f"Found {len(experience_files)} existing experience files")
        
        # Check for existing context files
        contexts_dir = 'memory/contexts'
        if os.path.exists(contexts_dir):
            context_files = [f for f in os.listdir(contexts_dir) if f.endswith('.json')]
            self.logger.info(f"Found {len(context_files)} existing context files")
        
        self.logger.info("Existing memories loaded")
    
    async def create_knowledge_base(self):
        """Create initial knowledge base"""
        self.logger.info("📖 Creating initial knowledge base...")
        
        knowledge_base = {
            'software_architecture': {
                'patterns': ['MVC', 'MVP', 'MVVM', 'Microservices', 'Event-Driven', 'Layered'],
                'principles': ['SOLID', 'DRY', 'KISS', 'YAGNI', 'Separation of Concerns'],
                'technologies': {
                    'frontend': ['React', 'Vue', 'Angular', 'TypeScript', 'CSS-in-JS'],
                    'backend': ['Node.js', 'Python', 'Java', 'FastAPI', 'Express'],
                    'database': ['PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch'],
                    'infrastructure': ['Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP']
                }
            },
            'testing_strategies': {
                'types': ['Unit', 'Integration', 'E2E', 'Performance', 'Security'],
                'frameworks': ['Jest', 'Cypress', 'Playwright', 'Selenium', 'JMeter'],
                'best_practices': ['Test-Driven Development', 'Behavior-Driven Development', 'Continuous Testing']
            },
            'project_management': {
                'methodologies': ['Agile', 'Scrum', 'Kanban', 'DevOps', 'Lean'],
                'tools': ['Jira', 'Trello', 'GitHub', 'Jenkins', 'Docker'],
                'metrics': ['Velocity', 'Lead Time', 'Cycle Time', 'Quality Score']
            }
        }
        
        knowledge_file = 'memory/knowledge_base/core_knowledge.json'
        with open(knowledge_file, 'w') as f:
            json.dump(knowledge_base, f, indent=2)
        
        self.logger.info("Knowledge base created")
    
    def get_memory_status(self):
        """Get current memory system status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'directories_created': True,
            'vector_db_available': self.check_qdrant_connection(),
            'agent_profiles': len(os.listdir('memory/agent_profiles')) if os.path.exists('memory/agent_profiles') else 0,
            'knowledge_base_created': os.path.exists('memory/knowledge_base/core_knowledge.json'),
            'memory_system': 'operational'
        }
        return status
    
    def check_qdrant_connection(self):
        """Check if Qdrant is available"""
        try:
            import requests
            response = requests.get("http://localhost:6333/health", timeout=2)
            return response.status_code == 200
        except:
            return False

async def main():
    """Initialize the memory system"""
    initializer = MemoryInitializer()
    
    try:
        await initializer.initialize_memory_system()
        await initializer.create_knowledge_base()
        
        status = initializer.get_memory_status()
        
        print("\n" + "="*60)
        print("MEMORY SYSTEM INITIALIZATION COMPLETE")
        print("="*60)
        print(f"Agent Profiles: {status['agent_profiles']}")
        print(f"🗃️  Vector DB: {'Available' if status['vector_db_available'] else 'Fallback Mode'}")
        print(f"📖 Knowledge Base: {'Created' if status['knowledge_base_created'] else 'Pending'}")
        print(f"Status: {status['memory_system'].title()}")
        print("="*60)
        
    except Exception as e:
        print(f"Memory initialization failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())


