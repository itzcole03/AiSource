"""Enhanced System Manager - Elite Refactor

Handles full orchestration, async startup, and one-click swarm execution.
"""

import asyncio
import logging
import signal
import sys
import os
import json
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    yaml = None
    YAML_AVAILABLE = False

from core.enhanced_llm_manager import EnhancedLLMManager
from core.distributed_agent_manager import DistributedAgentManager
from core.advanced_memory_manager import AdvancedMemoryManager
from core.plugin_system import PluginManager
from core.agent_manager import EnhancedAgentManager
from integrations.editor_selection_manager import EditorSelectionManager
from utils.logger import setup_logger

class EnhancedSystemManager:
    def __init__(self, config_path="config/system_config.yaml", models_config_path="config/models_config.yaml", void_integration=True):
        self.config_path = config_path
        self.models_config_path = models_config_path
        self.void_integration = void_integration
        self.logger = setup_logger("EnhancedSystemManager")

        self.config = {}
        self.models_config = {}
        self.running = False
        self.startup_time = None
        self.performance_metrics = {
            "tasks_completed": 0,
            "model_switches": 0,
            "avg_response_time": 0.0,
            "success_rate": 1.0,
            "uptime": 0
        }

        self.llm_manager = None
        self.agent_manager = None
        self.memory_manager = None
        self.plugin_manager = None
        self.distributed_manager = None
        self.editor_manager = None

    async def initialize(self) -> None:
        self.logger.info("Initializing Ultimate Copilot System...")
        await self._load_configuration()
        await self._initialize_managers()
        self.logger.info("System initialized successfully.")

    async def _load_configuration(self) -> None:
        self.logger.info("Loading configuration files...")
        self.config = await self._load_yaml_or_json(self.config_path, default={})
        self.models_config = await self._load_yaml_or_json(self.models_config_path, default={})

    async def _load_yaml_or_json(self, path: str, default: Dict) -> Dict:
        if not Path(path).exists():
            self.logger.warning(f"{path} not found. Using default.")
            return default

        try:
            with open(path, "r", encoding='utf-8') as f:
                content = f.read()
                
            if not content.strip():
                self.logger.warning(f"{path} is empty. Using default.")
                return default
                
            try:
                if YAML_AVAILABLE and yaml and path.endswith(".yaml"):
                    return yaml.safe_load(content) or default
                elif content.strip().startswith("{"):
                    return json.loads(content)
                else:
                    return self._parse_simple_yaml(content)
            except Exception as e:
                if YAML_AVAILABLE and yaml and hasattr(yaml, 'YAMLError') and isinstance(e, yaml.YAMLError):
                    self.logger.error(f"YAML parsing error in {path}: {e}")
                elif isinstance(e, json.JSONDecodeError):
                    self.logger.error(f"JSON parsing error in {path}: {e}")
                else:
                    self.logger.error(f"Config parsing error in {path}: {e}")
                return default
        except Exception as e:
            self.logger.error(f"Failed to load config from {path}: {e}")
            return default

    async def _initialize_managers(self) -> None:
        self.logger.info("Initializing core managers...")

        self.llm_manager = EnhancedLLMManager(self.models_config)
        self.agent_manager = EnhancedAgentManager(self.config)
        self.memory_manager = AdvancedMemoryManager()
        self.plugin_manager = PluginManager()
        self.distributed_manager = DistributedAgentManager(self.config)
        self.editor_manager = EditorSelectionManager(self.config, self.void_integration)

        await self.llm_manager.initialize()
        await self.agent_manager.initialize()
        await self.memory_manager.initialize()
        await self.plugin_manager.initialize()
        await self.distributed_manager.initialize()
        await self.editor_manager.initialize()

    async def start(self) -> None:
        self.running = True
        self.logger.info("Ultimate Copilot is now running.")
        self.logger.info("System is ready! Press Ctrl+C to stop.")
        
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received shutdown signal...")
            self.running = False

    async def shutdown(self) -> None:
        self.logger.info("Shutting down system...")
        self.running = False
        
        # Gracefully shutdown all managers with error handling
        managers = [
            (self.agent_manager, "Agent Manager"),
            (self.llm_manager, "LLM Manager"),
            (self.memory_manager, "Memory Manager"),
            (self.plugin_manager, "Plugin Manager"),
            (self.distributed_manager, "Distributed Manager"),
            (self.editor_manager, "Editor Manager")
        ]
        
        for manager, name in managers:
            if manager and hasattr(manager, 'shutdown'):
                try:
                    await manager.shutdown()
                    self.logger.info(f"[OK] {name} shutdown complete")
                except Exception as e:
                    self.logger.error(f"[ERROR] {name} shutdown failed: {e}")
            elif manager:
                self.logger.warning(f"[WARNING] {name} has no shutdown method")

    async def one_click_run(self, user_prompt: Optional[str] = None) -> None:
        await self.initialize()
        self.logger.info("One-click mode activated.")
        
        try:
            if user_prompt and self.agent_manager and hasattr(self.agent_manager, 'dispatch_prompt'):
                await self.agent_manager.dispatch_prompt(user_prompt)
            elif self.agent_manager and hasattr(self.agent_manager, 'auto_execute_workspace_plan'):
                await self.agent_manager.auto_execute_workspace_plan()
            else:
                self.logger.warning("[WARNING] Agent manager not available or missing required methods")
        except Exception as e:
            self.logger.error(f"[ERROR] One-click execution failed: {e}")
        finally:
            await self.shutdown()

    def _parse_simple_yaml(self, raw: str) -> Dict[str, Any]:
        """Parse simple YAML-like format as fallback"""
        result = {}
        try:
            lines = raw.strip().splitlines()
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Try to parse value as appropriate type
                    if value.lower() in ('true', 'false'):
                        result[key] = value.lower() == 'true'
                    elif value.isdigit():
                        result[key] = int(value)
                    elif value.replace('.', '', 1).isdigit():
                        result[key] = float(value)
                    else:
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        result[key] = value
        except Exception as e:
            self.logger.error(f"Simple YAML parsing failed: {e}")
        
        return result
