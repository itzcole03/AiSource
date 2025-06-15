#!/usr/bin/env python3
"""
Plugin Manager for Dashboard Plugins

Manages plugin loading, configuration, and lifecycle.
"""

import importlib
import importlib.util
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Type, Union
import logging
import yaml

from .base_plugin import BasePlugin

class PluginManager:
    """Manages dashboard plugins"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logging.getLogger("PluginManager")
        self.plugins: Dict[str, BasePlugin] = {}
        self.plugin_configs: Dict[str, Dict[str, Any]] = {}
        self.dashboard_context = {}
        
        # Load plugin configurations
        if config_file and Path(config_file).exists():
            self.load_config(config_file)
    
    def load_config(self, config_file: str) -> None:
        """Load plugin configurations from YAML file"""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                self.plugin_configs = config.get("plugins", {})
            self.logger.info(f"Loaded plugin config from {config_file}")
        except Exception as e:
            self.logger.error(f"Failed to load plugin config: {e}")
    
    def set_dashboard_context(self, context: Dict[str, Any]) -> None:
        """Set the dashboard context for plugins"""
        self.dashboard_context = context
    
    def discover_plugins(self, plugin_dir: Optional[str] = None) -> List[str]:
        """Discover available plugins"""
        if plugin_dir is None:
            plugin_dir = str(Path(__file__).parent)
        
        plugin_files = []
        plugin_path = Path(plugin_dir)
        
        if plugin_path.exists():
            for file in plugin_path.glob("*.py"):
                if file.name.startswith("_") or file.name == "base_plugin.py":
                    continue
                plugin_files.append(file.stem)
        
        self.logger.info(f"Discovered {len(plugin_files)} plugins: {plugin_files}")
        return plugin_files
    
    def load_plugin(self, plugin_name: str, plugin_dir: Optional[str] = None) -> bool:
        """Load a specific plugin"""
        try:
            if plugin_dir is None:
                plugin_dir = str(Path(__file__).parent)
            
            # Import the plugin module
            module_name = f"frontend.dashboard_plugins.{plugin_name}"
            spec = importlib.util.spec_from_file_location(
                module_name, 
                Path(plugin_dir) / f"{plugin_name}.py"
            )
            
            if spec is None or spec.loader is None:
                self.logger.error(f"Could not find plugin: {plugin_name}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes in the module
            plugin_classes = []
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BasePlugin) and 
                    obj != BasePlugin):
                    plugin_classes.append(obj)
            
            if not plugin_classes:
                self.logger.error(f"No plugin class found in {plugin_name}")
                return False
            
            # Use the first plugin class found
            PluginClass = plugin_classes[0]
            
            # Get plugin configuration
            plugin_config = self.plugin_configs.get(plugin_name, {})
            
            # Create plugin instance
            plugin = PluginClass(plugin_name, plugin_config)
            
            # Initialize plugin
            if plugin.initialize(self.dashboard_context):
                self.plugins[plugin_name] = plugin
                self.logger.info(f"Loaded plugin: {plugin_name}")
                return True
            else:
                self.logger.error(f"Failed to initialize plugin: {plugin_name}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to load plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self, plugin_dir: Optional[str] = None) -> int:
        """Load all discovered plugins"""
        plugin_names = self.discover_plugins(plugin_dir)
        loaded_count = 0
        
        for plugin_name in plugin_names:
            if self.load_plugin(plugin_name, plugin_dir):
                loaded_count += 1
        
        self.logger.info(f"Loaded {loaded_count}/{len(plugin_names)} plugins")
        return loaded_count
    
    def get_plugin(self, name: str) -> Optional[BasePlugin]:
        """Get a specific plugin"""
        return self.plugins.get(name)
    
    def get_enabled_plugins(self) -> List[BasePlugin]:
        """Get all enabled plugins sorted by order"""
        enabled = [p for p in self.plugins.values() if p.is_enabled()]
        return sorted(enabled, key=lambda p: p.order)
    
    def get_plugin_names(self) -> List[str]:
        """Get names of all loaded plugins"""
        return list(self.plugins.keys())
    
    def enable_plugin(self, name: str) -> bool:
        """Enable a plugin"""
        plugin = self.plugins.get(name)
        if plugin:
            plugin.enable()
            self.logger.info(f"Enabled plugin: {name}")
            return True
        return False
    
    def disable_plugin(self, name: str) -> bool:
        """Disable a plugin"""
        plugin = self.plugins.get(name)
        if plugin:
            plugin.disable()
            self.logger.info(f"Disabled plugin: {name}")
            return True
        return False
    
    def unload_plugin(self, name: str) -> bool:
        """Unload a plugin"""
        if name in self.plugins:
            plugin = self.plugins[name]
            plugin.cleanup()
            del self.plugins[name]
            self.logger.info(f"Unloaded plugin: {name}")
            return True
        return False
    
    def reload_plugin(self, name: str, plugin_dir: Optional[str] = None) -> bool:
        """Reload a plugin"""
        if name in self.plugins:
            self.unload_plugin(name)
        return self.load_plugin(name, plugin_dir)
    
    def get_plugin_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Get metadata for all plugins"""
        metadata = {}
        for name, plugin in self.plugins.items():
            metadata[name] = plugin.get_metadata()
            metadata[name]["enabled"] = plugin.is_enabled()
            metadata[name]["order"] = plugin.order
        return metadata
    
    def cleanup(self) -> None:
        """Cleanup all plugins"""
        for plugin in self.plugins.values():
            plugin.cleanup()
        self.plugins.clear()
        self.logger.info("Cleaned up all plugins")
