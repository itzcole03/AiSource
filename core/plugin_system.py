"""
Plugin System for Custom Agents
Enables dynamic loading and management of custom agent plugins
"""

import asyncio
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Type, Any
import inspect
import json
from datetime import datetime

from agents.base_agent import BaseAgent

class PluginManager:
    def __init__(self, plugin_directory: str = "plugins"):
        self.plugin_directory = Path(plugin_directory)
        self.logger = logging.getLogger("PluginManager")
        
        # Plugin registry
        self.registered_plugins: Dict[str, Dict] = {}
        self.loaded_agents: Dict[str, BaseAgent] = {}
        self.plugin_configs: Dict[str, Dict] = {}
        
        # Plugin metadata
        self.plugin_metadata: Dict[str, Dict] = {}
        
    async def initialize(self):
        """Initialize plugin system"""
        self.logger.info("[PLUGIN] Initializing Plugin System...")
        
        # Create plugin directory if it doesn't exist
        self.plugin_directory.mkdir(exist_ok=True)
        
        # Create example plugin structure
        await self.create_example_plugin()
        
        # Discover and load plugins
        await self.discover_plugins()
        
        self.logger.info(f"[OK] Plugin System initialized with {len(self.registered_plugins)} plugins")
    
    async def create_example_plugin(self):
        """Create an example plugin for reference"""
        example_dir = self.plugin_directory / "example_agent"
        example_dir.mkdir(exist_ok=True)
        
        # Plugin manifest
        manifest = {
            "name": "Example Agent",
            "version": "1.0.0",
            "description": "An example custom agent plugin",
            "author": "Ultimate Copilot Team",
            "agent_class": "ExampleAgent",
            "capabilities": ["example_task", "demo_functionality"],
            "dependencies": [],
            "config_schema": {
                "example_setting": {"type": "string", "default": "default_value"},
                "enable_feature": {"type": "boolean", "default": True}
            }
        }
        
        manifest_file = example_dir / "manifest.json"
        if not manifest_file.exists():
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)
        
        # Example agent implementation
        agent_file = example_dir / "agent.py"
        if not agent_file.exists():
            agent_code = '''"""
Example Custom Agent Plugin
"""

from agents.base_agent import BaseAgent
from typing import Dict

class ExampleAgent(BaseAgent):
    async def agent_initialize(self):
        """Initialize example agent"""
        self.example_setting = self.config.get('example_setting', 'default_value')
        self.enable_feature = self.config.get('enable_feature', True)
        
        self.capabilities = ['example_task', 'demo_functionality']
        
        self.logger.info(f"Example agent initialized with setting: {self.example_setting}")
    
    async def process_task(self, task: Dict, context: Dict) -> Dict:
        """Process tasks for example agent"""
        task_type = self.determine_task_type(task)
        
        if task_type == "example_task":
            return await self.handle_example_task(task, context)
        elif task_type == "demo_functionality":
            return await self.handle_demo_functionality(task, context)
        else:
            return await self.general_example_task(task, context)
    
    async def handle_example_task(self, task: Dict, context: Dict) -> Dict:
        """Handle example task type"""
        prompt = f"""
        As an example agent, process the following task:
        
        Task: {task.get('title', '')}
        Description: {task.get('description', '')}
        
        Provide a helpful response demonstrating custom agent capabilities.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=500)
        
        return {
            'type': 'example_task',
            'response': response,
            'agent_setting': self.example_setting,
            'feature_enabled': self.enable_feature,
            'success': True,
            'summary': f"Example task completed: {task.get('title', 'Unknown')}"
        }
    
    async def handle_demo_functionality(self, task: Dict, context: Dict) -> Dict:
        """Handle demo functionality"""
        return {
            'type': 'demo_functionality',
            'message': 'Demo functionality executed successfully',
            'timestamp': datetime.now().isoformat(),
            'success': True,
            'summary': 'Demo functionality completed'
        }
    
    async def general_example_task(self, task: Dict, context: Dict) -> Dict:
        """Handle general example tasks"""
        prompt = f"""
        As a custom example agent, help with:
        
        Task: {task.get('title', '')}
        Description: {task.get('description', '')}
        
        Provide guidance using custom agent capabilities.
        """
        
        response = await self.generate_llm_response(prompt, max_tokens=400)
        
        return {
            'type': 'general_example',
            'guidance': response,
            'success': True,
            'summary': f"General example task completed: {task.get('title', 'task')}"
        }
    
    def determine_task_type(self, task: Dict) -> str:
        """Determine task type for example agent"""
        description = task.get('description', '').lower()
        title = task.get('title', '').lower()
        
        if any(word in description + title for word in ['example', 'test', 'demo']):
            return "example_task"
        elif any(word in description + title for word in ['demo', 'functionality', 'feature']):
            return "demo_functionality"
        else:
            return "general"
    
    async def agent_health_check(self):
        """Example agent health check"""
        test_prompt = "Hello from example agent"
        response = await self.generate_llm_response(test_prompt, max_tokens=10)
        
        if not response or len(response) < 5:
            raise Exception("Example agent health check failed")
    
    async def agent_cleanup(self):
        """Example agent cleanup"""
        self.logger.info("Example agent cleanup completed")
'''
            
            with open(agent_file, 'w') as f:
                f.write(agent_code)
    
    async def discover_plugins(self):
        """Discover available plugins"""
        self.logger.info("[DISCOVERY] Discovering plugins...")
        
        for plugin_dir in self.plugin_directory.iterdir():
            if plugin_dir.is_dir() and not plugin_dir.name.startswith('.'):
                await self.load_plugin(plugin_dir)
    
    async def load_plugin(self, plugin_dir: Path):
        """Load a specific plugin"""
        plugin_name = plugin_dir.name
        
        try:
            # Load manifest
            manifest_file = plugin_dir / "manifest.json"
            if not manifest_file.exists():
                self.logger.warning(f"Plugin {plugin_name} missing manifest.json")
                return
            
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            # Validate manifest
            if not self.validate_manifest(manifest):
                self.logger.error(f"Invalid manifest for plugin {plugin_name}")
                return
            
            # Load agent module
            agent_file = plugin_dir / "agent.py"
            if not agent_file.exists():
                self.logger.warning(f"Plugin {plugin_name} missing agent.py")
                return
            
            # Import the agent class
            spec = importlib.util.spec_from_file_location(
                f"plugin_{plugin_name}", 
                agent_file
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get agent class
            agent_class_name = manifest.get('agent_class')
            if not hasattr(module, agent_class_name):
                self.logger.error(f"Agent class {agent_class_name} not found in plugin {plugin_name}")
                return
            
            agent_class = getattr(module, agent_class_name)
            
            # Validate agent class
            if not issubclass(agent_class, BaseAgent):
                self.logger.error(f"Agent class {agent_class_name} must inherit from BaseAgent")
                return
            
            # Register plugin
            self.registered_plugins[plugin_name] = {
                'manifest': manifest,
                'agent_class': agent_class,
                'plugin_dir': plugin_dir,
                'loaded_at': datetime.now().isoformat()
            }
            
            self.plugin_metadata[plugin_name] = manifest
            
            self.logger.info(f"[OK] Plugin loaded: {manifest.get('name', plugin_name)} v{manifest.get('version', '1.0.0')}")
            
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
    
    def validate_manifest(self, manifest: Dict) -> bool:
        """Validate plugin manifest"""
        required_fields = ['name', 'version', 'agent_class', 'capabilities']
        
        for field in required_fields:
            if field not in manifest:
                return False
        
        return True
    
    async def create_agent_instance(self, plugin_name: str, agent_id: str, config: Dict) -> Optional[BaseAgent]:
        """Create an instance of a plugin agent"""
        if plugin_name not in self.registered_plugins:
            self.logger.error(f"Plugin {plugin_name} not registered")
            return None
        
        try:
            plugin_info = self.registered_plugins[plugin_name]
            agent_class = plugin_info['agent_class']
            
            # Merge plugin config with provided config
            plugin_config = self.merge_plugin_config(plugin_name, config)
            
            # Create agent instance
            agent = agent_class(
                agent_id=agent_id,
                config=plugin_config,
                llm_manager=None,  # Will be set by agent manager
                memory_manager=None  # Will be set by agent manager
            )
            
            self.loaded_agents[agent_id] = agent
            
            self.logger.info(f"[OK] Created agent instance: {agent_id} from plugin {plugin_name}")
            return agent
            
        except Exception as e:
            self.logger.error(f"Failed to create agent instance from plugin {plugin_name}: {e}")
            return None
    
    def merge_plugin_config(self, plugin_name: str, config: Dict) -> Dict:
        """Merge plugin default config with provided config"""
        plugin_info = self.registered_plugins[plugin_name]
        manifest = plugin_info['manifest']
        
        # Start with default config from manifest
        merged_config = {}
        
        config_schema = manifest.get('config_schema', {})
        for key, schema in config_schema.items():
            merged_config[key] = schema.get('default')
        
        # Override with provided config
        merged_config.update(config)
        
        # Add plugin metadata
        merged_config['plugin_name'] = plugin_name
        merged_config['plugin_version'] = manifest.get('version')
        merged_config['capabilities'] = manifest.get('capabilities', [])
        
        return merged_config
    
    def get_available_plugins(self) -> List[Dict]:
        """Get list of available plugins"""
        return [
            {
                'name': plugin_name,
                'manifest': info['manifest'],
                'loaded_at': info['loaded_at']
            }
            for plugin_name, info in self.registered_plugins.items()
        ]
    
    def get_plugin_capabilities(self, plugin_name: str) -> List[str]:
        """Get capabilities of a specific plugin"""
        if plugin_name not in self.registered_plugins:
            return []
        
        return self.registered_plugins[plugin_name]['manifest'].get('capabilities', [])
    
    async def reload_plugin(self, plugin_name: str):
        """Reload a specific plugin"""
        if plugin_name not in self.registered_plugins:
            self.logger.error(f"Plugin {plugin_name} not found")
            return
        
        plugin_dir = self.registered_plugins[plugin_name]['plugin_dir']
        
        # Remove from registry
        del self.registered_plugins[plugin_name]
        
        # Reload
        await self.load_plugin(plugin_dir)
    
    async def unload_plugin(self, plugin_name: str):
        """Unload a specific plugin"""
        if plugin_name not in self.registered_plugins:
            return
        
        # Stop any running agent instances
        agents_to_remove = []
        for agent_id, agent in self.loaded_agents.items():
            if hasattr(agent, 'config') and agent.config.get('plugin_name') == plugin_name:
                agents_to_remove.append(agent_id)
                try:
                    await agent.stop()
                except:
                    pass
        
        for agent_id in agents_to_remove:
            del self.loaded_agents[agent_id]
        
        # Remove from registry
        del self.registered_plugins[plugin_name]
        
        self.logger.info(f"🗑️ Plugin {plugin_name} unloaded")
    
    async def shutdown(self):
        """Shutdown plugin system"""
        self.logger.info("Plugin System shutdown complete")
        
        # Shutdown all loaded agents
        for agent_id, agent in self.loaded_agents.items():
            try:
                if hasattr(agent, 'shutdown'):
                    if asyncio.iscoroutinefunction(agent.shutdown):
                        await agent.shutdown()
                    else:
                        agent.shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down plugin agent {agent_id}: {e}")
        
        self.loaded_agents.clear()
        self.registered_plugins.clear()
    
    def get_status(self) -> Dict:
        """Get plugin system status"""
        return {
            'total_plugins': len(self.registered_plugins),
            'loaded_agents': len(self.loaded_agents),
            'available_plugins': list(self.registered_plugins.keys()),
            'plugin_metadata': self.plugin_metadata
        }