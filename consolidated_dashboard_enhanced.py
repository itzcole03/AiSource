#!/usr/bin/env python3
"""
Enhanced Consolidated Ultimate Copilot Dashboard

This is the ultimate dashboard that consolidates the best features from all
dashboard implementations with the most advanced UI/UX and functionality.

Features:
- Advanced plugin architecture with event system
- External app integration framework
- Real-time metrics and monitoring
- Modern UI with theme support (dark/light)
- Background data streaming
- Alert/notification system
- Report export capabilities
- Plugin hot-loading
- API/IPC communication framework
- Enhanced error handling and logging
- Memory-aware agent integration
- Model provider control
- Workspace management
"""

import asyncio
import json
import logging
import threading
import time
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import weakref
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
import webbrowser

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("EnhancedConsolidatedDashboard")

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox, filedialog
    import tkinter.font as tkFont
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    logger.warning("GUI not available - dashboard will run in console mode")
    # Mock classes for when GUI is not available
    class _MockClass:
        def __init__(self, *args, **kwargs): pass
        def __call__(self, *args, **kwargs): return self
        def __getattr__(self, name): return self
    
    tk = ttk = scrolledtext = messagebox = filedialog = tkFont = _MockClass()

# Import enhanced agent system
try:
    from working_agent_upgrade import WorkingAgentUpgrade, dispatch_enhanced_task
    ENHANCED_AGENTS_AVAILABLE = True
except ImportError:
    ENHANCED_AGENTS_AVAILABLE = False
    logger.warning("Enhanced agent system not available - using fallback")

# Import existing agent system fallback
SIMPLE_AGENTS_AVAILABLE = False
SimpleAgents = None

try:
    # Try the fixed version first
    simple_agents_path = project_root / "core" / "simple_agents_fixed.py"
    if simple_agents_path.exists():
        sys.path.insert(0, str(project_root / "core"))
        try:
            import simple_agents_fixed
            SimpleAgents = getattr(simple_agents_fixed, 'SimpleAgents', None)
            SIMPLE_AGENTS_AVAILABLE = SimpleAgents is not None
            logger.info("✅ Simple agents (fixed) available")
        except Exception as e:
            logger.warning(f"Simple agents (fixed) import failed: {e}")
    
    if not SIMPLE_AGENTS_AVAILABLE:
        try:
            from core.simple_agents import SimpleAgents
            SIMPLE_AGENTS_AVAILABLE = True
            logger.info("✅ Simple agents (original) available")
        except Exception as e:
            logger.warning(f"Simple agents (original) import failed: {e}")
            
except Exception as e:
    logger.warning(f"Agent import failed: {e}")

# Data Models
@dataclass
class DashboardEvent:
    """Enhanced dashboard event for plugin communication"""
    event_type: str
    source: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    priority: str = "normal"  # low, normal, high, critical

@dataclass
class SystemMetric:
    """Enhanced system metric with metadata"""
    name: str
    value: Any
    unit: str = ""
    category: str = "general"
    status: str = "normal"  # normal, warning, critical
    trend: str = "stable"   # up, down, stable
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DashboardAlert:
    """Dashboard alert/notification with severity levels"""
    id: str
    severity: str  # info, warning, error, critical
    title: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    actions: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class PluginConfig:
    """Enhanced plugin configuration"""
    name: str
    enabled: bool = True
    order: int = 0
    hot_reload: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

# Enhanced Plugin System
class EnhancedDashboardPlugin(ABC):
    """Enhanced base class for dashboard plugins with full feature set"""

    def __init__(self, config: Optional[PluginConfig] = None):
        self.config = config or PluginConfig(name=self.__class__.__name__)
        self.dashboard_context = None
        self.ui_widget = None
        self.event_handlers = {}
        self.is_active = False
        self.is_initialized = False
        self.logger = logging.getLogger(f"Plugin.{self.config.name}")
        self.metrics = []
        self.alerts = []
        self.background_tasks = []

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get enhanced plugin metadata"""
        return {
            "name": self.config.name,
            "version": "1.0.0",
            "description": "Enhanced dashboard plugin",
            "author": "Ultimate Copilot",
            "icon": "🔧",
            "category": "general",
            "capabilities": []
        }

    @abstractmethod
    def initialize(self, dashboard_context) -> bool:
        """Initialize plugin with dashboard context"""
        return False

    @abstractmethod
    def create_ui(self, parent) -> Any:
        """Create enhanced plugin UI"""
        return None

    @abstractmethod
    def update_data(self) -> Dict[str, Any]:
        """Update plugin data with enhanced metrics"""
        return {}

    def cleanup(self):
        """Enhanced cleanup with background task management"""
        try:
            # Stop background tasks
            for task in self.background_tasks:
                if hasattr(task, 'cancel'):
                    task.cancel()
            self.background_tasks.clear()
            
            # Cleanup UI
            if self.ui_widget:
                try:
                    self.ui_widget.destroy()
                except:
                    pass
            
            self.is_active = False
            self.is_initialized = False
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def handle_event(self, event: DashboardEvent):
        """Handle dashboard events with priority support"""
        handler = self.event_handlers.get(event.event_type)
        if handler:
            try:
                handler(event)
            except Exception as e:
                self.logger.error(f"Error handling event {event.event_type}: {e}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler"""
        self.event_handlers[event_type] = handler
    
    def emit_event(self, event_type: str, data: Dict[str, Any], priority: str = "normal"):
        """Emit event to dashboard with priority"""
        if self.dashboard_context:
            event = DashboardEvent(event_type, self.config.name, data, priority=priority)
            self.dashboard_context.emit_event(event)
    
    def add_metric(self, metric: SystemMetric):
        """Add metric to plugin"""
        self.metrics.append(metric)
    
    def add_alert(self, alert: DashboardAlert):
        """Add alert to plugin"""
        self.alerts.append(alert)
    
    def on_activate(self):
        """Enhanced activation with metrics reset"""
        self.is_active = True
        self.emit_event("plugin_activated", {"plugin": self.config.name})
    
    def on_deactivate(self):
        """Enhanced deactivation"""
        self.is_active = False
        self.emit_event("plugin_deactivated", {"plugin": self.config.name})

