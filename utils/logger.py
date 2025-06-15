"""
Logging utilities for the Ultimate Copilot system
"""

import logging
import os
from datetime import datetime
from pathlib import Path

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """Setup a logger with file and console handlers"""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    file_formatter = logging.Formatter(
        '[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s'
    )
    console_formatter = logging.Formatter(
        '[%(levelname)s] %(name)s: %(message)s'
    )
    
    # File handler
    log_file = log_dir / "system.log"
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def setup_agent_logger(agent_id: str) -> logging.Logger:
    """Setup a logger specifically for an agent"""
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger = logging.getLogger(f"Agent.{agent_id}")
    logger.setLevel(logging.INFO)
    
    if logger.handlers:
        return logger
    
    # Agent-specific log file
    log_file = log_dir / f"agent_{agent_id}.log"
    
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] %(message)s'
    )
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    return logger