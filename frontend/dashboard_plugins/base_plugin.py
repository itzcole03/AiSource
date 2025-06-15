#!/usr/bin/env python3
"""
Base Plugin Class for Dashboard Plugins

Provides the abstract base class and utilities for creating dashboard plugins.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import streamlit as st

class BasePlugin(ABC):
    """Abstract base class for dashboard plugins"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"Plugin.{name}")
        self.enabled = self.config.get("enabled", True)
        self.order = self.config.get("order", 0)
        self.initialized = False
        self._data_cache = {}
        self._last_update = None
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata"""
        return {
            "name": self.name,
            "version": "1.0.0",
            "description": "Base plugin",
            "author": "Ultimate Copilot",
            "capabilities": []
        }
    
    @abstractmethod
    def initialize(self, dashboard_context: Any) -> bool:
        """Initialize the plugin with dashboard context"""
        pass
    
    @abstractmethod
    def render(self, container: Any) -> None:
        """Render the plugin UI in the given container"""
        pass
    
    @abstractmethod
    async def update_data(self) -> Dict[str, Any]:
        """Update plugin data"""
        pass
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
    
    def cache_data(self, key: str, data: Any) -> None:
        """Cache data for this plugin"""
        self._data_cache[key] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
    def get_cached_data(self, key: str, max_age_seconds: int = 300) -> Optional[Any]:
        """Get cached data if it's still fresh"""
        if key not in self._data_cache:
            return None
        
        cached = self._data_cache[key]
        age = (datetime.now() - cached["timestamp"]).total_seconds()
        
        if age <= max_age_seconds:
            return cached["data"]
        
        # Remove stale data
        del self._data_cache[key]
        return None
    
    def log_info(self, message: str) -> None:
        """Log info message"""
        self.logger.info(message)
    
    def log_warning(self, message: str) -> None:
        """Log warning message"""
        self.logger.warning(message)
    
    def log_error(self, message: str) -> None:
        """Log error message"""
        self.logger.error(message)
    
    def is_enabled(self) -> bool:
        """Check if plugin is enabled"""
        return self.enabled
    
    def enable(self) -> None:
        """Enable the plugin"""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the plugin"""
        self.enabled = False
    
    def cleanup(self) -> None:
        """Cleanup resources when plugin is destroyed"""
        self._data_cache.clear()

class StreamlitPlugin(BasePlugin):
    """Base class for Streamlit-based plugins"""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.dashboard_api = None
    
    def initialize(self, dashboard_context: Any) -> bool:
        """Initialize with dashboard context"""
        try:
            self.dashboard_api = dashboard_context.get("api_client")
            self.initialized = True
            self.log_info(f"Initialized plugin: {self.name}")
            return True
        except Exception as e:
            self.log_error(f"Failed to initialize plugin: {e}")
            return False
    
    def render_header(self, title: str, icon: str = "🔧") -> None:
        """Render standard plugin header"""
        st.markdown(f"### {icon} {title}")
    
    def render_status_indicator(self, status: str, message: str = "") -> None:
        """Render status indicator"""
        if status == "online":
            st.success(f"🟢 Online{' - ' + message if message else ''}")
        elif status == "offline":
            st.error(f"🔴 Offline{' - ' + message if message else ''}")
        elif status == "warning":
            st.warning(f"🟡 Warning{' - ' + message if message else ''}")
        else:
            st.info(f"ℹ️ {status}{' - ' + message if message else ''}")
    
    def render_metric_cards(self, metrics: List[Dict[str, Any]]) -> None:
        """Render metric cards"""
        cols = st.columns(len(metrics))
        for i, metric in enumerate(metrics):
            with cols[i]:
                st.metric(
                    label=metric.get("label", ""),
                    value=metric.get("value", ""),
                    delta=metric.get("delta"),
                    help=metric.get("help")
                )
    
    def render_data_table(self, data: List[Dict[str, Any]], title: str = "Data") -> None:
        """Render data as a table"""
        if data:
            st.markdown(f"**{title}**")
            st.dataframe(data, use_container_width=True)
        else:
            st.info(f"No {title.lower()} available")
    
    async def fetch_api_data(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Fetch data from the dashboard API"""
        if not self.dashboard_api:
            return None
        
        try:
            return await self.dashboard_api.get(endpoint)
        except Exception as e:
            self.log_error(f"Failed to fetch data from {endpoint}: {e}")
            return None
    
    async def send_api_command(self, endpoint: str, command: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send command to the dashboard API"""
        if not self.dashboard_api:
            return None
        
        try:
            return await self.dashboard_api.post(endpoint, command)
        except Exception as e:
            self.log_error(f"Failed to send command to {endpoint}: {e}")
            return None