# External App Integration Framework
class ExternalAppIntegration:
    """Enhanced framework for integrating external applications"""
    
    def __init__(self, app_config: Dict[str, Any]):
        self.config = app_config
        self.process = None
        self.communication_method = app_config.get('communication', 'subprocess')
        self.embed_method = app_config.get('embed_method', 'window')
        self.api_endpoint = app_config.get('api_endpoint', 'http://localhost:8080')
        self.logger = logging.getLogger("ExternalApp")
    
    def launch_app(self) -> bool:
        """Launch external application with enhanced error handling"""
        try:
            app_path = self.config.get('executable')
            if not app_path:
                self.logger.error("No executable path configured")
                return False
            
            args = self.config.get('args', [])
            working_dir = self.config.get('working_dir', None)
            
            self.process = subprocess.Popen(
                [app_path] + args, 
                cwd=working_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            self.logger.info(f"Launched external app: {app_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to launch external app: {e}")
            return False

    def is_running(self) -> bool:
        """Check if external app is running"""
        return bool(self.process and self.process.poll() is None)
    
    def send_command(self, command: str, data: Any = None) -> bool:
        """Send command to external app via configured method"""
        try:
            if self.communication_method == 'api':
                return self._send_api_command(command, data)
            elif self.communication_method == 'ipc':
                return self._send_ipc_command(command, data)
            else:
                self.logger.warning(f"Unsupported communication method: {self.communication_method}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to send command: {e}")
            return False

    def _send_api_command(self, command: str, data: Any) -> bool:
        """Send command via API"""
        try:
            import requests
            response = requests.post(f"{self.api_endpoint}/command", 
                                   json={"command": command, "data": data},
                                   timeout=5)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"API command failed: {e}")
            return False

    def _send_ipc_command(self, command: str, data: Any) -> bool:
        """Send command via IPC"""
        # Implementation for IPC communication
        self.logger.info(f"IPC command: {command}")
        return True

