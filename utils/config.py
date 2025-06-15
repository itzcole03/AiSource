"""
Configuration utilities for the Ultimate Copilot system
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any

def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file with environment variable substitution"""
    
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Substitute environment variables
    config = substitute_env_vars(config)
    
    return config

def substitute_env_vars(obj: Any) -> Any:
    """Recursively substitute environment variables in configuration"""
    
    if isinstance(obj, dict):
        return {key: substitute_env_vars(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [substitute_env_vars(item) for item in obj]
    elif isinstance(obj, str):
        # Handle ${VAR_NAME} and ${VAR_NAME:-default} patterns
        if obj.startswith('${') and obj.endswith('}'):
            var_expr = obj[2:-1]  # Remove ${ and }
            
            if ':-' in var_expr:
                var_name, default_value = var_expr.split(':-', 1)
                return os.getenv(var_name, default_value)
            else:
                return os.getenv(var_expr, obj)
        return obj
    else:
        return obj

def get_env_var(var_name: str, default: str = None, required: bool = False) -> str:
    """Get environment variable with optional default and required check"""
    
    value = os.getenv(var_name, default)
    
    if required and not value:
        raise ValueError(f"Required environment variable {var_name} is not set")
    
    return value

def validate_config(config: Dict[str, Any]) -> bool:
    """Validate configuration structure and required fields"""
    
    required_sections = ['system', 'llm_providers', 'agents', 'memory', 'tasks', 'logging']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Required configuration section '{section}' is missing")
    
    # Validate LLM providers
    if not config['llm_providers']:
        raise ValueError("At least one LLM provider must be configured")
    
    # Validate agents
    if not config['agents']:
        raise ValueError("At least one agent must be configured")
    
    return True

def create_default_config() -> Dict[str, Any]:
    """Create a default configuration"""
    
    return {
        'system': {
            'name': 'Ultimate Copilot Swarm',
            'version': '2.0.0',
            'debug': True,
            'auto_start': True
        },
        'llm_providers': {
            'huggingface': {
                'api_key': '${HUGGINGFACE_API_KEY}',
                'base_url': 'https://api-inference.huggingface.co/models',
                'models': ['microsoft/DialoGPT-medium']
            },
            'ollama': {
                'base_url': '${OLLAMA_BASE_URL:-http://localhost:11434}',
                'models': ['llama3', 'codellama']
            }
        },
        'agents': {
            'orchestrator': {
                'model': 'huggingface/microsoft/DialoGPT-medium',
                'role': 'Task Orchestration',
                'capabilities': ['coordination', 'planning', 'management']
            }
        },
        'memory': {
            'provider': 'json',
            'file': 'memory/memory.json'
        },
        'tasks': {
            'auto_load': True,
            'max_concurrent': 3,
            'retry_attempts': 2,
            'timeout': 300
        },
        'logging': {
            'level': 'INFO',
            'format': '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s',
            'file': 'logs/system.log'
        }
    }