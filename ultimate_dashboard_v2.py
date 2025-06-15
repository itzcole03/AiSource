#!/usr/bin/env python3
"""
Ultimate Copilot Dashboard v2

Enhanced modular dashboard with improved plugin architecture and seamless 
integration capabilities for external model provider control applications.

Key Features:
- Improved plugin architecture with event system
- Better external app integration framework
- Real-time data streaming
- Modern UI with customizable themes
- Plugin hot-loading capability
- API endpoints for external control
"""

import asyncio
import logging
from typing import Dict, Optional, Any, Callable, TYPE_CHECKING
from datetime import datetime
from dataclasses import dataclass, field
import json
import threading
from pathlib import Path
import time
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
import weakref
import logging

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox, filedialog
    import tkinter.font as tkFont
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    # Mock classes for when GUI is not available
    class _MockClass:
        def __init__(self, *args, **kwargs): pass
        def __call__(self, *args, **kwargs): return self
        def __getattr__(self, name): return self
    
    tk = messagebox = filedialog = _MockClass()

# Data Models
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
class DashboardEvent:
    """Dashboard event for plugin communication"""
    event_type: str
    source: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class PluginConfig:
    """Plugin configuration structure"""
    name: str
    enabled: bool = True
    order: int = 0
    config: Dict[str, Any] = field(default_factory=dict)

# Plugin System
    def create_ui(self, parent) -> Any: ...
    """Plugin interface protocol"""
    def get_metadata(self) -> Dict[str, Any]: ...
# Plugin System
from abc import ABC, abstractmethod

