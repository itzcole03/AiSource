#!/usr/bin/env python3
"""
System Monitor Plugin

Provides system status and health monitoring for the Ultimate Copilot Dashboard.
"""

import asyncio
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, List
import psutil

from .base_plugin import StreamlitPlugin

class SystemMonitorPlugin(StreamlitPlugin):
    """System monitoring and health plugin"""
    
    def __init__(self, name: str = "system_monitor", config: Dict[str, Any] = None):
        super().__init__(name, config)
        self.metrics_history = []
        self.max_history = 100
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata"""
        return {
            "name": "System Monitor",
            "version": "2.0.0",
            "description": "System status and health monitoring",
            "author": "Ultimate Copilot",
            "capabilities": [
                "system_status",
                "performance_metrics", 
                "resource_monitoring",
                "health_checks"
            ]
        }
    
    async def update_data(self) -> Dict[str, Any]:
        """Update system monitoring data"""
        try:
            # Get system status from API
            system_status = await self.fetch_api_data("/system/status")
            performance_metrics = await self.fetch_api_data("/system/metrics")
            
            # Store in cache
            if system_status:
                self.cache_data("system_status", system_status)
            if performance_metrics:
                self.cache_data("performance_metrics", performance_metrics)
                
                # Add to history for charts
                self.add_to_history(performance_metrics)
            
            return {
                "system_status": system_status,
                "performance_metrics": performance_metrics,
                "history": self.metrics_history
            }
            
        except Exception as e:
            self.log_error(f"Failed to update system data: {e}")
            return {"error": str(e)}
    
    def render(self, container) -> None:
        """Render system monitoring UI"""
        with container:
            self.render_header("System Overview", "🖥️")
            
            # Get cached data
            system_status = self.get_cached_data("system_status", 30)
            performance_metrics = self.get_cached_data("performance_metrics", 30)
            
            if not system_status:
                st.error("Unable to fetch system status")
                return
            
            # System status
            self.render_system_status(system_status)
            
            # Performance metrics
            if performance_metrics:
                self.render_performance_metrics(performance_metrics)
            
            # Resource monitoring
            self.render_resource_monitoring(system_status)
            
            # System controls
            self.render_system_controls()
    
    def render_system_status(self, status: Dict[str, Any]) -> None:
        """Render system status section"""
        st.subheader("System Status")
        
        # Status indicator
        system_status = status.get("status", "unknown")
        if system_status == "running":
            self.render_status_indicator("online", "System is running normally")
        elif system_status == "error":
            self.render_status_indicator("offline", "System has errors")
        else:
            self.render_status_indicator("warning", f"Status: {system_status}")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Uptime", status.get("uptime", "Unknown"))
        
        with col2:
            active_connections = status.get("active_connections", 0)
            st.metric("Active Connections", active_connections)
        
        with col3:
            components = status.get("components", {})
            active_components = sum(1 for v in components.values() if v)
            total_components = len(components)
            st.metric("Components", f"{active_components}/{total_components}")
        
        with col4:
            timestamp = status.get("timestamp", "")
            if timestamp:
                last_update = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_diff = datetime.now() - last_update.replace(tzinfo=None)
                st.metric("Last Update", f"{int(time_diff.total_seconds())}s ago")
    
    def render_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """Render performance metrics section"""
        st.subheader("Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            requests_total = metrics.get("requests_total", 0)
            st.metric("Total Requests", requests_total)
        
        with col2:
            rpm = metrics.get("requests_per_minute", 0)
            st.metric("Requests/Min", rpm)
        
        with col3:
            avg_response = metrics.get("average_response_time", 0)
            st.metric("Avg Response", f"{avg_response:.2f}s")
        
        with col4:
            error_rate = metrics.get("error_rate", 0)
            st.metric("Error Rate", f"{error_rate:.1f}%")
        
        # Performance charts
        if self.metrics_history:
            self.render_performance_charts()
    
    def render_resource_monitoring(self, status: Dict[str, Any]) -> None:
        """Render resource monitoring section"""
        st.subheader("Resource Usage")
        
        system_info = status.get("system", {})
        vram_info = status.get("vram", {})
        
        # System resources
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**System Resources**")
            
            # CPU usage
            cpu_percent = system_info.get("cpu_percent", 0)
            st.metric("CPU Usage", f"{cpu_percent:.1f}%")
            
            # Memory usage
            memory = system_info.get("memory", {})
            if memory:
                memory_percent = memory.get("percent", 0)
                memory_used = memory.get("used", 0) / (1024**3)  # GB
                memory_total = memory.get("total", 0) / (1024**3)  # GB
                st.metric("Memory Usage", f"{memory_percent:.1f}%", 
                         f"{memory_used:.1f}/{memory_total:.1f} GB")
            
            # Disk usage
            disk = system_info.get("disk", {})
            if disk:
                disk_percent = disk.get("percent", 0)
                disk_free = disk.get("free", 0) / (1024**3)  # GB
                st.metric("Disk Usage", f"{disk_percent:.1f}%", 
                         f"{disk_free:.1f} GB free")
        
        with col2:
            st.markdown("**VRAM Usage**")
            
            if vram_info:
                current_vram = vram_info.get("current_usage", 0)
                total_vram = vram_info.get("total_capacity", 0)
                
                if total_vram > 0:
                    vram_percent = (current_vram / total_vram) * 100
                    st.metric("VRAM Usage", f"{vram_percent:.1f}%",
                             f"{current_vram:.1f}/{total_vram:.1f} GB")
                
                # VRAM breakdown by model
                models = vram_info.get("models", {})
                if models:
                    st.markdown("**By Model:**")
                    for model, usage in models.items():
                        st.text(f"{model}: {usage:.1f} GB")
            else:
                st.info("VRAM information not available")
    
    def render_system_controls(self) -> None:
        """Render system control buttons"""
        st.subheader("System Controls")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Refresh Data", use_container_width=True):
                # Clear cache to force refresh
                self._data_cache.clear()
                st.rerun()
        
        with col2:
            if st.button("⚙️ Reload Config", use_container_width=True):
                result = asyncio.run(self.send_api_command("/system/control", {
                    "action": "reload_config"
                }))
                if result and result.get("status") == "success":
                    st.success("Configuration reloaded")
                else:
                    st.error("Failed to reload configuration")
        
        with col3:
            if st.button("🔄 Restart System", use_container_width=True):
                if st.session_state.get("confirm_restart"):
                    result = asyncio.run(self.send_api_command("/system/control", {
                        "action": "restart"
                    }))
                    if result and result.get("status") == "success":
                        st.success("System restart initiated")
                    else:
                        st.error("Failed to restart system")
                    st.session_state.confirm_restart = False
                else:
                    st.session_state.confirm_restart = True
                    st.warning("Click again to confirm restart")
        
        with col4:
            if st.button("🛑 Shutdown", use_container_width=True):
                if st.session_state.get("confirm_shutdown"):
                    result = asyncio.run(self.send_api_command("/system/control", {
                        "action": "shutdown"
                    }))
                    if result and result.get("status") == "success":
                        st.success("System shutdown initiated")
                    else:
                        st.error("Failed to shutdown system")
                    st.session_state.confirm_shutdown = False
                else:
                    st.session_state.confirm_shutdown = True
                    st.error("Click again to confirm shutdown")
    
    def render_performance_charts(self) -> None:
        """Render performance charts"""
        if len(self.metrics_history) < 2:
            return
        
        st.subheader("Performance Trends")
        
        # Create DataFrame from history
        df = pd.DataFrame(self.metrics_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Response time chart
            if 'average_response_time' in df.columns:
                fig = px.line(df, x='timestamp', y='average_response_time', 
                             title='Average Response Time')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Requests per minute chart
            if 'requests_per_minute' in df.columns:
                fig = px.line(df, x='timestamp', y='requests_per_minute',
                             title='Requests per Minute')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
    
    def add_to_history(self, metrics: Dict[str, Any]) -> None:
        """Add metrics to history for charts"""
        metrics_with_time = metrics.copy()
        metrics_with_time['timestamp'] = datetime.now().isoformat()
        
        self.metrics_history.append(metrics_with_time)
        
        # Keep only recent history
        if len(self.metrics_history) > self.max_history:
            self.metrics_history = self.metrics_history[-self.max_history:]
