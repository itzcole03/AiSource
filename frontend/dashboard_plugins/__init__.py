"""
Dashboard Plugins Package

Plugin system for the Ultimate Copilot Dashboard.
"""

__version__ = "2.0.0"
__all__ = ["BasePlugin", "PluginManager"]

from .base_plugin import BasePlugin
from .plugin_manager import PluginManager
