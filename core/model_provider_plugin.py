"""
Model Provider Plugin System

This module implements a plugin system for custom model providers, allowing users
to extend the Ultimate Copilot System with their own model providers.
"""

import os
import sys
import json
import platform
import importlib.util
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable, Type
from pathlib import Path

logger = logging.getLogger(__name__)

class ModelProviderPlugin:
    """Base class for model provider plugins"""
    
    def __init__(self, plugin_id: str, config: Dict[str, Any]):
        self.plugin_id = plugin_id
        self.config = config
        self.name = "Base Model Provider Plugin"
        self.description = "Base class for model provider plugins"
        self.version = "1.0.0"
        self.models = []
        self.initialized = False
        self.platform_compatible = False
        self.supported_platforms = []
        self.active_model = None
        self.exclusive_instance = False
        self.endpoint = None
    
    async def initialize(self) -> bool:
        """Initialize the model provider plugin"""
        # Check platform compatibility
        current_platform = self._get_current_platform()
        if self.supported_platforms and current_platform not in self.supported_platforms:
            logger.warning(f"Plugin {self.plugin_id} is not compatible with {current_platform}")
            return False
            
        self.platform_compatible = True
        self.initialized = True
        return True
    
    def _get_current_platform(self) -> str:
        """Get the current platform"""
        system = platform.system().lower()
        if system == "darwin":
            return "macos"
        return system
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models from this provider"""
        return self.models
    
    async def is_available(self) -> bool:
        """Check if the model provider is available"""
        return self.initialized and self.platform_compatible
    
    async def generate_text(self, model_id: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using the specified model"""
        raise NotImplementedError("Subclasses must implement generate_text")
    
    async def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        for model in self.models:
            if model["id"] == model_id:
                return model
        return None
    
    async def load_model(self, model_id: str) -> bool:
        """Load a specific model (for providers that can only run one model at a time)"""
        if not self.exclusive_instance:
            # Provider can run multiple models simultaneously
            return True
            
        if self.active_model == model_id:
            # Model is already loaded
            return True
            
        # Unload current model if any
        if self.active_model:
            await self.unload_model(self.active_model)
            
        # Load the requested model
        logger.info(f"Loading model {model_id} for provider {self.plugin_id}")
        self.active_model = model_id
        return True
    
    async def unload_model(self, model_id: str) -> bool:
        """Unload a specific model"""
        if not self.exclusive_instance:
            # Provider can run multiple models simultaneously
            return True
            
        if self.active_model != model_id:
            # Model is not loaded
            return True
            
        logger.info(f"Unloading model {model_id} for provider {self.plugin_id}")
        self.active_model = None
        return True
    
    async def get_resource_requirements(self, model_id: str) -> Dict[str, str]:
        """Get resource requirements for a specific model"""
        model_info = await self.get_model_info(model_id)
        if model_info and "resource_requirements" in model_info:
            return model_info["resource_requirements"]
        return {"ram": "unknown", "vram": "unknown"}
    
    async def shutdown(self) -> None:
        """Shutdown the model provider plugin"""
        if self.active_model:
            await self.unload_model(self.active_model)
        self.initialized = False


