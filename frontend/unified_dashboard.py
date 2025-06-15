#!/usr/bin/env python3
"""
Unified Dashboard for Ultimate Copilot System

A comprehensive, modern dashboard that consolidates all features from various
dashboard implementations into a single, powerful interface.
"""

import asyncio
import logging
import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

# Configure Streamlit page
st.set_page_config(
    page_title="Ultimate Copilot System - Unified Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1f4e79, #2d5aa0);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    text-align: center;
}
.status-card {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
}
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 8px;
    text-align: center;
    margin: 0.5rem;
}
.error-text {
    color: #dc3545;
    font-weight: bold;
}
.success-text {
    color: #28a745;
    font-weight: bold;
}
.warning-text {
    color: #ffc107;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

class APIClient:
    """Simple API client for backend communication"""
    
    def __init__(self, base_url: Optional[str] = None):
        if base_url is None:
            # Try to get from environment variable or use default
            import os
            base_url = os.environ.get('DASHBOARD_BACKEND_URL', "http://127.0.0.1:8001")
        self.base_url = base_url
        self.timeout = 5
    
    async def get(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Make GET request to API"""
        try:
            response = requests.get(f"{self.base_url}{endpoint}", timeout=self.timeout)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    async def post(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make POST request to API"""
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}", 
                json=data, 
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

class UnifiedDashboard:
    """Main unified dashboard class"""
    
    def __init__(self):
        self.api_client = APIClient()
        self.plugins = {}
        self.dashboard_context = {"api_client": self.api_client}
        
        # Initialize session state
        if "backend_available" not in st.session_state:
            st.session_state.backend_available = False
        if "last_check" not in st.session_state:
            st.session_state.last_check = None
        if "current_tab" not in st.session_state:
            st.session_state.current_tab = "System Overview"
    
    async def check_backend_health(self) -> bool:
        """Check if backend API is available"""
        try:
            result = await self.api_client.get("/")
            return result is not None and "error" not in result
        except:
            return False
    
    def load_plugins(self):
        """Load dashboard plugins"""
        try:
            from frontend.dashboard_plugins.plugin_manager import PluginManager
            from frontend.dashboard_plugins.system_monitor import SystemMonitorPlugin
            from frontend.dashboard_plugins.model_manager import ModelManagerPlugin
            
            # Create plugin instances
            self.plugins = {
                "system_monitor": SystemMonitorPlugin(),
                "model_manager": ModelManagerPlugin()
            }
            
            # Initialize plugins
            for plugin in self.plugins.values():
                plugin.initialize(self.dashboard_context)
                
        except Exception as e:
            st.error(f"Failed to load plugins: {e}")
    
    def render_header(self):
        """Render dashboard header"""
        st.markdown("""
        <div class="main-header">
            <h1>🚀 Ultimate Copilot System</h1>
            <p>Unified Dashboard - Real-time Monitoring & Control</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_connection_status(self):
        """Render backend connection status"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            if st.session_state.backend_available:
                st.success("🟢 Backend Connected")
            else:
                st.error("🔴 Backend Disconnected")
        
        with col2:
            if st.button("🔄 Check Connection"):
                backend_status = asyncio.run(self.check_backend_health())
                st.session_state.backend_available = backend_status
                st.session_state.last_check = datetime.now()
                st.rerun()
        
        with col3:
            if st.session_state.last_check:
                time_diff = datetime.now() - st.session_state.last_check
                st.caption(f"Last check: {int(time_diff.total_seconds())}s ago")
    
    def render_sidebar(self):
        """Render dashboard sidebar"""
        with st.sidebar:
            st.header("🎛️ Dashboard Control")
            
            # Connection status
            self.render_connection_status()
            
            st.divider()
            
            # Quick actions
            st.subheader("Quick Actions")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Refresh All", use_container_width=True):
                    # Clear all caches and refresh
                    if hasattr(st, 'cache_data'):
                        st.cache_data.clear()
                    st.rerun()
            
            with col2:
                auto_refresh = st.checkbox("Auto Refresh", value=False)
                if auto_refresh:
                    # Auto-refresh every 30 seconds
                    st.rerun()
            
            st.divider()
            
            # System info
            st.subheader("System Info")
            st.info("Dashboard Version: 2.0.0")
            st.info(f"Python: {sys.version.split()[0]}")
            st.info(f"Streamlit: {st.__version__}")
            
            # Backend status
            if st.session_state.backend_available:
                backend_info = asyncio.run(self.api_client.get("/"))
                if backend_info and "error" not in backend_info:
                    st.success("Backend: Online")
                else:
                    st.warning("Backend: Limited")
            else:
                st.error("Backend: Offline")
    
    def render_system_overview_tab(self):
        """Render system overview tab"""
        if not st.session_state.backend_available:
            st.warning("⚠️ Backend not available. Please start the dashboard backend server.")
            st.markdown("""
            To start the backend server, run:
            ```bash
            python frontend/dashboard_backend.py
            ```
            """)
            return
        
        # Use system monitor plugin if available
        if "system_monitor" in self.plugins:
            plugin = self.plugins["system_monitor"]
            asyncio.run(plugin.update_data())
            plugin.render(st.container())
        else:
            st.error("System monitor plugin not available")
    
    def render_model_management_tab(self):
        """Render model management tab"""
        if not st.session_state.backend_available:
            st.warning("⚠️ Backend not available. Model management requires backend connection.")
            return
        
        # Use model manager plugin if available
        if "model_manager" in self.plugins:
            plugin = self.plugins["model_manager"]
            asyncio.run(plugin.update_data())
            plugin.render(st.container())
        else:
            st.error("Model manager plugin not available")
    
    def render_agent_management_tab(self):
        """Render agent management tab"""
        st.header("🤖 Agent Management")
        
        if not st.session_state.backend_available:
            st.warning("⚠️ Backend not available. Agent management requires backend connection.")
            return
        
        # Get agent status
        agent_status = asyncio.run(self.api_client.get("/agents/status"))
        
        if agent_status and "error" not in agent_status:
            # Agent overview
            st.subheader("Agent Overview")
            
            agents = agent_status.get("agents", [])
            if agents:
                # Display agents in a table
                import pandas as pd
                df = pd.DataFrame(agents)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No agents currently active")
            
            # Agent controls
            st.subheader("Agent Controls")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Create Agent**")
                agent_type = st.selectbox("Agent Type", ["coding", "research", "general"])
                if st.button("Create Agent", use_container_width=True):
                    st.info(f"Creating {agent_type} agent...")
            
            with col2:
                st.markdown("**Stop Agent**")
                agent_id = st.text_input("Agent ID")
                if st.button("Stop Agent", use_container_width=True):
                    if agent_id:
                        st.warning(f"Stopping agent {agent_id}")
            
            with col3:
                st.markdown("**Refresh Status**")
                st.write("")  # Spacing
                if st.button("Refresh Agents", use_container_width=True):
                    st.rerun()
        else:
            st.error("Failed to get agent status")
    
    def render_logs_tab(self):
        """Render logs and diagnostics tab"""
        st.header("📋 Logs & Diagnostics")
        
        if not st.session_state.backend_available:
            st.warning("⚠️ Backend not available. Logs require backend connection.")
            return
        
        # Get system logs
        logs_data = asyncio.run(self.api_client.get("/logs"))
        
        if logs_data and "error" not in logs_data:
            logs = logs_data.get("logs", [])
            
            if logs:
                st.subheader("Recent System Logs")
                
                # Log level filter
                log_levels = ["ALL", "ERROR", "WARNING", "INFO", "DEBUG"]
                selected_level = st.selectbox("Filter by Level", log_levels)
                
                # Display logs
                with st.container():
                    for log_line in logs[-50:]:  # Show last 50 lines
                        if selected_level == "ALL" or selected_level.lower() in log_line.lower():
                            if "error" in log_line.lower():
                                st.markdown(f'<span class="error-text">{log_line}</span>', 
                                          unsafe_allow_html=True)
                            elif "warning" in log_line.lower():
                                st.markdown(f'<span class="warning-text">{log_line}</span>', 
                                          unsafe_allow_html=True)
                            else:
                                st.text(log_line)
            else:
                st.info("No logs available")
        else:
            st.error("Failed to retrieve logs")
        
        # Diagnostics section
        st.subheader("System Diagnostics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Run Health Check", use_container_width=True):
                with st.spinner("Running health check..."):
                    # Simulate health check
                    health_status = {
                        "backend_api": st.session_state.backend_available,
                        "database": True,  # Placeholder
                        "memory": True,    # Placeholder
                        "disk_space": True # Placeholder
                    }
                    
                    for component, status in health_status.items():
                        if status:
                            st.success(f"✅ {component.replace('_', ' ').title()}: OK")
                        else:
                            st.error(f"❌ {component.replace('_', ' ').title()}: FAIL")
        
        with col2:
            if st.button("Export Logs", use_container_width=True):
                if logs_data:
                    logs_text = "\n".join(logs_data.get("logs", []))
                    st.download_button(
                        label="Download Logs",
                        data=logs_text,
                        file_name=f"system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                else:
                    st.error("No logs to export")
    
    def render_settings_tab(self):
        """Render settings and configuration tab"""
        st.header("⚙️ Settings & Configuration")
        
        # Dashboard settings
        st.subheader("Dashboard Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Display Settings**")
            theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
            refresh_interval = st.slider("Refresh Interval (seconds)", 5, 60, 30)
            show_tooltips = st.checkbox("Show Tooltips", value=True)
        
        with col2:
            st.markdown("**Performance Settings**")
            cache_enabled = st.checkbox("Enable Caching", value=True)
            max_history = st.slider("Max History Items", 50, 500, 100)
            concurrent_requests = st.slider("Max Concurrent Requests", 1, 10, 3)
        
        # System settings
        st.subheader("System Configuration")
        
        if st.session_state.backend_available:
            st.info("System configuration can be modified through the backend API")
            
            if st.button("Reload System Configuration"):
                result = asyncio.run(self.api_client.post("/system/control", {
                    "action": "reload_config"
                }))
                if result and result.get("status") == "success":
                    st.success("Configuration reloaded successfully")
                else:
                    st.error("Failed to reload configuration")
        else:
            st.warning("Backend not available - cannot modify system configuration")
        
        # Plugin settings
        st.subheader("Plugin Management")
        
        if self.plugins:
            for plugin_name, plugin in self.plugins.items():
                with st.expander(f"{plugin.get_metadata().get('name', plugin_name)}"):
                    metadata = plugin.get_metadata()
                    st.write(f"**Version:** {metadata.get('version', 'Unknown')}")
                    st.write(f"**Description:** {metadata.get('description', 'No description')}")
                    st.write(f"**Enabled:** {'Yes' if plugin.is_enabled() else 'No'}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Enable", key=f"enable_{plugin_name}"):
                            plugin.enable()
                            st.success(f"Enabled {plugin_name}")
                    with col2:
                        if st.button(f"Disable", key=f"disable_{plugin_name}"):
                            plugin.disable()
                            st.success(f"Disabled {plugin_name}")
        else:
            st.info("No plugins loaded")
    
    def run(self):
        """Run the unified dashboard"""
        # Check backend availability
        st.session_state.backend_available = asyncio.run(self.check_backend_health())
        
        # Load plugins
        self.load_plugins()
        
        # Render header
        self.render_header()
        
        # Render sidebar
        self.render_sidebar()
        
        # Main content area with tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🖥️ System Overview",
            "🤖 Model Management", 
            "👥 Agent Management",
            "📋 Logs & Diagnostics",
            "⚙️ Settings"
        ])
        
        with tab1:
            self.render_system_overview_tab()
        
        with tab2:
            self.render_model_management_tab()
        
        with tab3:
            self.render_agent_management_tab()
        
        with tab4:
            self.render_logs_tab()
        
        with tab5:
            self.render_settings_tab()

# Main execution
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and run dashboard
    dashboard = UnifiedDashboard()
    dashboard.run()
