"""
Hybrid Ultimate Copilot System
Demonstrates integration between custom agents and CodeGPT platform
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.enhanced_system_manager import EnhancedSystemManager
from core.enhanced_llm_manager import EnhancedLLMManager
from core.advanced_memory_manager import AdvancedMemoryManager
from backend.agent_manager import EnhancedAgentManager
from integrations.codegpt_bridge import CodeGPTBridge, HybridAgentManager
from integrations.void_integration import VoidEditorIntegration
from integrations.vscode_integration import VSCodeIntegration
from utils.logger import setup_logging
from utils.config import load_config

class HybridUltimateCopilot:
    """Ultimate Copilot System with CodeGPT integration"""
    
    def __init__(self):
        self.logger = None
        self.config = None
        self.system_manager = None
        self.llm_manager = None
        self.memory_manager = None
        self.agent_manager = None
        self.codegpt_bridge = None
        self.hybrid_manager = None
        
        # Integrations
        self.void_integration = None
        self.vscode_integration = None
        
        self.running = False
    
    async def initialize(self):
        """Initialize the hybrid system"""
        print("Starting Hybrid Ultimate Copilot System...")
        
        # Setup logging
        self.logger = setup_logging()
        self.logger.info("=== HYBRID ULTIMATE COPILOT SYSTEM STARTUP ===")
        
        # Load configuration
        await self.load_configuration()
        
        # Initialize core managers
        await self.initialize_core_managers()
        
        # Initialize CodeGPT bridge if enabled
        await self.initialize_codegpt_bridge()
        
        # Initialize hybrid agent manager
        await self.initialize_hybrid_manager()
        
        # Initialize integrations
        await self.initialize_integrations()
        
        # Start monitoring
        await self.start_monitoring()
        
        self.running = True
        self.logger.info("Hybrid Ultimate Copilot System fully initialized!")
    
    async def load_configuration(self):
        """Load system and hybrid configuration"""
        self.config = load_config()
        
        # Load hybrid-specific config
        hybrid_config_path = Path("config/hybrid_config.yaml")
        if hybrid_config_path.exists():
            import yaml
            with open(hybrid_config_path, 'r', encoding='utf-8') as f:
                hybrid_config = yaml.safe_load(f)
            
            # Merge with main config
            self.config['hybrid'] = hybrid_config
            self.logger.info("Hybrid configuration loaded")
        else:
            self.logger.warning("Hybrid config not found, using defaults")
            self.config['hybrid'] = {'codegpt': {'enabled': False}}
    
    async def initialize_core_managers(self):
        """Initialize core system managers"""
        self.logger.info("Initializing core managers...")
        
        # LLM Manager
        self.llm_manager = EnhancedLLMManager(self.config)
        await self.llm_manager.initialize()
        
        # Memory Manager
        self.memory_manager = AdvancedMemoryManager()
        await self.memory_manager.initialize()
        
        # Agent Manager (custom)
        self.agent_manager = EnhancedAgentManager(
            llm_manager=self.llm_manager,
            memory_manager=self.memory_manager
        )
        await self.agent_manager.initialize()
        
        # System Manager
        self.system_manager = EnhancedSystemManager(
            llm_manager=self.llm_manager,
            memory_manager=self.memory_manager,
            agent_manager=self.agent_manager
        )
        await self.system_manager.initialize()
        
        self.logger.info("Core managers initialized")
    
    async def initialize_codegpt_bridge(self):
        """Initialize CodeGPT bridge if enabled"""
        codegpt_config = self.config['hybrid'].get('codegpt', {})
        
        if not codegpt_config.get('enabled', False):
            self.logger.info("📴 CodeGPT integration disabled")
            return
        
        # Check for API credentials
        api_key = os.getenv('CODEGPT_API_KEY') or codegpt_config.get('api_key')
        org_id = os.getenv('CODEGPT_ORG_ID') or codegpt_config.get('org_id')
        
        if not api_key or not org_id:
            self.logger.error("CodeGPT API credentials not found!")
            self.logger.info("Please set CODEGPT_API_KEY and CODEGPT_ORG_ID environment variables")
            self.logger.info("Or add them to config/hybrid_config.yaml")
            return
        
        try:
            self.logger.info("🔗 Initializing CodeGPT bridge...")
            self.codegpt_bridge = CodeGPTBridge(api_key, org_id)
            await self.codegpt_bridge.initialize()
            self.logger.info("CodeGPT bridge initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize CodeGPT bridge: {e}")
            self.codegpt_bridge = None
    
    async def initialize_hybrid_manager(self):
        """Initialize hybrid agent manager"""
        if self.codegpt_bridge:
            self.logger.info("🤝 Initializing hybrid agent manager...")
            self.hybrid_manager = HybridAgentManager(
                self.agent_manager,
                self.codegpt_bridge
            )
            await self.hybrid_manager.initialize()
            self.logger.info("Hybrid agent manager initialized")
        else:
            self.logger.info("Using custom agents only (CodeGPT not available)")
            self.hybrid_manager = self.agent_manager
    
    async def initialize_integrations(self):
        """Initialize editor integrations with proper priority"""
        self.logger.info("🔌 Initializing editor integrations...")
        
        # Priority 1: Void Editor (if enabled)
        if self.config['hybrid']['integration']['void_editor']['enabled']:
            try:
                self.void_integration = VoidEditorIntegration(self.config)
                await self.void_integration.initialize()
                self.logger.info("Void Editor integration active (Priority 1)")
            except Exception as e:
                self.logger.warning(f"Void Editor integration failed: {e}")
        
        # Priority 2: VS Code Insiders for swarm automation
        if self.config['hybrid']['integration']['vscode_insiders']['enabled']:
            try:
                self.vscode_integration = VSCodeIntegration(
                    self.config,
                    self.system_manager
                )
                await self.vscode_integration.initialize()
                
                # Enable swarm mode if configured
                if self.config['hybrid']['integration']['vscode_insiders']['swarm_mode']:
                    await self.vscode_integration.enable_swarm_mode()
                
                self.logger.info("VS Code Insiders integration active (Priority 2)")
            except Exception as e:
                self.logger.warning(f"VS Code integration failed: {e}")
        
        self.logger.info("🔌 Editor integrations initialized")
    
    async def start_monitoring(self):
        """Start system monitoring and health checks"""
        self.logger.info("Starting system monitoring...")
        
        # Start monitoring tasks
        asyncio.create_task(self.monitor_system_health())
        asyncio.create_task(self.monitor_hybrid_performance())
        
        self.logger.info("Monitoring active")
    
    async def monitor_system_health(self):
        """Monitor overall system health"""
        while self.running:
            try:
                # Check core managers
                await self.llm_manager.health_check()
                await self.memory_manager.health_check()
                
                # Check hybrid bridge if available
                if self.codegpt_bridge:
                    # Simple connectivity test
                    pass
                
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
                await asyncio.sleep(60)
    
    async def monitor_hybrid_performance(self):
        """Monitor hybrid system performance"""
        while self.running:
            try:
                if self.hybrid_manager and hasattr(self.hybrid_manager, 'get_agent_status'):
                    status = await self.hybrid_manager.get_agent_status()
                    # Log performance metrics
                    custom_agents = status.get('custom_agents', {})
                    codegpt_agents = status.get('codegpt_agents', {})
                    
                    self.logger.debug(f"System Status - Custom: {len(custom_agents)} agents, "
                                    f"CodeGPT: {codegpt_agents.get('available_agents', 0)} agents")
                
                await asyncio.sleep(120)  # Check every 2 minutes
            except Exception as e:
                self.logger.error(f"Performance monitoring failed: {e}")
                await asyncio.sleep(180)
    
    async def demonstrate_hybrid_capabilities(self):
        """Demonstrate the hybrid system capabilities"""
        self.logger.info("Demonstrating hybrid capabilities...")
        
        # Example tasks for different agent types
        demo_tasks = [
            {
                'id': 'demo_code_review',
                'title': 'Code Review Task',
                'description': 'Review this Python function for best practices and security',
                'type': 'code_review'
            },
            {
                'id': 'demo_orchestration',
                'title': 'Project Orchestration',
                'description': 'Plan and coordinate a new web application project',
                'type': 'project_orchestration'
            },
            {
                'id': 'demo_documentation',
                'title': 'Generate Documentation',
                'description': 'Create API documentation for the hybrid system',
                'type': 'documentation'
            }
        ]
        
        for task in demo_tasks:
            try:
                self.logger.info(f"Executing demo task: {task['title']}")
                result = await self.hybrid_manager.execute_task(task)
                self.logger.info(f"Task completed: {result.get('type', 'unknown')}")
            except Exception as e:
                self.logger.error(f"Demo task failed: {e}")
    
    async def run(self):
        """Main run loop"""
        try:
            await self.initialize()
            
            # Run demonstrations
            await self.demonstrate_hybrid_capabilities()
            
            # Keep system running
            self.logger.info("Hybrid Ultimate Copilot System is now running!")
            self.logger.info("Use the dashboard or integrations to interact with the system")
            
            while self.running:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Shutdown requested by user")
        except Exception as e:
            self.logger.error(f"System error: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.logger.info("🛑 Shutting down Hybrid Ultimate Copilot System...")
        self.running = False
        
        # Close integrations
        if self.void_integration:
            await self.void_integration.stop()
        
        if self.vscode_integration:
            await self.vscode_integration.stop()
        
        # Close CodeGPT bridge
        if self.codegpt_bridge:
            await self.codegpt_bridge.close()
        
        # Stop managers
        if self.system_manager:
            await self.system_manager.stop()
        
        self.logger.info("Hybrid system shutdown complete")

async def main():
    """Main entry point"""
    system = HybridUltimateCopilot()
    await system.run()

if __name__ == "__main__":
    # Set environment variables if not already set
    if not os.getenv('CODEGPT_API_KEY'):
        print("Note: Set CODEGPT_API_KEY environment variable to enable CodeGPT integration")
    if not os.getenv('CODEGPT_ORG_ID'):
        print("Note: Set CODEGPT_ORG_ID environment variable to enable CodeGPT integration")
    
    print("Starting Hybrid Ultimate Copilot System...")
    print("🔗 This version integrates custom agents with CodeGPT platform")
    print("System will prioritize Void Editor and VS Code Insiders integration")
    print("CodeGPT agents will handle simple tasks, custom agents handle complex workflows")
    print()
    
    asyncio.run(main())