class ModelProviderPluginManager:
    """Manager for model provider plugins"""
    
    def __init__(self, plugins_dir: str = "plugins/model_providers"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, ModelProviderPlugin] = {}
        self.plugin_classes: Dict[str, Type[ModelProviderPlugin]] = {}
        self.model_load_lock = asyncio.Lock()
        self.exclusive_providers = set()
        self.resource_manager = ResourceManager()
    
    async def initialize(self) -> None:
        """Initialize the plugin manager and discover plugins"""
        logger.info(f"Initializing Model Provider Plugin Manager from {self.plugins_dir}")
        
        # Create plugins directory if it doesn't exist
        os.makedirs(self.plugins_dir, exist_ok=True)
        
        # Initialize resource manager
        await self.resource_manager.initialize()
        
        # Discover plugins
        await self.discover_plugins()
    
    async def discover_plugins(self) -> None:
        """Discover available model provider plugins"""
        if not self.plugins_dir.exists():
            logger.warning(f"Plugins directory {self.plugins_dir} does not exist")
            return
        
        for plugin_dir in self.plugins_dir.iterdir():
            if not plugin_dir.is_dir():
                continue
            
            manifest_path = plugin_dir / "manifest.json"
            if not manifest_path.exists():
                logger.warning(f"No manifest.json found in {plugin_dir}")
                continue
            
            try:
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                
                if manifest.get("type") != "model_provider":
                    logger.debug(f"Skipping non-model provider plugin: {plugin_dir}")
                    continue
                
                plugin_id = manifest.get("id")
                if not plugin_id:
                    logger.warning(f"Plugin in {plugin_dir} has no ID in manifest")
                    continue
                
                # Check platform compatibility
                supported_platforms = manifest.get("platform", [])
                current_platform = self._get_current_platform()
                if supported_platforms and current_platform not in supported_platforms:
                    logger.info(f"Plugin {plugin_id} is not compatible with {current_platform}, skipping")
                    continue
                
                main_module = manifest.get("main", "provider.py")
                main_class = manifest.get("class", "ModelProvider")
                
                # Load the plugin module
                plugin_module_path = plugin_dir / main_module
                if not plugin_module_path.exists():
                    logger.warning(f"Plugin module {plugin_module_path} not found")
                    continue
                
                # Import the plugin module
                spec = importlib.util.spec_from_file_location(
                    f"model_provider_plugin_{plugin_id}", 
                    plugin_module_path
                )
                if not spec or not spec.loader:
                    logger.warning(f"Failed to load plugin spec: {plugin_id}")
                    continue
                    
                plugin_module = importlib.util.module_from_spec(spec)
                sys.modules[spec.name] = plugin_module
                spec.loader.exec_module(plugin_module)
                
                # Get the plugin class
                if not hasattr(plugin_module, main_class):
                    logger.warning(f"Plugin class {main_class} not found in {plugin_module_path}")
                    continue
                
                plugin_class = getattr(plugin_module, main_class)
                self.plugin_classes[plugin_id] = plugin_class
                
                # Track exclusive instance providers
                if manifest.get("exclusive_instance", False):
                    self.exclusive_providers.add(plugin_id)
                
                logger.info(f"Discovered model provider plugin: {plugin_id}")
                
            except Exception as e:
                logger.error(f"Error loading plugin from {plugin_dir}: {e}")
    
    def _get_current_platform(self) -> str:
        """Get the current platform"""
        system = platform.system().lower()
        if system == "darwin":
            return "macos"
        return system
    
    async def load_plugin(self, plugin_id: str, config: Dict[str, Any]) -> Optional[ModelProviderPlugin]:
        """Load and initialize a specific plugin"""
        if plugin_id not in self.plugin_classes:
            logger.warning(f"Plugin {plugin_id} not found")
            return None
        
        try:
            plugin_class = self.plugin_classes[plugin_id]
            plugin = plugin_class(plugin_id, config)
            
            # Set exclusive instance flag
            if plugin_id in self.exclusive_providers:
                plugin.exclusive_instance = True
            
            # Set supported platforms from manifest
            manifest_path = self.plugins_dir / plugin_id / "manifest.json"
            if manifest_path.exists():
                with open(manifest_path, "r") as f:
                    manifest = json.load(f)
                    plugin.supported_platforms = manifest.get("platform", [])
                    plugin.endpoint = config.get("base_url") or manifest.get("endpoint")
            
            # Initialize the plugin
            success = await plugin.initialize()
            if not success:
                logger.warning(f"Failed to initialize plugin {plugin_id}")
                return None
            
            self.plugins[plugin_id] = plugin
            logger.info(f"Loaded model provider plugin: {plugin_id}")
            
            return plugin
            
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_id}: {e}")
            return None
    
    async def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin"""
        if plugin_id not in self.plugins:
            logger.warning(f"Plugin {plugin_id} not loaded")
            return False
        
        try:
            plugin = self.plugins[plugin_id]
            await plugin.shutdown()
            del self.plugins[plugin_id]
            logger.info(f"Unloaded plugin {plugin_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_id}: {e}")
            return False
    
    async def get_available_plugins(self) -> List[Dict[str, Any]]:
        """Get list of available plugins"""
        return [
            {
                "id": plugin_id,
                "name": plugin.name,
                "description": plugin.description,
                "version": plugin.version,
                "initialized": plugin.initialized
            }
            for plugin_id, plugin in self.plugins.items()
        ]
    
    async def get_available_models(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all available models from all plugins"""
        models = {}
        
        for plugin_id, plugin in self.plugins.items():
            if await plugin.is_available():
                try:
                    plugin_models = await plugin.get_available_models()
                    models[plugin_id] = plugin_models
                except Exception as e:
                    logger.error(f"Error getting models from plugin {plugin_id}: {e}")
        
        return models
    
    async def generate_text(self, plugin_id: str, model_id: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using a specific plugin and model"""
        if plugin_id not in self.plugins:
            raise ValueError(f"Plugin {plugin_id} not found")
        
        plugin = self.plugins[plugin_id]
        if not await plugin.is_available():
            raise ValueError(f"Plugin {plugin_id} is not available")
        
        # Handle exclusive instance providers
        if plugin.exclusive_instance:
            async with self.model_load_lock:
                # Check if we need to load the model
                if plugin.active_model != model_id:
                    # Get resource requirements
                    requirements = await plugin.get_resource_requirements(model_id)
                    
                    # Check if we have enough resources
                    if not await self.resource_manager.check_resources(requirements):
                        raise ValueError(f"Not enough resources to load model {model_id}")
                    
                    # Load the model
                    success = await plugin.load_model(model_id)
                    if not success:
                        raise ValueError(f"Failed to load model {model_id}")
        
        return await plugin.generate_text(model_id, prompt, **kwargs)
    
    async def load_model(self, plugin_id: str, model_id: str) -> bool:
        """Explicitly load a model for a provider that supports model switching"""
        if plugin_id not in self.plugins:
            logger.warning(f"Plugin {plugin_id} not found")
            return False
        
        plugin = self.plugins[plugin_id]
        if not plugin.exclusive_instance:
            # Provider doesn't need explicit model loading
            return True
        
        async with self.model_load_lock:
            # Get resource requirements
            requirements = await plugin.get_resource_requirements(model_id)
            
            # Check if we have enough resources
            if not await self.resource_manager.check_resources(requirements):
                logger.warning(f"Not enough resources to load model {model_id}")
                return False
            
            # Load the model
            return await plugin.load_model(model_id)
    
    async def shutdown(self) -> None:
        """Shutdown all plugins"""
        for plugin_id, plugin in list(self.plugins.items()):
            try:
                await plugin.shutdown()
                logger.info(f"Shut down plugin {plugin_id}")
            except Exception as e:
                logger.error(f"Error shutting down plugin {plugin_id}: {e}")
        
        self.plugins.clear()
        
        # Shutdown resource manager
        await self.resource_manager.shutdown()


class ResourceManager:
    """Manager for system resources"""
    
    def __init__(self):
        self.available_ram = "0GB"
        self.available_vram = "0GB"
        self.allocated_ram = "0GB"
        self.allocated_vram = "0GB"
    
    async def initialize(self) -> None:
        """Initialize the resource manager"""
        # Detect available system resources
        try:
            import psutil
            from gputil import GPUtil
            
            # Get RAM
            ram = psutil.virtual_memory().total
            self.available_ram = f"{ram // (1024**3)}GB"
            
            # Get VRAM if available
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    vram = sum(gpu.memoryTotal for gpu in gpus)
                    self.available_vram = f"{vram // 1024}GB"
            except:
                self.available_vram = "0GB"
                
        except ImportError:
            logger.warning("psutil or GPUtil not available, using default resource values")
            self.available_ram = "16GB"  # Default assumption
            self.available_vram = "0GB"
            
        logger.info(f"System resources: RAM={self.available_ram}, VRAM={self.available_vram}")
    
    async def check_resources(self, requirements: Dict[str, str]) -> bool:
        """Check if there are enough resources for the given requirements"""
        required_ram = self._parse_gb(requirements.get("ram", "0GB"))
        required_vram = self._parse_gb(requirements.get("vram", "0GB"))
        
        available_ram = self._parse_gb(self.available_ram)
        available_vram = self._parse_gb(self.available_vram)
        
        # Check if we have enough resources
        if required_ram > available_ram:
            logger.warning(f"Not enough RAM: required={required_ram}GB, available={available_ram}GB")
            return False
            
        if required_vram > 0 and required_vram > available_vram:
            logger.warning(f"Not enough VRAM: required={required_vram}GB, available={available_vram}GB")
            return False
            
        return True
    
    def _parse_gb(self, size_str: str) -> float:
        """Parse a size string like '4GB' to a float value in GB"""
        try:
            if size_str.lower().endswith("gb"):
                return float(size_str[:-2])
            elif size_str.lower().endswith("mb"):
                return float(size_str[:-2]) / 1024
            elif size_str.lower().endswith("kb"):
                return float(size_str[:-2]) / (1024 * 1024)
            else:
                return float(size_str)
        except (ValueError, AttributeError):
            return 0.0
    
    async def shutdown(self) -> None:
        """Shutdown the resource manager"""
        pass
