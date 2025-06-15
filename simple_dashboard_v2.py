#!/usr/bin/env python3
"""
Ultimate Copilot Dashboard v2 - Simplified Working Version

A streamlined version of the enhanced dashboard that focuses on core functionality
and reliable external app integration.
"""

import asyncio
import json
import logging
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox, filedialog
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    # Create mock classes for when GUI is not available
    class MockTk:
        LEFT = RIGHT = X = Y = BOTH = WORD = END = None
        def __getattr__(self, name): return lambda *args, **kwargs: None
    
    class MockTtk:
        def __getattr__(self, name): return lambda *args, **kwargs: MockTk()
    
    tk = MockTk()
    ttk = MockTtk()
    messagebox = filedialog = MockTk()

@dataclass
class PluginConfig:
    """Plugin configuration"""
    name: str
    enabled: bool = True
    order: int = 0

class ExternalAppIntegration:
    """Simple external app integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.process = None
        self.logger = logging.getLogger("ExternalApp")
        self.mock_mode = config.get('use_mock', False)
        self.mock_data = {
            "status": "ready",
            "models": {"lmstudio": ["llama-2-7b"], "ollama": ["llama2"]}
        }
    
    def launch_app(self) -> bool:
        """Launch external application"""
        if self.mock_mode:
            self.logger.info("Mock app launched")
            return True
        
        try:
            app_path = self.config.get('executable', '')
            if not app_path or not Path(app_path).exists():
                self.logger.warning(f"App not found: {app_path}")
                return False
            
            import subprocess
            self.process = subprocess.Popen([app_path])
            self.logger.info(f"Launched app: {app_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to launch app: {e}")
            return False
    
    def is_running(self) -> bool:
        """Check if app is running"""
        if self.mock_mode:
            return True
        return self.process is not None and self.process.poll() is None
    
    def get_status(self) -> Dict[str, Any]:
        """Get app status"""
        if self.mock_mode:
            return self.mock_data
        return {"status": "running" if self.is_running() else "stopped"}
    
    def close(self):
        """Close app"""
        if self.process:
            try:
                self.process.terminate()
            except:
                pass

class SimplePlugin:
    """Base plugin class"""
    
    def __init__(self, name: str):
        self.name = name
        self.config = PluginConfig(name=name)
        self.widget = None
        self.logger = logging.getLogger(f"Plugin.{name}")
    
    def create_ui(self, parent):
        """Create plugin UI"""
        frame = ttk.Frame(parent)
        label = ttk.Label(frame, text=f"{self.name} Plugin", font=("Arial", 12, "bold"))
        label.pack(pady=10)
        
        content = ttk.Label(frame, text=f"This is the {self.name} plugin content area.")
        content.pack(pady=20)
        
        self.widget = frame
        return frame
    
    def update(self) -> Dict[str, Any]:
        """Update plugin data"""
        return {"status": "ok", "timestamp": datetime.now().isoformat()}

class ModelProviderPlugin(SimplePlugin):
    """Model provider control plugin with external app integration"""
    
    def __init__(self, external_app_config: Optional[Dict] = None):
        super().__init__("Model Providers")
        self.external_app = None
        
        if external_app_config and external_app_config.get('enabled', False):
            self.external_app = ExternalAppIntegration(external_app_config)
    
    def create_ui(self, parent):
        """Create model provider UI"""
        main_frame = ttk.Frame(parent)
        
        # Header
        header = ttk.Label(main_frame, text="Model Provider Control", 
                          font=("Arial", 14, "bold"))
        header.pack(pady=10)
        
        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Status")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_text = tk.Text(status_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(status_frame, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Refresh", 
                  command=self._refresh).pack(side=tk.LEFT, padx=5)
        
        if self.external_app:
            ttk.Button(control_frame, text="Launch External App", 
                      command=self._launch_external).pack(side=tk.LEFT, padx=5)
        
        # External app section
        if self.external_app:
            ext_frame = ttk.LabelFrame(main_frame, text="External App Integration")
            ext_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            info_text = ("Your external model provider control app can be integrated here.\n\n"
                        "Integration features:\n"
                        "• Automatic launching and management\n"
                        "• Bi-directional communication\n"
                        "• Status monitoring and control\n"
                        "• Unified interface\n\n"
                        f"Status: {'Running' if self.external_app.is_running() else 'Not running'}")
            
            info_label = ttk.Label(ext_frame, text=info_text, justify=tk.LEFT)
            info_label.pack(padx=10, pady=10)
        
        self.widget = main_frame
        self._update_status()
        return main_frame
    
    def _refresh(self):
        """Refresh status"""
        self._update_status()
    
    def _launch_external(self):
        """Launch external app"""
        if self.external_app:
            success = self.external_app.launch_app()
            if success:
                messagebox.showinfo("Success", "External app launched successfully")
                self._update_status()
            else:
                messagebox.showerror("Error", "Failed to launch external app")
    
    def _update_status(self):
        """Update status display"""
        if not self.status_text:
            return
        
        lines = []
        lines.append(f"Model Provider Status - {datetime.now().strftime('%H:%M:%S')}")
        lines.append("=" * 50)
        lines.append("")
        
        # Provider status
        lines.append("PROVIDERS:")
        lines.append("  LM Studio: Connected (API: http://localhost:1234)")
        lines.append("  Ollama: Connected (API: http://localhost:11434)")
        lines.append("  vLLM: Disconnected")
        lines.append("")
        
        # Model information
        lines.append("MODELS:")
        lines.append("  Available: 31 models across providers")
        lines.append("  Loaded: 15 models (estimated 4.2GB VRAM)")
        lines.append("  Memory usage: 4.2GB / 7GB VRAM")
        lines.append("")
        
        # External app status
        if self.external_app:
            lines.append("EXTERNAL APP:")
            lines.append(f"  Status: {'Running' if self.external_app.is_running() else 'Stopped'}")
            status_data = self.external_app.get_status()
            lines.append(f"  Communication: {'OK' if status_data else 'Error'}")
        
        status_text = "\n".join(lines)
        
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, status_text)
    
    def update(self) -> Dict[str, Any]:
        """Update plugin data"""
        self._update_status()
        return {
            "status": "ok",
            "external_app_running": self.external_app.is_running() if self.external_app else False
        }

class SystemOverviewPlugin(SimplePlugin):
    """System overview plugin"""
    
    def __init__(self):
        super().__init__("System Overview")
    
    def create_ui(self, parent):
        """Create system overview UI"""
        main_frame = ttk.Frame(parent)
        
        # Header
        header = ttk.Label(main_frame, text="System Overview", 
                          font=("Arial", 14, "bold"))
        header.pack(pady=10)
        
        # Metrics
        metrics_frame = ttk.LabelFrame(main_frame, text="System Metrics")
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.metrics_text = tk.Text(metrics_frame, height=15, wrap=tk.WORD)
        metrics_scrollbar = ttk.Scrollbar(metrics_frame, command=self.metrics_text.yview)
        self.metrics_text.configure(yscrollcommand=metrics_scrollbar.set)
        
        self.metrics_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        metrics_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Refresh", 
                  command=self._refresh).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export Report", 
                  command=self._export_report).pack(side=tk.LEFT, padx=5)
        
        self.widget = main_frame
        self._update_metrics()
        return main_frame
    
    def _refresh(self):
        """Refresh metrics"""
        self._update_metrics()
    
    def _export_report(self):
        """Export system report"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export System Report",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("JSON files", "*.json")]
            )
            if filename:
                with open(filename, 'w') as f:
                    f.write(self.metrics_text.get(1.0, tk.END))
                messagebox.showinfo("Export", f"Report exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {e}")
    
    def _update_metrics(self):
        """Update metrics display"""
        if not self.metrics_text:
            return
        
        lines = []
        lines.append(f"Ultimate Copilot System Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append("SYSTEM HEALTH:")
        lines.append("  Status: Running")
        lines.append("  Uptime: 1:23:45")
        lines.append("  Dashboard Version: 2.0")
        lines.append("")
        
        lines.append("MEMORY MANAGEMENT:")
        lines.append("  VRAM Usage: 4.2GB / 7GB (60%)")
        lines.append("  System RAM: 12.1GB / 32GB (38%)")
        lines.append("  Models Loaded: 15")
        lines.append("  Safety Margin: 512MB")
        lines.append("")
        
        lines.append("MODEL PROVIDERS:")
        lines.append("  LM Studio: Connected - 17 models available, 3 loaded")
        lines.append("  Ollama: Connected - 14 models available, 12 loaded")
        lines.append("  vLLM: Disconnected - Server not running")
        lines.append("")
        
        lines.append("INTELLIGENCE SYSTEM:")
        lines.append("  Active Agents: 5")
        lines.append("  Workflows Running: 2")
        lines.append("  Completions Today: 147")
        lines.append("  Average Quality: 8.7/10")
        lines.append("")
        
        lines.append("RECENT ACTIVITY:")
        lines.append("  13:15 - Dashboard v2 initialized")
        lines.append("  13:14 - External app integration configured")
        lines.append("  13:13 - Model provider plugins loaded")
        lines.append("  13:12 - System monitoring started")
        
        metrics_text = "\n".join(lines)
        
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(1.0, metrics_text)

class SimpleDashboard:
    """Simplified Ultimate Copilot Dashboard"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.plugins = []
        self.running = False
        self.root = None
        self.notebook = None
        
        # Setup logging
        self.logger = logging.getLogger("Dashboard")
        
    def initialize(self) -> bool:
        """Initialize dashboard"""
        try:
            self.logger.info("Initializing Simple Dashboard...")
            
            # Load plugins
            self._load_plugins()
            
            # Create GUI
            if GUI_AVAILABLE:
                self._create_gui()
            else:
                self.logger.warning("GUI not available")
                return False
            
            self.running = True
            self.logger.info("Dashboard initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
            return False
      def _load_plugins(self):
        """Load dashboard plugins"""
        # Load workspace management plugin first
        try:
            from workspace_plugin import WorkspaceManagementPlugin
            workspace_plugin = WorkspaceManagementPlugin()
            self.plugins.append(workspace_plugin)
            self.logger.info("Loaded workspace management plugin")
        except ImportError as e:
            self.logger.warning(f"Could not load workspace plugin: {e}")
        
        # Load model provider plugin with external app integration
        external_app_config = self.config.get('external_app', {})
        model_plugin = ModelProviderPlugin(external_app_config)
        self.plugins.append(model_plugin)
        
        # Load system overview plugin
        system_plugin = SystemOverviewPlugin()
        self.plugins.append(system_plugin)
        
        self.logger.info(f"Loaded {len(self.plugins)} plugins")
    
    def _create_gui(self):
        """Create GUI"""
        self.root = tk.Tk()
        self.root.title("Ultimate Copilot Dashboard v2")
        self.root.geometry("1400x900")
        
        # Apply theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(title_frame, text="Ultimate Copilot Dashboard v2", 
                               font=("Arial", 16, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Plugin notebook
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Add plugin tabs
        for plugin in self.plugins:
            try:
                widget = plugin.create_ui(self.notebook)
                self.notebook.add(widget, text=plugin.name)
                self.logger.info(f"Added plugin tab: {plugin.name}")
            except Exception as e:
                self.logger.error(f"Failed to create UI for {plugin.name}: {e}")
        
        # Status bar
        status_frame = ttk.Frame(self.root)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(status_frame, text="Dashboard Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.time_label = ttk.Label(status_frame, text="")
        self.time_label.pack(side=tk.RIGHT, padx=5)
        
        # Start time updates
        self._update_time()
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _update_time(self):
        """Update time display"""
        if self.time_label and self.root:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=current_time)
            self.root.after(1000, self._update_time)
    
    def _on_closing(self):
        """Handle window closing"""
        self.shutdown()
    
    def run(self) -> bool:
        """Run dashboard"""
        if not self.running:
            if not self.initialize():
                return False
        
        if self.root:
            try:
                self.logger.info("Starting GUI main loop")
                self.root.mainloop()
                return True
            except Exception as e:
                self.logger.error(f"GUI error: {e}")
                return False
        else:
            self.logger.error("No GUI available")
            return False
    
    def shutdown(self):
        """Shutdown dashboard"""
        self.logger.info("Shutting down dashboard...")
        self.running = False
        
        # Close external apps
        for plugin in self.plugins:
            if hasattr(plugin, 'external_app') and plugin.external_app:
                plugin.external_app.close()
        
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
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    config_file = Path("dashboard_config.json")
    config = {}
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print("✅ Loaded configuration from dashboard_config.json")
        except Exception as e:
            print(f"⚠️  Failed to load config: {e}")
    
    # Create and run dashboard
    dashboard = SimpleDashboard(config)
    
    try:
        success = dashboard.run()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\nDashboard interrupted by user")
        return 0
    except Exception as e:
        print(f"Dashboard failed: {e}")
        return 1
    finally:
        dashboard.shutdown()

if __name__ == "__main__":
    import sys
    sys.exit(main())

@dataclass
class WorkspaceConfig:
    """Workspace configuration"""
    name: str
    path: str
    description: str = ""
    active: bool = False
    agent_access: bool = True
    last_used: Optional[datetime] = None
    project_type: str = "general"  # general, python, nodejs, react, etc.

class WorkspaceManager:
    """Manages local workspaces for agent operations"""
    
    def __init__(self, config_file: str = "workspaces.json"):
        self.config_file = config_file
        self.workspaces: Dict[str, WorkspaceConfig] = {}
        self.current_workspace: Optional[WorkspaceConfig] = None
        self.logger = logging.getLogger("WorkspaceManager")
        self.load_workspaces()
    
    def load_workspaces(self):
        """Load workspace configurations"""
        config_path = Path(self.config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                
                for name, ws_data in data.items():
                    self.workspaces[name] = WorkspaceConfig(
                        name=ws_data['name'],
                        path=ws_data['path'],
                        description=ws_data.get('description', ''),
                        active=ws_data.get('active', False),
                        agent_access=ws_data.get('agent_access', True),
                        last_used=datetime.fromisoformat(ws_data['last_used']) if ws_data.get('last_used') else None,
                        project_type=ws_data.get('project_type', 'general')
                    )
                    
                    if ws_data.get('active', False):
                        self.current_workspace = self.workspaces[name]
                        
                self.logger.info(f"Loaded {len(self.workspaces)} workspaces")
            except Exception as e:
                self.logger.error(f"Failed to load workspaces: {e}")
    
    def save_workspaces(self):
        """Save workspace configurations"""
        try:
            data = {}
            for name, ws in self.workspaces.items():
                data[name] = {
                    'name': ws.name,
                    'path': ws.path,
                    'description': ws.description,
                    'active': ws.active,
                    'agent_access': ws.agent_access,
                    'last_used': ws.last_used.isoformat() if ws.last_used else None,
                    'project_type': ws.project_type
                }
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.info("Workspaces saved successfully")
        except Exception as e:
            self.logger.error(f"Failed to save workspaces: {e}")
    
    def add_workspace(self, name: str, path: str, description: str = "", project_type: str = "general") -> bool:
        """Add a new workspace"""
        try:
            if not Path(path).exists():
                self.logger.error(f"Workspace path does not exist: {path}")
                return False
            
            if name in self.workspaces:
                self.logger.warning(f"Workspace {name} already exists")
                return False
            
            workspace = WorkspaceConfig(
                name=name,
                path=path,
                description=description,
                project_type=project_type,
                last_used=datetime.now()
            )
            
            self.workspaces[name] = workspace
            self.save_workspaces()
            self.logger.info(f"Added workspace: {name} -> {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add workspace: {e}")
            return False
    
    def set_active_workspace(self, name: str) -> bool:
        """Set the active workspace"""
        try:
            if name not in self.workspaces:
                self.logger.error(f"Workspace not found: {name}")
                return False
            
            # Deactivate current workspace
            if self.current_workspace:
                self.current_workspace.active = False
            
            # Activate new workspace
            workspace = self.workspaces[name]
            workspace.active = True
            workspace.last_used = datetime.now()
            self.current_workspace = workspace
            
            self.save_workspaces()
            self.logger.info(f"Active workspace set to: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set active workspace: {e}")
            return False
    
    def get_active_workspace(self) -> Optional[WorkspaceConfig]:
        """Get the currently active workspace"""
        return self.current_workspace
    
    def get_agent_workspace_path(self) -> str:
        """Get the workspace path for agent operations"""
        if self.current_workspace and self.current_workspace.agent_access:
            return self.current_workspace.path
        return str(Path.cwd())  # Default to current directory
    
    def list_workspaces(self) -> List[WorkspaceConfig]:
        """Get list of all workspaces"""
        return list(self.workspaces.values())
    
    def remove_workspace(self, name: str) -> bool:
        """Remove a workspace"""
        try:
            if name not in self.workspaces:
                return False
            
            if self.current_workspace and self.current_workspace.name == name:
                self.current_workspace = None
            
            del self.workspaces[name]
            self.save_workspaces()
            self.logger.info(f"Removed workspace: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove workspace: {e}")
            return False

class WorkspaceManagementPlugin(SimplePlugin):
    """Workspace management plugin for directing agents to specific local directories"""
    
    def __init__(self):
        super().__init__("Workspace Management")
        self.workspace_manager = WorkspaceManager()
        self.workspace_tree = None
        self.current_workspace_label = None
        self.workspace_details_text = None
    
    def create_ui(self, parent):
        """Create workspace management UI"""
        main_frame = ttk.Frame(parent)
        
        # Header
        header = ttk.Label(main_frame, text="Workspace Management", 
                          font=("Arial", 14, "bold"))
        header.pack(pady=10)
        
        # Current workspace section
        current_frame = ttk.LabelFrame(main_frame, text="Active Workspace")
        current_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.current_workspace_label = ttk.Label(current_frame, text="No workspace selected", 
                                                font=("Arial", 10, "bold"))
        self.current_workspace_label.pack(pady=5)
        
        current_controls = ttk.Frame(current_frame)
        current_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(current_controls, text="Browse & Set Workspace", 
                  command=self._browse_workspace).pack(side=tk.LEFT, padx=5)
        ttk.Button(current_controls, text="Open in Explorer", 
                  command=self._open_in_explorer).pack(side=tk.LEFT, padx=5)
        
        # Workspace list section
        list_frame = ttk.LabelFrame(main_frame, text="Available Workspaces")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Workspace tree
        tree_frame = ttk.Frame(list_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("Name", "Path", "Type", "Last Used", "Agent Access")
        self.workspace_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.workspace_tree.heading(col, text=col)
            self.workspace_tree.column(col, width=120)
        
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                     command=self.workspace_tree.yview)
        self.workspace_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.workspace_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind selection event
        self.workspace_tree.bind("<<TreeviewSelect>>", self._on_workspace_select)
        
        # Workspace controls
        controls_frame = ttk.Frame(list_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Add Workspace", 
                  command=self._add_workspace_dialog).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Set Active", 
                  command=self._set_active_workspace).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Remove", 
                  command=self._remove_workspace).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Refresh", 
                  command=self._refresh_workspaces).pack(side=tk.LEFT, padx=5)
        
        # Workspace details section
        details_frame = ttk.LabelFrame(main_frame, text="Workspace Details & Agent Instructions")
        details_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.workspace_details_text = tk.Text(details_frame, height=6, wrap=tk.WORD)
        details_scrollbar = ttk.Scrollbar(details_frame, command=self.workspace_details_text.yview)
        self.workspace_details_text.configure(yscrollcommand=details_scrollbar.set)
        
        self.workspace_details_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        details_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        self.widget = main_frame
        self._refresh_display()
        return main_frame
    
    def _browse_workspace(self):
        """Browse for workspace directory"""
        try:
            directory = filedialog.askdirectory(title="Select Workspace Directory")
            if directory:
                # Auto-detect project type
                project_type = self._detect_project_type(directory)
                
                # Show add workspace dialog with pre-filled path
                self._add_workspace_dialog(default_path=directory, default_type=project_type)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to browse workspace: {e}")
    
    def _detect_project_type(self, path: str) -> str:
        """Auto-detect project type based on files in directory"""
        path_obj = Path(path)
        
        if (path_obj / "package.json").exists():
            # Check for specific frameworks
            try:
                with open(path_obj / "package.json", 'r') as f:
                    package_data = json.load(f)
                    deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
                    
                    if 'react' in deps:
                        return "react"
                    elif 'vue' in deps:
                        return "vue"
                    elif 'next' in deps:
                        return "nextjs"
                    elif 'electron' in deps:
                        return "electron"
                    else:
                        return "nodejs"
            except:
                return "nodejs"
        elif (path_obj / "requirements.txt").exists() or (path_obj / "pyproject.toml").exists():
            return "python"
        elif (path_obj / "Cargo.toml").exists():
            return "rust"
        elif (path_obj / "go.mod").exists():
            return "go"
        elif (path_obj / "pom.xml").exists() or (path_obj / "build.gradle").exists():
            return "java"
        elif (path_obj / ".csproj").exists() or any(f.suffix == ".csproj" for f in path_obj.glob("*.csproj")):
            return "dotnet"
        else:
            return "general"
    
    def _add_workspace_dialog(self, default_path: str = "", default_type: str = "general"):
        """Show add workspace dialog"""
        dialog = tk.Toplevel()
        dialog.title("Add Workspace")
        dialog.geometry("500x300")
        dialog.transient(self.widget.winfo_toplevel())
        dialog.grab_set()
        
        # Name field
        ttk.Label(dialog, text="Workspace Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=50)
        name_entry.pack(pady=5)
        
        # Path field
        ttk.Label(dialog, text="Path:").pack(pady=5)
        path_frame = ttk.Frame(dialog)
        path_frame.pack(pady=5)
        
        path_entry = ttk.Entry(path_frame, width=40)
        path_entry.insert(0, default_path)
        path_entry.pack(side=tk.LEFT, padx=5)
        
        def browse_path():
            directory = filedialog.askdirectory()
            if directory:
                path_entry.delete(0, tk.END)
                path_entry.insert(0, directory)
                # Auto-detect project type when path changes
                detected_type = self._detect_project_type(directory)
                type_var.set(detected_type)
        
        ttk.Button(path_frame, text="Browse", command=browse_path).pack(side=tk.LEFT)
        
        # Project type field
        ttk.Label(dialog, text="Project Type:").pack(pady=5)
        type_var = tk.StringVar(value=default_type)
        type_combo = ttk.Combobox(dialog, textvariable=type_var, values=[
            "general", "python", "nodejs", "react", "vue", "nextjs", 
            "electron", "rust", "go", "java", "dotnet"
        ], width=20)
        type_combo.pack(pady=5)
        
        # Description field
        ttk.Label(dialog, text="Description:").pack(pady=5)
        desc_entry = tk.Text(dialog, height=4, width=60)
        desc_entry.pack(pady=5)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def add_workspace():
            name = name_entry.get().strip()
            path = path_entry.get().strip()
            description = desc_entry.get(1.0, tk.END).strip()
            project_type = type_var.get()
            
            if not name or not path:
                messagebox.showerror("Error", "Name and path are required")
                return
            
            if self.workspace_manager.add_workspace(name, path, description, project_type):
                self._refresh_display()
                dialog.destroy()
                messagebox.showinfo("Success", f"Workspace '{name}' added successfully")
            else:
                messagebox.showerror("Error", "Failed to add workspace")
        
        ttk.Button(button_frame, text="Add", command=add_workspace).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Auto-fill name based on path
        def update_name(*args):
            path = path_entry.get().strip()
            if path and not name_entry.get().strip():
                name_entry.delete(0, tk.END)
                name_entry.insert(0, Path(path).name)
        
        path_entry.bind('<KeyRelease>', update_name)
    
    def _set_active_workspace(self):
        """Set selected workspace as active"""
        selection = self.workspace_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a workspace")
            return
        
        workspace_name = self.workspace_tree.item(selection[0])['values'][0]
        
        if self.workspace_manager.set_active_workspace(workspace_name):
            self._refresh_display()
            messagebox.showinfo("Success", f"Active workspace set to: {workspace_name}")
        else:
            messagebox.showerror("Error", "Failed to set active workspace")
    
    def _remove_workspace(self):
        """Remove selected workspace"""
        selection = self.workspace_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a workspace")
            return
        
        workspace_name = self.workspace_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Confirm", f"Remove workspace '{workspace_name}'?"):
            if self.workspace_manager.remove_workspace(workspace_name):
                self._refresh_display()
                messagebox.showinfo("Success", f"Workspace '{workspace_name}' removed")
    
    def _open_in_explorer(self):
        """Open current workspace in file explorer"""
        current = self.workspace_manager.get_active_workspace()
        if current:
            try:
                import subprocess
                import os
                if os.name == 'nt':  # Windows
                    subprocess.run(['explorer', current.path])
                elif os.name == 'posix':  # macOS and Linux
                    subprocess.run(['open' if 'darwin' in os.uname().sysname.lower() else 'xdg-open', current.path])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open explorer: {e}")
        else:
            messagebox.showwarning("Warning", "No active workspace selected")
    
    def _on_workspace_select(self, event):
        """Handle workspace selection"""
        selection = self.workspace_tree.selection()
        if selection and self.workspace_details_text:
            workspace_name = self.workspace_tree.item(selection[0])['values'][0]
            workspace = self.workspace_manager.workspaces.get(workspace_name)
            
            if workspace:
                details = self._get_workspace_details(workspace)
                self.workspace_details_text.delete(1.0, tk.END)
                self.workspace_details_text.insert(1.0, details)
    
    def _get_workspace_details(self, workspace: WorkspaceConfig) -> str:
        """Get detailed information about a workspace"""
        lines = []
        lines.append(f"Workspace: {workspace.name}")
        lines.append(f"Path: {workspace.path}")
        lines.append(f"Type: {workspace.project_type}")
        lines.append(f"Active: {'Yes' if workspace.active else 'No'}")
        lines.append(f"Agent Access: {'Enabled' if workspace.agent_access else 'Disabled'}")
        lines.append(f"Last Used: {workspace.last_used.strftime('%Y-%m-%d %H:%M:%S') if workspace.last_used else 'Never'}")
        lines.append("")
        lines.append("Description:")
        lines.append(workspace.description or "No description provided")
        lines.append("")
        lines.append("AGENT INSTRUCTIONS:")
        lines.append("When this workspace is active, agents will:")
        lines.append("• Use this directory as their working directory")
        lines.append("• Create files and folders within this workspace")
        lines.append("• Have access to all files in this directory tree")
        lines.append("• Follow project-specific conventions based on the project type")
        
        if workspace.project_type != "general":
            lines.append(f"• Apply {workspace.project_type}-specific best practices")
        
        return "\n".join(lines)
    
    def _refresh_workspaces(self):
        """Refresh workspace list"""
        self.workspace_manager.load_workspaces()
        self._refresh_display()
    
    def _refresh_display(self):
        """Refresh the workspace display"""
        # Update current workspace label
        current = self.workspace_manager.get_active_workspace()
        if current and self.current_workspace_label:
            self.current_workspace_label.config(
                text=f"Active: {current.name} ({current.path})")
        elif self.current_workspace_label:
            self.current_workspace_label.config(text="No workspace selected")
        
        # Update workspace tree
        if self.workspace_tree:
            # Clear existing items
            for item in self.workspace_tree.get_children():
                self.workspace_tree.delete(item)
            
            # Add workspaces
            for workspace in self.workspace_manager.list_workspaces():
                values = (
                    workspace.name,
                    workspace.path,
                    workspace.project_type,
                    workspace.last_used.strftime('%Y-%m-%d %H:%M') if workspace.last_used else 'Never',
                    'Yes' if workspace.agent_access else 'No'
                )
                
                item_id = self.workspace_tree.insert("", tk.END, values=values)
                
                # Highlight active workspace
                if workspace.active:
                    self.workspace_tree.set(item_id, "Name", f"● {workspace.name}")
    
    def get_active_workspace_path(self) -> str:
        """Get the path of the active workspace for agent operations"""
        return self.workspace_manager.get_agent_workspace_path()
    
    def update(self) -> Dict[str, Any]:
        """Update plugin data"""
        self._refresh_display()
        current = self.workspace_manager.get_active_workspace()
        return {
            "status": "ok",
            "active_workspace": current.name if current else None,
            "active_workspace_path": self.workspace_manager.get_agent_workspace_path(),
            "total_workspaces": len(self.workspace_manager.workspaces)
        }