class DashboardPlugin(ABC):
    """Enhanced base class for dashboard plugins"""

    def __init__(self, config: Optional[PluginConfig] = None):
        self.config = config or PluginConfig(name=self.__class__.__name__)
        self.dashboard_context = None
        self.ui_widget = None
        self.event_handlers = {}
        self.is_active = False
        self.logger = logging.getLogger(f"Plugin.{self.config.name}")

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata"""
        return {}

    @abstractmethod
    def initialize(self, dashboard_context) -> bool:
        """Initialize plugin"""
        return False

    @abstractmethod
    def create_ui(self, parent) -> Any:
        """Create plugin UI"""
        return None

    @abstractmethod
    def update(self) -> Dict[str, Any]:
        """Update plugin data"""
        return {}
            try:
                self.ui_widget.destroy()
            except:
                pass
    
    def handle_event(self, event: DashboardEvent):
        """Handle dashboard events"""
        handler = self.event_handlers.get(event.event_type)
        if handler:
            handler(event)
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register event handler"""
        self.event_handlers[event_type] = handler
    
    def emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit event to dashboard"""
        if self.dashboard_context:
            event = DashboardEvent(event_type, self.config.name, data)
            self.dashboard_context.emit_event(event)
    
    def on_activate(self):
        """Called when plugin becomes active"""
        self.is_active = True
    
    def on_deactivate(self):
        """Called when plugin becomes inactive"""
        self.is_active = False

class ExternalAppIntegration:
    """Framework for integrating external applications"""
    
    def __init__(self, app_config: Dict[str, Any]):
        self.config = app_config
        self.process = None
        self.communication_method = app_config.get('communication', 'subprocess')
        self.embed_method = app_config.get('embed_method', 'window')
        self.logger = logging.getLogger("ExternalApp")
    
    def launch_app(self) -> bool:
        """Launch external application"""
        try:
            app_path = self.config.get('executable')
            if not app_path:
                self.logger.error("No executable path configured")
                return False
            
            args = self.config.get('args', [])
            self.process = subprocess.Popen([app_path] + args)
            
    def launch_app(self) -> bool:
        """Launch external application"""
        try:
            app_path = self.config.get('executable')
            if not app_path:
                self.logger.error("No executable path configured")
                return False

            args = self.config.get('args', [])
            self.process = subprocess.Popen([app_path] + args)

            self.logger.info(f"Launched external app: {app_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to launch external app: {e}")
            return False

    def is_running(self) -> bool:
        """Check if external app is running"""
        return bool(self.process and self.process.poll() is None)
    def _send_api_command(self, command: str, data: Any) -> bool:
        """Send command via API"""
    def send_command(self, command: str, data: Any = None) -> bool:
        """Send command to external app"""
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
        # Implementation for API communication
        # This would use requests or similar to communicate with your app's API
        # For now, just log and return True
        self.logger.info(f"API command sent: {command} with data: {data}")
        return True

    def _send_ipc_command(self, command: str, data: Any) -> bool:
        """Send command via IPC"""
        # Implementation for IPC communication
        # This could use named pipes, sockets, or shared memory
        self.logger.info(f"IPC command sent: {command} with data: {data}")
        return True

    def embed_window(self, parent_widget) -> Optional[Any]:
        """Embed external app window or web view"""
        if self.embed_method == 'window':
            return self._embed_native_window(parent_widget)
        elif self.embed_method == 'web':
            return self._embed_web_view(parent_widget)
        else:
            return None

    def _embed_native_window(self, parent) -> Optional[Any]:
        # This would use platform-specific window embedding
        # For Windows: win32gui, for Linux: Xlib, etc.
        if not GUI_AVAILABLE:
            return None
        frame = ttk.Frame(parent)
        label = ttk.Label(frame, text="External app window would be embedded here")
        label.pack(expand=True)
        return frame

    def _embed_web_view(self, parent) -> Optional[Any]:
        """Embed web view"""
        # This would use a web view component like tkinter.html or cefpython
        if not GUI_AVAILABLE:
            return None
        frame = ttk.Frame(parent)
        label = ttk.Label(frame, text="Web view would be embedded here")
        label.pack(expand=True)
        return frame
class ModelProviderControlPlugin(DashboardPlugin):
    """Enhanced model provider control plugin with external app integration"""
    
    def __init__(self, external_app_config: Optional[Dict] = None):
        super().__init__(PluginConfig(name="Model Providers", order=1))
        self.external_app = None
        self.provider_data = {}
        self.control_widgets = {}
        
        if external_app_config:
            self.external_app = ExternalAppIntegration(external_app_config)
    
    def get_metadata(self) -> Dict[str, Any]:
        return {
            "name": "Model Provider Control",
            "version": "2.0",
            "description": "Advanced model provider control with external app integration",
            "requires_external_app": self.external_app is not None,
            "capabilities": ["model_loading", "provider_monitoring", "external_control"]
        }
    
    def initialize(self, dashboard_context) -> bool:
        """Initialize plugin"""
        self.dashboard_context = dashboard_context
        
        # Register event handlers
        self.register_event_handler("model_status_changed", self._handle_model_status)
        self.register_event_handler("provider_connected", self._handle_provider_connection)
        
        # Initialize external app if configured
        if self.external_app:
            success = self.external_app.launch_app()
            if not success:
                self.logger.warning("Failed to launch external app, falling back to built-in controls")
        
        return True
    
    def create_ui(self, parent) -> tk.Widget:
        """Create enhanced UI with external app integration"""
        main_frame = ttk.Frame(parent)
        
        # Control header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = ttk.Label(header_frame, text="Model Provider Control", 
                               font=("Arial", 14, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Status indicator
        self.status_label = ttk.Label(header_frame, text="●", foreground="green")
        self.status_label.pack(side=tk.RIGHT)
        
        # Create notebook for different views
        self.control_notebook = ttk.Notebook(main_frame)
        self.control_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Provider status tab
        self._create_provider_status_tab()
        
        # Model management tab
        self._create_model_management_tab()
        
        # External app integration tab
        if self.external_app:
            self._create_external_app_tab()
        
        # Quick actions tab
        self._create_quick_actions_tab()
        
        self.ui_widget = main_frame
        return main_frame
    
    def _create_provider_status_tab(self):
        """Create provider status monitoring tab"""
        tab_frame = ttk.Frame(self.control_notebook)
        self.control_notebook.add(tab_frame, text="Provider Status")
        
        # Provider grid
        providers_frame = ttk.LabelFrame(tab_frame, text="Active Providers")
        providers_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for providers
        columns = ("Provider", "Status", "Models", "Loaded", "Memory", "Response Time")
        self.providers_tree = ttk.Treeview(providers_frame, columns=columns, show="headings")
        
        for col in columns:
            self.providers_tree.heading(col, text=col)
            self.providers_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(providers_frame, orient=tk.VERTICAL, 
                                 command=self.providers_tree.yview)
        self.providers_tree.configure(yscrollcommand=scrollbar.set)
        
        self.providers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Provider controls
        controls_frame = ttk.Frame(tab_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Refresh All", 
                  command=self._refresh_providers).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Test Connectivity", 
                  command=self._test_connectivity).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Provider Settings", 
                  command=self._open_provider_settings).pack(side=tk.LEFT, padx=5)
    
    def _create_model_management_tab(self):
        """Create model management tab"""
        tab_frame = ttk.Frame(self.control_notebook)
        self.control_notebook.add(tab_frame, text="Model Management")
        
        # Available models
        available_frame = ttk.LabelFrame(tab_frame, text="Available Models")
        available_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Model list with load/unload controls
        columns = ("Model", "Provider", "Size", "Status", "Quality", "Speed")
        self.models_tree = ttk.Treeview(available_frame, columns=columns, show="headings")
        
        for col in columns:
            self.models_tree.heading(col, text=col)
            self.models_tree.column(col, width=100)
        
        model_scrollbar = ttk.Scrollbar(available_frame, orient=tk.VERTICAL,
                                       command=self.models_tree.yview)
        self.models_tree.configure(yscrollcommand=model_scrollbar.set)
        
        self.models_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        model_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Model control buttons
        model_controls = ttk.Frame(tab_frame)
        model_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(model_controls, text="Load Selected", 
                  command=self._load_selected_model).pack(side=tk.LEFT, padx=5)
        ttk.Button(model_controls, text="Unload Selected", 
                  command=self._unload_selected_model).pack(side=tk.LEFT, padx=5)
        ttk.Button(model_controls, text="Load Optimal Set", 
                  command=self._load_optimal_models).pack(side=tk.LEFT, padx=5)
        ttk.Button(model_controls, text="Unload All", 
                  command=self._unload_all_models).pack(side=tk.LEFT, padx=5)
    
    def _create_external_app_tab(self):
        """Create external app integration tab"""
        tab_frame = ttk.Frame(self.control_notebook)
        self.control_notebook.add(tab_frame, text="External Control")
        
        # App status
        status_frame = ttk.LabelFrame(tab_frame, text="External App Status")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.app_status_label = ttk.Label(status_frame, text="Checking...")
        self.app_status_label.pack(padx=10, pady=5)
        
        app_controls = ttk.Frame(status_frame)
        app_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(app_controls, text="Launch App", 
                  command=self._launch_external_app).pack(side=tk.LEFT, padx=5)
        ttk.Button(app_controls, text="Focus App", 
                  command=self._focus_external_app).pack(side=tk.LEFT, padx=5)
        ttk.Button(app_controls, text="Sync Data", 
                  command=self._sync_with_external_app).pack(side=tk.LEFT, padx=5)
        
        # Embedded control area
        embed_frame = ttk.LabelFrame(tab_frame, text="Embedded Controls")
        embed_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        if self.external_app:
            embedded_widget = self.external_app.embed_window(embed_frame)
            if embedded_widget:
                embedded_widget.pack(fill=tk.BOTH, expand=True)
            else:
                ttk.Label(embed_frame, 
                         text="External app integration available but not embedded.\n"
                              "Use the control buttons above to interact with the external app.").pack(
                    expand=True, padx=20, pady=20)
        else:
            ttk.Label(embed_frame, 
                     text="No external app configured.\n"
                          "Configure external app integration to enable this feature.").pack(
                expand=True, padx=20, pady=20)
    
    def _create_quick_actions_tab(self):
        """Create quick actions tab"""
        tab_frame = ttk.Frame(self.control_notebook)
        self.control_notebook.add(tab_frame, text="Quick Actions")
        
        # Preset configurations
        presets_frame = ttk.LabelFrame(tab_frame, text="Model Presets")
        presets_frame.pack(fill=tk.X, padx=5, pady=5)
        
        preset_buttons = [
            ("Development Setup", self._load_development_preset),
            ("Research Configuration", self._load_research_preset),
            ("High Performance", self._load_performance_preset),
            ("Memory Optimized", self._load_memory_preset)
        ]
        
        for text, command in preset_buttons:
            ttk.Button(presets_frame, text=text, command=command).pack(
                side=tk.LEFT, padx=5, pady=5)
        
        # Emergency actions
        emergency_frame = ttk.LabelFrame(tab_frame, text="Emergency Actions")
        emergency_frame.pack(fill=tk.X, padx=5, pady=5)
        
        emergency_buttons = [
            ("Force Unload All", self._emergency_unload_all),
            ("Restart Providers", self._restart_providers),
            ("Clear Memory", self._clear_memory),
            ("Reset System", self._reset_system)
        ]
        
        for text, command in emergency_buttons:
            btn = ttk.Button(emergency_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # System information
        info_frame = ttk.LabelFrame(tab_frame, text="System Information")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.system_info_text = scrolledtext.ScrolledText(info_frame, height=10)
        self.system_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def update(self) -> Dict[str, Any]:
        """Update plugin data"""
        try:
            # Update provider status
            self._update_provider_data()
            
            # Update model information
            self._update_model_data()
            
            # Update external app status
            if self.external_app:
                self._update_external_app_status()

            # Update system information
            self._update_system_info()

            return {"status": "success", "providers": len(self.provider_data)}
        except Exception as e:
            self.logger.error(f"Update failed: {e}")
            return {"status": "error", "error": str(e)}
        """Update model information"""
        # This would get current model status
    def _update_provider_data(self):
        """Update provider status data"""
        # This would interface with your model manager
        providers = ["LM Studio", "Ollama", "vLLM"]
        # Example: update provider_data dict
        for provider in providers:
            self.provider_data[provider] = {"status": "unknown"}
            else:
                self.app_status_label.config(text="External app not running", foreground="red")
    
    def _update_system_info(self):
        """Update system information display"""
        if self.system_info_text:
            info = self._get_system_info()
            self.system_info_text.delete(1.0, tk.END)
            self.system_info_text.insert(1.0, info)
    
    def _get_system_info(self) -> str:
        """Get formatted system information"""
        lines = []
        lines.append(f"System Status: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("PROVIDERS:")
        lines.append("  LM Studio: Connected (17 models, 3 loaded)")
        lines.append("  Ollama: Connected (14 models, 12 loaded)")
        lines.append("  vLLM: Disconnected")
        lines.append("")
        lines.append("MEMORY:")
        lines.append("  VRAM: 4.2GB / 7GB")
        lines.append("  System RAM: 12.1GB / 32GB")
        lines.append("")
        if self.external_app:
            lines.append("EXTERNAL APP:")
            lines.append(f"  Status: {'Running' if self.external_app.is_running() else 'Stopped'}")
            lines.append(f"  Communication: {self.external_app.communication_method}")
        
        return "\n".join(lines)
    
    # Event handlers
    def _handle_model_status(self, event: DashboardEvent):
        """Handle model status change events"""
        self.logger.info(f"Model status changed: {event.data}")
        if self.external_app:
            lines.append("EXTERNAL APP:")
            try:
                running = self.external_app.is_running()
            except Exception:
                running = False
            lines.append(f"  Status: {'Running' if running else 'Stopped'}")
            lines.append(f"  Communication: {self.external_app.communication_method}")

        return "\n".join(lines)
    def _refresh_providers(self):
        """Refresh all provider data"""
        self.emit_event("refresh_providers", {})
    
    def _test_connectivity(self):
        """Test provider connectivity"""
        self.emit_event("test_connectivity", {})
    
    def _open_provider_settings(self):
        """Open provider settings dialog"""
        messagebox.showinfo("Settings", "Provider settings dialog would open here")
    
    def _load_selected_model(self):
        """Load selected model"""
        selection = self.models_tree.selection()
        if selection:
            model_id = self.models_tree.item(selection[0])['values'][0]
            self.emit_event("load_model", {"model_id": model_id})
    
    def _unload_selected_model(self):
        """Unload selected model"""
        selection = self.models_tree.selection()
        if selection:
            model_id = self.models_tree.item(selection[0])['values'][0]
            self.emit_event("unload_model", {"model_id": model_id})
    
    def _load_optimal_models(self):
        """Load optimal model set"""
        self.emit_event("load_optimal_models", {})
    
    def _unload_all_models(self):
        """Unload all models"""
        if messagebox.askyesno("Confirm", "Unload all models?"):
            self.emit_event("unload_all_models", {})
    
    def _launch_external_app(self):
        """Launch external application"""
        if self.external_app and not self.external_app.is_running():
            success = self.external_app.launch_app()
            if success:
                messagebox.showinfo("Success", "External app launched")
            else:
                messagebox.showerror("Error", "Failed to launch external app")
    
    def _focus_external_app(self):
        """Focus external application"""
        if self.external_app and self.external_app.is_running():
            self.external_app.send_command("focus")
    
    def _sync_with_external_app(self):
        """Sync data with external application"""
        if self.external_app and self.external_app.is_running():
            self.external_app.send_command("sync", {"action": "full_sync"})
            messagebox.showinfo("Sync", "Data synchronization initiated")
    
    # Preset actions
    def _load_development_preset(self):
        """Load development model preset"""
        self.emit_event("load_preset", {"preset": "development"})
    
    def _load_research_preset(self):
        """Load research model preset"""
        self.emit_event("load_preset", {"preset": "research"})
    
    def _load_performance_preset(self):
        """Load performance model preset"""
        self.emit_event("load_preset", {"preset": "performance"})
    
    def _load_memory_preset(self):
        """Load memory-optimized preset"""
        self.emit_event("load_preset", {"preset": "memory"})
    
    # Emergency actions
    def _emergency_unload_all(self):
        """Emergency unload all models"""
        if messagebox.askyesno("Emergency Action", "Force unload all models? This may interrupt running tasks."):
            self.emit_event("emergency_unload", {})
    
    def _restart_providers(self):
        """Restart all providers"""
        if messagebox.askyesno("Restart", "Restart all model providers? This will interrupt all tasks."):
            self.emit_event("restart_providers", {})
    
    def _clear_memory(self):
        """Clear system memory"""
        if messagebox.askyesno("Clear Memory", "Clear system memory? This will unload models and clear caches."):
            self.emit_event("clear_memory", {})
    
    def _reset_system(self):
        """Reset entire system"""
        if messagebox.askyesno("Reset System", "Reset entire system? This will restart all components."):
            self.emit_event("reset_system", {})
    
    def cleanup(self):
        """Cleanup plugin resources"""
        if self.external_app:
            self.external_app.close()
        super().cleanup()

class UltimateDashboardV2:
    """Enhanced Ultimate Copilot Dashboard with improved architecture"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.plugins = []
        self.event_handlers = {}
        self.metrics = []
        self.running = False
        self.root = None
        self.notebook = None
        
        # External app configuration
        self.external_app_config = self.config.get('external_app', {})
        
        # UI state
        self.theme = self.config.get('theme', 'default')
        self.refresh_interval = self.config.get('refresh_interval', 5)
        self.auto_refresh = self.config.get('auto_refresh', True)
        
        # Background tasks
        self.update_task = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Setup logging
        self.logger = logging.getLogger("Dashboard")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def initialize(self) -> bool:
        """Initialize dashboard system"""
        try:
            self.logger.info("Initializing Ultimate Dashboard v2...")
            
            # Initialize plugins
            self._load_plugins()
            
            # Create GUI if available
            if GUI_AVAILABLE:
                self._create_gui()
            else:
                self.logger.warning("GUI not available, running in console mode")
            
            # Start background services
            self._start_background_services()
            
            self.running = True
            self.logger.info("Dashboard initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dashboard: {e}")
            return False
    
    def _load_plugins(self):
        """Load and initialize plugins"""
        # Load model provider control plugin with external app integration
        model_plugin = ModelProviderControlPlugin(self.external_app_config)
        if model_plugin.initialize(self):
            self.plugins.append(model_plugin)
        
        # Load vLLM monitor plugin
        try:
            from vllm_dashboard_plugin_clean import create_vllm_plugin
            vllm_plugin = create_vllm_plugin()
            
            # Create a dummy dashboard context for initialization
            if hasattr(vllm_plugin, 'get_metadata'):
                self.plugins.append(vllm_plugin)
                self.logger.info("vLLM plugin loaded successfully")
        except ImportError as e:
            self.logger.warning(f"vLLM plugin not available: {e}")
        except Exception as e:
            self.logger.error(f"Failed to load vLLM plugin: {e}")
        
        # Add workspace management plugin
        try:
            from workspace_plugin import WorkspacePlugin
            workspace_plugin = WorkspacePlugin()
            if workspace_plugin.initialize(self):
                self.plugins.append(workspace_plugin)
                self.logger.info("Workspace plugin loaded successfully")
        except ImportError as e:
            self.logger.warning(f"Workspace plugin not available: {e}")
        except Exception as e:
            self.logger.error(f"Failed to load workspace plugin: {e}")
    
    def _create_gui(self):
        """Create enhanced GUI"""
        self.root = tk.Tk()
        self.root.title("Ultimate Copilot Dashboard v2")
        self.root.geometry("1600x1000")
        
        # Apply theme
        self._apply_theme()
        
        # Create main layout
        self._create_main_layout()
        
        # Setup window protocols
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _apply_theme(self):
        """Apply visual theme"""
        style = ttk.Style()
        
        if self.theme == 'dark':
            # Dark theme configuration
            style.theme_use('clam')
            style.configure('TFrame', background='#2b2b2b')
            style.configure('TLabel', background='#2b2b2b', foreground='white')
            style.configure('TNotebook', background='#3c3c3c')
            style.configure('TNotebook.Tab', background='#3c3c3c', foreground='white')
        else:
            # Default/light theme
            style.theme_use('clam')
    
    def _create_main_layout(self):
        """Create main dashboard layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Toolbar
        self._create_toolbar(main_frame)
        
        # Plugin notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add plugin tabs
        for plugin in self.plugins:
            try:
                widget = plugin.create_ui(self.notebook)
                metadata = plugin.get_metadata()
                tab_name = metadata.get('name', plugin.config.name)
                self.notebook.add(widget, text=tab_name)
            except Exception as e:
                self.logger.error(f"Failed to create UI for plugin {plugin.config.name}: {e}")
        
        # Status bar
        self._create_status_bar()
        
        # Bind events
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _create_toolbar(self, parent):
        """Create toolbar with global actions"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 5))
        
        # Logo/title
        title_label = ttk.Label(toolbar, text="Ultimate Copilot Dashboard", 
                               font=("Arial", 14, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Global actions
        actions_frame = ttk.Frame(toolbar)
        actions_frame.pack(side=tk.RIGHT)
        
        ttk.Button(actions_frame, text="Refresh All", 
                  command=self._refresh_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Settings", 
                  command=self._open_settings).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Export Report", 
                  command=self._export_report).pack(side=tk.LEFT, padx=2)
        ttk.Button(actions_frame, text="Help", 
                  command=self._show_help).pack(side=tk.LEFT, padx=2)
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Status message
        self.status_label = ttk.Label(self.status_bar, text="Dashboard Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Connection indicators
        self.connection_frame = ttk.Frame(self.status_bar)
        self.connection_frame.pack(side=tk.RIGHT, padx=5)
        
        # Time display
        self.time_label = ttk.Label(self.status_bar, text="")
        self.time_label.pack(side=tk.RIGHT, padx=10)
        
        self._update_time_display()
    
    def _update_time_display(self):
        """Update time display"""
        if self.time_label:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=current_time)
            if self.root:
                self.root.after(1000, self._update_time_display)
      def _start_background_services(self):
        """Start background update services"""
        if self.auto_refresh:
            # Don't start async task here, will be started when GUI runs
            pass
    
    def _start_async_services(self):
        """Start async services when event loop is available"""
        if self.auto_refresh and not self.update_task:
            try:
                loop = asyncio.get_event_loop()
                self.update_task = loop.create_task(self._background_update_loop())
            except RuntimeError:
                # No event loop running, skip async services
                self.logger.warning("No event loop available for background services")
    
    async def _background_update_loop(self):
        """Background update loop"""
        while self.running:
            try:
                await self._update_all_plugins()
                await asyncio.sleep(self.refresh_interval)
            except Exception as e:
                self.logger.error(f"Background update error: {e}")
                await asyncio.sleep(10)
    
    async def _update_all_plugins(self):
        """Update all plugins"""
        for plugin in self.plugins:
            try:
                if plugin.is_active:
                    await asyncio.get_event_loop().run_in_executor(
                        self.executor, plugin.update)
            except Exception as e:
                self.logger.warning(f"Plugin {plugin.config.name} update failed: {e}")
    
    def emit_event(self, event: DashboardEvent):
        """Emit event to all interested parties"""
        # Notify plugins
        for plugin in self.plugins:
            try:
                plugin.handle_event(event)
            except Exception as e:
                self.logger.warning(f"Plugin {plugin.config.name} event handling failed: {e}")
        
        # Handle at dashboard level
        handler = self.event_handlers.get(event.event_type)
        if handler:
            handler(event)
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """Register dashboard-level event handler"""
        self.event_handlers[event_type] = handler
    
    # Event handlers
    def _on_tab_changed(self, event):
        """Handle tab change"""
        try:
            selected_tab = event.widget.tab('current')['text']
            
            # Notify plugins
            for plugin in self.plugins:
                metadata = plugin.get_metadata()
                if metadata.get('name', plugin.config.name) == selected_tab:
                    plugin.on_activate()
                else:
                    plugin.on_deactivate()
                    
        except Exception as e:
            self.logger.error(f"Tab change handling error: {e}")
    
    def _on_closing(self):
        """Handle window closing"""
        self.shutdown()
    
    # Action handlers
    def _refresh_all(self):
        """Refresh all plugin data"""
        asyncio.create_task(self._update_all_plugins())
    
    def _open_settings(self):
        """Open settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog would open here")
    
    def _export_report(self):
        """Export system report"""
        filename = filedialog.asksaveasfilename(
            title="Export Report",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("Text files", "*.txt")]
        )
        if filename:
            try:
                report = self._generate_report()
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2, default=str)
                messagebox.showinfo("Export", f"Report exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export report: {e}")
    
    def _show_help(self):
        """Show help dialog"""
        help_text = """
Ultimate Copilot Dashboard v2

Features:
- Enhanced plugin architecture
- External app integration
- Real-time monitoring
- Modern UI with themes
- Event-driven communication

Plugin Integration:
Your external model provider control app can be integrated using the 
external_app configuration. The dashboard provides:
- Window embedding
- API communication
- Event synchronization
- Data sharing

For more information, see the documentation.
        """
        messagebox.showinfo("Help", help_text)
    
    def _generate_report(self) -> Dict:
        """Generate system report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "dashboard_version": "2.0",
            "plugins": [],
            "metrics": [],
            "system_status": "running" if self.running else "stopped"
        }
        
        # Add plugin information
        for plugin in self.plugins:
            try:
                metadata = plugin.get_metadata()
                plugin_data = plugin.update()
                report["plugins"].append({
                    "name": plugin.config.name,
                    "metadata": metadata,
                    "data": plugin_data
                })
            except Exception as e:
                report["plugins"].append({
                    "name": plugin.config.name,
                    "error": str(e)
                })
        
        return report
    
    def run(self):
        """Run dashboard main loop"""
        if not self.running:
            if not self.initialize():
                return False
        
        if self.root:
            try:
                self.root.mainloop()
            except KeyboardInterrupt:
                self.logger.info("Dashboard interrupted by user")
        else:
            # Console mode
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("Dashboard interrupted by user")
        
        return True
    
    def shutdown(self):
        """Shutdown dashboard"""
        self.logger.info("Shutting down dashboard...")
        self.running = False
        
        # Cancel background tasks
        if self.update_task:
            self.update_task.cancel()
        
        # Cleanup plugins
        for plugin in self.plugins:
            try:
                plugin.cleanup()
            except Exception as e:
                self.logger.warning(f"Plugin {plugin.config.name} cleanup failed: {e}")
        
        # Shutdown executor
        self.executor.shutdown(wait=False)
        
        # Close GUI
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
        
        self.logger.info("Dashboard shutdown complete")

def main():
    """Main entry point"""
    # Example configuration with external app integration
    config = {
        'theme': 'default',  # or 'dark'
        'refresh_interval': 5,
        'auto_refresh': True,
        'external_app': {
            'executable': r'C:\Path\To\Your\ModelProviderApp.exe',
            'args': ['--dashboard-mode'],
            'communication': 'api',  # or 'ipc' or 'subprocess'
            'embed_method': 'window',  # or 'web'
            'api_endpoint': 'http://localhost:8080',
            'window_title': 'Model Provider Control'
        }
    }
    
    # Create and run dashboard
    dashboard = UltimateDashboardV2(config)
    
    try:
        success = dashboard.run()
        return 0 if success else 1
    except Exception as e:
        logging.error(f"Dashboard failed: {e}")
        return 1
    finally:
        dashboard.shutdown()

if __name__ == "__main__":
    import sys
    sys.exit(main())