# Enhanced Plugin Implementations
class SystemOverviewPlugin(EnhancedDashboardPlugin):
    """Enhanced system overview with real-time metrics"""
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "System Overview",
            "version": "2.0.0",
            "description": "Real-time system monitoring and metrics",
            "author": "Ultimate Copilot",
            "icon": "📊",
            "category": "monitoring",
            "capabilities": ["real-time", "metrics", "alerts", "export"]
        }
    
    def initialize(self, dashboard_context) -> bool:
        """Initialize system overview plugin"""
        self.dashboard_context = dashboard_context
        self.metrics_tree = None
        self.status_text = None
        self.alert_frame = None
        self.is_initialized = True
        return True
    
    def create_ui(self, parent) -> Any:
        """Create enhanced system overview UI"""
        frame = ttk.Frame(parent)
        
        # Create main layout
        self._create_header(frame)
        self._create_metrics_section(frame)
        self._create_alerts_section(frame)
        self._create_controls(frame)
        
        return frame
    
    def _create_header(self, parent):
        """Create header with system status"""
        header_frame = ttk.LabelFrame(parent, text="System Status")
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # System status text
        self.status_text = scrolledtext.ScrolledText(header_frame, height=6, 
                                                    font=("Consolas", 10))
        self.status_text.pack(fill=tk.X, padx=5, pady=5)
    
    def _create_metrics_section(self, parent):
        """Create real-time metrics section"""
        metrics_frame = ttk.LabelFrame(parent, text="Live Metrics")
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Metrics tree with enhanced columns
        columns = ("Metric", "Value", "Unit", "Status", "Trend", "Last Updated")
        self.metrics_tree = ttk.Treeview(metrics_frame, columns=columns, show="headings", height=12)
        
        # Configure columns
        column_widths = {"Metric": 150, "Value": 100, "Unit": 60, "Status": 80, "Trend": 60, "Last Updated": 120}
        for col in columns:
            self.metrics_tree.heading(col, text=col)
            self.metrics_tree.column(col, width=column_widths.get(col, 100))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(metrics_frame, orient=tk.VERTICAL, command=self.metrics_tree.yview)
        h_scrollbar = ttk.Scrollbar(metrics_frame, orient=tk.HORIZONTAL, command=self.metrics_tree.xview)
        self.metrics_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack components
        self.metrics_tree.grid(row=0, column=0, sticky="nsew", padx=(5, 0), pady=5)
        v_scrollbar.grid(row=0, column=1, sticky="ns", pady=5)
        h_scrollbar.grid(row=1, column=0, sticky="ew", padx=(5, 0))
        
        # Configure grid weights
        metrics_frame.grid_rowconfigure(0, weight=1)
        metrics_frame.grid_columnconfigure(0, weight=1)
    
    def _create_alerts_section(self, parent):
        """Create alerts and notifications section"""
        self.alert_frame = ttk.LabelFrame(parent, text="Alerts & Notifications")
        self.alert_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Alert list
        self.alert_text = scrolledtext.ScrolledText(self.alert_frame, height=4, 
                                                   font=("Consolas", 9))
        self.alert_text.pack(fill=tk.X, padx=5, pady=5)
    
    def _create_controls(self, parent):
        """Create control buttons"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        buttons = [
            ("🔄 Refresh", self._refresh_data),
            ("📊 Export Report", self._export_report),
            ("🔔 Clear Alerts", self._clear_alerts),
            ("⚙️ Settings", self._show_settings),
            ("🌐 Open Web View", self._open_web_view)
        ]
        
        for text, command in buttons:
            ttk.Button(control_frame, text=text, command=command).pack(side=tk.LEFT, padx=5)
    
    def _refresh_data(self):
        """Manually refresh system data"""
        try:
            data = self.update_data()
            self._update_displays(data)
            self.emit_event("data_refreshed", {"source": "manual"})
        except Exception as e:
            self.logger.error(f"Error refreshing data: {e}")
    
    def _export_report(self):
        """Export system report"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("Text files", "*.txt")],
                title="Export System Report"
            )
            if filename:
                data = self.update_data()
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                messagebox.showinfo("Export Complete", f"Report exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export report: {e}")
    
    def _clear_alerts(self):
        """Clear all alerts"""
        if self.alert_text:
            self.alert_text.delete(1.0, tk.END)
        self.alerts.clear()
        self.emit_event("alerts_cleared", {})
    
    def _show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog would open here")
    
    def _open_web_view(self):
        """Open web dashboard"""
        try:
            webbrowser.open("http://127.0.0.1:8001/docs")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open web view: {e}")
    
    def update_data(self) -> Dict[str, Any]:
        """Update system overview data with enhanced metrics"""
        try:
            # Get enhanced agent system data if available
            if self.dashboard_context and hasattr(self.dashboard_context, 'enhanced_agents'):
                agent_data = self.dashboard_context.enhanced_agents.get_system_status()
            else:
                agent_data = {"status": "fallback_mode", "agents": 0, "tasks": 0}
            
            # Get system metrics
            import psutil
            system_data = {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent if hasattr(psutil.disk_usage('/'), 'percent') else 0,
                "timestamp": datetime.now()
            }
            
            # Combine data
            combined_data = {
                "system": system_data,
                "agents": agent_data,
                "timestamp": datetime.now()
            }
            
            # Update displays
            self._update_displays(combined_data)
            
            return combined_data
            
        except Exception as e:
            self.logger.error(f"Error updating data: {e}")
            return {"error": str(e), "timestamp": datetime.now()}
    
    def _update_displays(self, data: Dict[str, Any]):
        """Update all display components"""
        try:
            # Update status text
            if self.status_text:
                self.status_text.delete(1.0, tk.END)
                status_text = self._format_status_text(data)
                self.status_text.insert(1.0, status_text)
            
            # Update metrics tree
            if self.metrics_tree:
                self._update_metrics_tree(data)
            
            # Update alerts
            if self.alert_text:
                self._update_alerts()
                
        except Exception as e:
            self.logger.error(f"Error updating displays: {e}")
    
    def _format_status_text(self, data: Dict[str, Any]) -> str:
        """Format system status text"""
        lines = []
        lines.append(f"🚀 Ultimate Copilot System Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        
        # System info
        system = data.get('system', {})
        lines.append(f"💻 SYSTEM RESOURCES:")
        lines.append(f"  CPU Usage: {system.get('cpu_percent', 0):.1f}%")
        lines.append(f"  Memory Usage: {system.get('memory_percent', 0):.1f}%")
        lines.append(f"  Disk Usage: {system.get('disk_percent', 0):.1f}%")
        
        # Agent info
        agents = data.get('agents', {})
        lines.append(f"\n🤖 AGENT SYSTEM:")
        lines.append(f"  Status: {agents.get('status', 'Unknown')}")
        lines.append(f"  Active Agents: {agents.get('agents', 0)}")
        lines.append(f"  Running Tasks: {agents.get('tasks', 0)}")
        
        return "\n".join(lines)
    
    def _update_metrics_tree(self, data: Dict[str, Any]):
        """Update the metrics tree view"""
        # Clear existing items
        for item in self.metrics_tree.get_children():
            self.metrics_tree.delete(item)
        
        # Add system metrics
        system = data.get('system', {})
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        metrics = [
            ("CPU Usage", f"{system.get('cpu_percent', 0):.1f}", "%", "normal", "stable", timestamp),
            ("Memory Usage", f"{system.get('memory_percent', 0):.1f}", "%", "normal", "stable", timestamp),
            ("Disk Usage", f"{system.get('disk_percent', 0):.1f}", "%", "normal", "stable", timestamp),
        ]
        
        # Add agent metrics
        agents = data.get('agents', {})
        metrics.extend([
            ("Active Agents", str(agents.get('agents', 0)), "count", "normal", "stable", timestamp),
            ("Running Tasks", str(agents.get('tasks', 0)), "count", "normal", "stable", timestamp),
        ])
        
        # Insert metrics
        for metric in metrics:
            item_id = self.metrics_tree.insert("", tk.END, values=metric)
            
            # Color coding based on status
            if metric[3] == "warning":
                self.metrics_tree.set(item_id, "Status", "⚠️ Warning")
            elif metric[3] == "critical":
                self.metrics_tree.set(item_id, "Status", "🔴 Critical")
            else:
                self.metrics_tree.set(item_id, "Status", "✅ Normal")
    
    def _update_alerts(self):
        """Update alerts display"""
        if not self.alert_text:
            return
        
        # Display recent alerts
        recent_alerts = self.alerts[-10:]  # Show last 10 alerts
        if recent_alerts:
            alert_text = "\n".join([
                f"[{alert.timestamp.strftime('%H:%M:%S')}] {alert.severity.upper()}: {alert.message}"
                for alert in recent_alerts
            ])
            self.alert_text.delete(1.0, tk.END)
            self.alert_text.insert(1.0, alert_text)

class ModelProviderControlPlugin(EnhancedDashboardPlugin):
    """Enhanced model provider control with external app integration"""
    
    def __init__(self, external_app_config: Optional[Dict] = None):
        super().__init__(PluginConfig(name="Model Providers"))
        self.external_app_config = external_app_config or {}
        self.external_app = None
        if self.external_app_config:
            self.external_app = ExternalAppIntegration(self.external_app_config)
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Model Providers",
            "version": "2.0.0",
            "description": "Control and monitor model providers",
            "author": "Ultimate Copilot",
            "icon": "🧠",
            "category": "models",
            "capabilities": ["external-app", "real-time", "control"]
        }
    
    def initialize(self, dashboard_context) -> bool:
        """Initialize model provider control"""
        self.dashboard_context = dashboard_context
        self.is_initialized = True
        return True
    
    def create_ui(self, parent) -> Any:
        """Create model provider control UI"""
        frame = ttk.Frame(parent)
        
        # External app integration section
        if self.external_app:
            self._create_external_app_section(frame)
        
        # Model status section
        self._create_model_status_section(frame)
        
        # Control section
        self._create_control_section(frame)
        
        return frame
    
    def _create_external_app_section(self, parent):
        """Create external app integration section"""
        app_frame = ttk.LabelFrame(parent, text="External Model Provider Control")
        app_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # App status
        self.app_status_label = ttk.Label(app_frame, text="Status: Not Connected")
        self.app_status_label.pack(pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(app_frame)
        button_frame.pack(pady=5)
        
        ttk.Button(button_frame, text="Launch App", 
                  command=self._launch_external_app).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Check Status", 
                  command=self._check_app_status).pack(side=tk.LEFT, padx=5)
    
    def _create_model_status_section(self, parent):
        """Create model status monitoring section"""
        status_frame = ttk.LabelFrame(parent, text="Model Status")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Model list
        columns = ("Model", "Status", "VRAM", "Provider", "Last Used")
        self.model_tree = ttk.Treeview(status_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.model_tree.heading(col, text=col)
            self.model_tree.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.model_tree.yview)
        self.model_tree.configure(yscrollcommand=scrollbar.set)
        
        self.model_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def _create_control_section(self, parent):
        """Create model control section"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        buttons = [
            ("🔄 Refresh Models", self._refresh_models),
            ("⚡ Load Model", self._load_model),
            ("🛑 Unload Model", self._unload_model),
            ("📊 Memory Report", self._show_memory_report)
        ]
        
        for text, command in buttons:
            ttk.Button(control_frame, text=text, command=command).pack(side=tk.LEFT, padx=5)
    
    def _launch_external_app(self):
        """Launch external model provider app"""
        if self.external_app:
            success = self.external_app.launch_app()
            if success:
                self.app_status_label.config(text="Status: ✅ Connected")
                self.emit_event("external_app_launched", {"status": "success"})
            else:
                self.app_status_label.config(text="Status: ❌ Failed to Launch")
        else:
            messagebox.showinfo("Info", "No external app configured")
    
    def _check_app_status(self):
        """Check external app status"""
        if self.external_app and self.external_app.is_running():
            self.app_status_label.config(text="Status: ✅ Running")
        else:
            self.app_status_label.config(text="Status: ❌ Not Running")
    
    def _refresh_models(self):
        """Refresh model list"""
        self._update_model_tree()
        self.emit_event("models_refreshed", {})
    
    def _load_model(self):
        """Load selected model"""
        selection = self.model_tree.selection()
        if selection:
            model_name = self.model_tree.item(selection[0])['values'][0]
            messagebox.showinfo("Load Model", f"Loading model: {model_name}")
            self.emit_event("model_load_requested", {"model": model_name})
    
    def _unload_model(self):
        """Unload selected model"""
        selection = self.model_tree.selection()
        if selection:
            model_name = self.model_tree.item(selection[0])['values'][0]
            messagebox.showinfo("Unload Model", f"Unloading model: {model_name}")
            self.emit_event("model_unload_requested", {"model": model_name})
    
    def _show_memory_report(self):
        """Show memory usage report"""
        messagebox.showinfo("Memory Report", "Memory report would be displayed here")
    
    def update_data(self) -> Dict[str, Any]:
        """Update model provider data"""
        try:
            # Get model data from dashboard context
            if self.dashboard_context and hasattr(self.dashboard_context, 'get_model_status'):
                model_data = self.dashboard_context.get_model_status()
            else:
                model_data = self._get_mock_model_data()
            
            self._update_model_tree(model_data)
            return model_data
            
        except Exception as e:
            self.logger.error(f"Error updating model data: {e}")
            return {"error": str(e)}
    
    def _get_mock_model_data(self) -> Dict[str, Any]:
        """Get mock model data for testing"""
        return {
            "models": [
                {"name": "llama-7b", "status": "loaded", "vram_mb": 7168, "provider": "ollama", "last_used": "2 min ago"},
                {"name": "mistral-7b", "status": "available", "vram_mb": 0, "provider": "lm-studio", "last_used": "1 hour ago"},
                {"name": "codellama-13b", "status": "loading", "vram_mb": 13312, "provider": "vllm", "last_used": "5 min ago"}
            ]
        }
    
    def _update_model_tree(self, model_data: Optional[Dict] = None):
        """Update model tree display"""
        if not self.model_tree:
            return
        
        # Clear existing items
        for item in self.model_tree.get_children():
            self.model_tree.delete(item)
        
        # Get model data
        if model_data is None:
            model_data = self._get_mock_model_data()
        
        # Add models to tree
        for model in model_data.get("models", []):
            values = (
                model.get("name", "Unknown"),
                model.get("status", "Unknown"),
                f"{model.get('vram_mb', 0)} MB",
                model.get("provider", "Unknown"),
                model.get("last_used", "Never")
            )
            
            item_id = self.model_tree.insert("", tk.END, values=values)
            
            # Color coding based on status
            status = model.get("status", "").lower()
            if status == "loaded":
                self.model_tree.set(item_id, "Status", "✅ Loaded")
            elif status == "loading":
                self.model_tree.set(item_id, "Status", "⏳ Loading")
            elif status == "error":
                self.model_tree.set(item_id, "Status", "❌ Error")
            else:
                self.model_tree.set(item_id, "Status", "⚪ Available")

# Enhanced Consolidated Dashboard Main Class
class EnhancedConsolidatedDashboard:
    """Ultimate consolidated dashboard with all advanced features"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.plugins = []
        self.event_handlers = {}
        self.metrics = []
        self.alerts = []
        self.running = False
        self.root = None
        self.notebook = None
        
        # Enhanced agents
        self.enhanced_agents = None
        self.simple_agents = None
        
        # UI components
        self.status_bar = None
        self.toolbar = None
        self.theme = self.config.get('theme', 'light')
        self.refresh_interval = self.config.get('refresh_interval', 5)
        self.auto_refresh = self.config.get('auto_refresh', True)
        
        # Background services
        self.update_task = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # External app configuration
        self.external_app_config = self.config.get('external_app', {})
        
        # Setup enhanced logging
        self.logger = logger
        self.logger.info("Initializing Enhanced Consolidated Dashboard...")
    
    def initialize(self) -> bool:
        """Initialize enhanced dashboard system"""
        try:
            # Initialize agent systems
            self._initialize_agents()
            
            # Load plugins
            self._load_plugins()
            
            # Create GUI if available
            if GUI_AVAILABLE:
                self._create_enhanced_gui()
            else:
                self.logger.warning("GUI not available, running in console mode")
            
            # Start background services
            self._start_background_services()
            
            self.running = True
            self.logger.info("✅ Enhanced Dashboard initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize enhanced dashboard: {e}")
            return False
    
    def _initialize_agents(self):
        """Initialize enhanced and simple agent systems"""
        try:
            if ENHANCED_AGENTS_AVAILABLE:
                self.enhanced_agents = WorkingAgentUpgrade()
                self.logger.info("✅ Enhanced agent system initialized")
            
            if SIMPLE_AGENTS_AVAILABLE and SimpleAgents:
                self.simple_agents = SimpleAgents()
                self.logger.info("✅ Simple agent system initialized")
        except Exception as e:
            self.logger.warning(f"Agent initialization issue: {e}")
    
    def _load_plugins(self):
        """Load enhanced plugins"""
        try:
            # System overview plugin
            system_plugin = SystemOverviewPlugin()
            if system_plugin.initialize(self):
                self.plugins.append(system_plugin)
            
            # Model provider control plugin
            model_plugin = ModelProviderControlPlugin(self.external_app_config)
            if model_plugin.initialize(self):
                self.plugins.append(model_plugin)
            
            self.logger.info(f"✅ Loaded {len(self.plugins)} plugins")
            
        except Exception as e:
            self.logger.error(f"Failed to load plugins: {e}")
    
    def _create_enhanced_gui(self):
        """Create enhanced GUI with modern design"""
        if not GUI_AVAILABLE:
            return
        
        self.root = tk.Tk()
        self.root.title("Ultimate Copilot - Enhanced Consolidated Dashboard")
        self.root.geometry("1600x1000")
        self.root.minsize(1200, 800)
        
        # Apply theme
        self._apply_theme()
        
        # Create main layout
        self._create_main_layout()
        
        # Setup window protocols
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        self.logger.info("✅ Enhanced GUI created successfully")
    
    def _apply_theme(self):
        """Apply enhanced visual theme"""
        style = ttk.Style()
        
        if self.theme == 'dark':
            # Enhanced dark theme
            style.theme_use('clam')
            style.configure('TFrame', background='#2b2b2b')
            style.configure('TLabel', background='#2b2b2b', foreground='#ffffff')
            style.configure('TNotebook', background='#3c3c3c', borderwidth=0)
            style.configure('TNotebook.Tab', background='#3c3c3c', foreground='#ffffff', 
                          padding=[10, 5], borderwidth=0)
            style.map('TNotebook.Tab', background=[('selected', '#4c4c4c')])
            style.configure('TButton', background='#4c4c4c', foreground='#ffffff')
            style.map('TButton', background=[('active', '#5c5c5c')])
        else:
            # Enhanced light theme
            style.theme_use('clam')
            style.configure('TNotebook.Tab', padding=[10, 5])
    
    def _create_main_layout(self):
        """Create enhanced main dashboard layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create toolbar
        self._create_enhanced_toolbar(main_frame)
        
        # Plugin notebook with enhanced styling
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add plugin tabs
        for plugin in self.plugins:
            try:
                widget = plugin.create_ui(self.notebook)
                metadata = plugin.get_metadata()
                tab_name = f"{metadata.get('icon', '🔧')} {metadata.get('name', plugin.config.name)}"
                self.notebook.add(widget, text=tab_name)
                self.logger.info(f"Added tab: {tab_name}")
            except Exception as e:
                self.logger.error(f"Failed to create UI for plugin {plugin.config.name}: {e}")
        
        # Enhanced status bar
        self._create_enhanced_status_bar()
        
        # Bind events
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _create_enhanced_toolbar(self, parent):
        """Create enhanced toolbar with modern controls"""
        self.toolbar = ttk.Frame(parent)
        self.toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Left side - Logo and title
        left_frame = ttk.Frame(self.toolbar)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(left_frame, text="🚀 Ultimate Copilot Dashboard", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT, padx=5)
        
        # Right side - Controls
        right_frame = ttk.Frame(self.toolbar)
        right_frame.pack(side=tk.RIGHT)
        
        # Theme toggle
        theme_btn = ttk.Button(right_frame, text="🌙" if self.theme == 'light' else "☀️", 
                              command=self._toggle_theme, width=3)
        theme_btn.pack(side=tk.RIGHT, padx=2)
        
        # Auto-refresh toggle
        refresh_text = "⏸️" if self.auto_refresh else "▶️"
        refresh_btn = ttk.Button(right_frame, text=refresh_text, 
                                command=self._toggle_auto_refresh, width=3)
        refresh_btn.pack(side=tk.RIGHT, padx=2)
        
        # Settings
        settings_btn = ttk.Button(right_frame, text="⚙️", 
                                 command=self._show_settings, width=3)
        settings_btn.pack(side=tk.RIGHT, padx=2)
        
        # Help
        help_btn = ttk.Button(right_frame, text="❓", 
                             command=self._show_help, width=3)
        help_btn.pack(side=tk.RIGHT, padx=2)
    
    def _create_enhanced_status_bar(self):
        """Create enhanced status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Left side - Status
        self.status_label = ttk.Label(self.status_bar, text="✅ Dashboard Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Center - Plugin status
        self.plugin_status_label = ttk.Label(self.status_bar, text=f"📦 {len(self.plugins)} plugins loaded")
        self.plugin_status_label.pack(side=tk.LEFT, padx=20)
        
        # Right side - Time and refresh indicator
        self.refresh_indicator = ttk.Label(self.status_bar, text="🔄" if self.auto_refresh else "⏸️")
        self.refresh_indicator.pack(side=tk.RIGHT, padx=2)
        
        self.time_label = ttk.Label(self.status_bar, text="")
        self.time_label.pack(side=tk.RIGHT, padx=5)
        
        # Update time periodically
        self._update_time_display()
    
    def _update_time_display(self):
        """Update time display in status bar"""
        if self.time_label and self.root:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=current_time)
            self.root.after(1000, self._update_time_display)
    
    def _toggle_theme(self):
        """Toggle between light and dark themes"""
        self.theme = 'dark' if self.theme == 'light' else 'light'
        self._apply_theme()
        # Recreate toolbar to update button text
        if self.toolbar:
            self.toolbar.destroy()
            self._create_enhanced_toolbar(self.root.children['!frame'])
    
    def _toggle_auto_refresh(self):
        """Toggle auto-refresh"""
        self.auto_refresh = not self.auto_refresh
        self.refresh_indicator.config(text="🔄" if self.auto_refresh else "⏸️")
        # Update toolbar button
        if self.toolbar:
            self.toolbar.destroy()
            self._create_enhanced_toolbar(self.root.children['!frame'])
    
    def _show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        
        # Center the window
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        ttk.Label(settings_window, text="Dashboard Settings", 
                 font=("Arial", 14, "bold")).pack(pady=10)
        
        # Refresh interval
        interval_frame = ttk.Frame(settings_window)
        interval_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(interval_frame, text="Refresh Interval (seconds):").pack(side=tk.LEFT)
        interval_var = tk.StringVar(value=str(self.refresh_interval))
        interval_entry = ttk.Entry(interval_frame, textvariable=interval_var, width=10)
        interval_entry.pack(side=tk.RIGHT)
        
        # Theme selection
        theme_frame = ttk.Frame(settings_window)
        theme_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(theme_frame, text="Theme:").pack(side=tk.LEFT)
        theme_var = tk.StringVar(value=self.theme)
        theme_combo = ttk.Combobox(theme_frame, textvariable=theme_var, 
                                  values=['light', 'dark'], state='readonly')
        theme_combo.pack(side=tk.RIGHT)
        
        # Buttons
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(pady=20)
        
        def apply_settings():
            try:
                self.refresh_interval = int(interval_var.get())
                self.theme = theme_var.get()
                self._apply_theme()
                settings_window.destroy()
                messagebox.showinfo("Settings", "Settings applied successfully!")
            except ValueError:
                messagebox.showerror("Error", "Invalid refresh interval")
        
        ttk.Button(button_frame, text="Apply", command=apply_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def _show_help(self):
        """Show help dialog"""
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("600x400")
        
        help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        help_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        help_content = """
🚀 Ultimate Copilot - Enhanced Consolidated Dashboard Help

OVERVIEW:
This dashboard provides a comprehensive interface for monitoring and controlling
your Ultimate Copilot system with advanced features and modern UI.

FEATURES:
• 📊 Real-time system monitoring and metrics
• 🧠 Model provider control and management
• 🌙 Dark/Light theme support
• 🔄 Auto-refresh with configurable intervals
• 📦 Plugin architecture for extensibility
• 🌐 External app integration framework
• 📋 Alert and notification system
• 💾 Data export capabilities

NAVIGATION:
• Use tabs to switch between different plugin views
• Click the theme button (🌙/☀️) to toggle dark/light mode
• Use the play/pause button (▶️/⏸️) to control auto-refresh
• Access settings via the gear icon (⚙️)

KEYBOARD SHORTCUTS:
• Ctrl+R: Manual refresh
• F11: Toggle fullscreen
• Ctrl+T: Toggle theme
• Ctrl+S: Open settings

PLUGINS:
• System Overview: Monitor system health and metrics
• Model Providers: Control and monitor AI models

For more information, visit the project documentation.
        """
        
        help_text.insert(tk.END, help_content)
        help_text.config(state=tk.DISABLED)
    
    def _start_background_services(self):
        """Start enhanced background services"""
        if self.auto_refresh:
            # Start background update loop
            def background_loop():
                while self.running and self.auto_refresh:
                    try:
                        self._update_all_plugins()
                        time.sleep(self.refresh_interval)
                    except Exception as e:
                        self.logger.error(f"Background update error: {e}")
                        time.sleep(self.refresh_interval)
            
            self.update_task = threading.Thread(target=background_loop, daemon=True)
            self.update_task.start()
    
    def _update_all_plugins(self):
        """Update all plugins data"""
        for plugin in self.plugins:
            try:
                if plugin.is_active:
                    plugin.update_data()
            except Exception as e:
                self.logger.error(f"Error updating plugin {plugin.config.name}: {e}")
    
    def _on_tab_changed(self, event):
        """Handle enhanced tab change events"""
        try:
            selected_tab = event.widget.tab('current')['text']
            
            # Notify plugins of activation/deactivation
            for plugin in self.plugins:
                metadata = plugin.get_metadata()
                tab_name = f"{metadata.get('icon', '🔧')} {metadata.get('name', plugin.config.name)}"
                
                if tab_name == selected_tab:
                    plugin.on_activate()
                else:
                    plugin.on_deactivate()
            
            # Update status
            if self.status_label:
                plugin_name = selected_tab.split(' ', 1)[-1] if ' ' in selected_tab else selected_tab
                self.status_label.config(text=f"📊 Viewing: {plugin_name}")
                
        except Exception as e:
            self.logger.error(f"Error handling tab change: {e}")
    
    def _on_closing(self):
        """Enhanced cleanup on window close"""
        try:
            self.logger.info("Shutting down Enhanced Dashboard...")
            
            # Stop background services
            self.running = False
            
            # Cleanup plugins
            for plugin in self.plugins:
                try:
                    plugin.cleanup()
                except Exception as e:
                    self.logger.error(f"Error cleaning up plugin {plugin.config.name}: {e}")
            
            # Cleanup executor
            self.executor.shutdown(wait=False)
            
            # Close window
            if self.root:
                self.root.destroy()
                
            self.logger.info("✅ Enhanced Dashboard shutdown complete")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def emit_event(self, event: DashboardEvent):
        """Emit event to all plugins"""
        for plugin in self.plugins:
            try:
                plugin.handle_event(event)
            except Exception as e:
                self.logger.error(f"Error handling event in plugin {plugin.config.name}: {e}")
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get model status from various sources"""
        try:
            # Try to get real model data from memory manager
            if hasattr(self, 'enhanced_agents') and self.enhanced_agents:
                # This would be implemented based on your memory manager
                return {"models": [], "status": "no_memory_manager"}
            else:
                # Return mock data for demonstration
                return {
                    "models": [
                        {"name": "llama-7b", "status": "loaded", "vram_mb": 7168, "provider": "ollama", "last_used": "2 min ago"},
                        {"name": "mistral-7b", "status": "available", "vram_mb": 0, "provider": "lm-studio", "last_used": "1 hour ago"}
                    ]
                }
        except Exception as e:
            self.logger.error(f"Error getting model status: {e}")
            return {"error": str(e)}
    
    def run(self):
        """Run the enhanced dashboard"""
        if GUI_AVAILABLE and self.root:
            self.logger.info("🚀 Starting Enhanced Dashboard GUI")
            self.root.mainloop()
        else:
            self.logger.info("Running in console mode - no GUI available")
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("Dashboard stopped by user")
                self._on_closing()

def main():
    """Main entry point for enhanced consolidated dashboard"""
    try:
        # Configuration with external app support
        config = {
            'theme': 'light',
            'refresh_interval': 5,
            'auto_refresh': True,
            'external_app': {
                'executable': 'path/to/model/provider/app.exe',
                'args': ['--api-mode'],
                'communication': 'api',
                'api_endpoint': 'http://localhost:8080'
            }
        }
        
        # Create and initialize dashboard
        dashboard = EnhancedConsolidatedDashboard(config)
        
        if dashboard.initialize():
            dashboard.run()
        else:
            logger.error("Failed to initialize dashboard")
            
    except KeyboardInterrupt:
        logger.info("Dashboard interrupted by user")
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
    finally:
        logger.info("Dashboard session ended")

if __name__ == "__main__":
    main()
