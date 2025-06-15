#!/usr/bin/env python3
"""
Enhanced Ultimate Copilot Dashboard

A modern, modular dashboard system with plugin architecture for easy integration
of external tools like model provider control applications.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import json
import threading
from pathlib import Path
import time
from abc import ABC, abstractmethod

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox
    import tkinter.font as tkFont
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False

@dataclass
class DashboardMetric:
    """Dashboard metric data structure"""
    name: str
    value: Any
    unit: str = ""
    status: str = "normal"  # normal, warning, critical
    trend: str = "stable"   # up, down, stable
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class DashboardAlert:
    """Dashboard alert/notification"""
    id: str
    severity: str  # info, warning, error, critical
    title: str
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False

class DashboardPlugin(ABC):
    """Abstract base class for dashboard plugins"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Get plugin name for tab display"""
        pass
    
    @abstractmethod
    def create_widget(self, parent) -> tk.Widget:
        """Create the plugin's widget for the tab"""
        pass
    
    @abstractmethod
    async def update_data(self) -> Dict[str, Any]:
        """Update plugin data"""
        pass
    
    def on_activate(self):
        """Called when plugin tab is activated"""
        pass
    
    def on_deactivate(self):
        """Called when plugin tab is deactivated"""
        pass

class ModelProviderControlPlugin(DashboardPlugin):
    """Plugin placeholder for external model provider control app"""
    
    def __init__(self, external_app_integration: Optional[Callable] = None):
        self.external_app_integration = external_app_integration
        self.widget = None
    
    def get_name(self) -> str:
        return "Model Providers"
    
    def create_widget(self, parent) -> tk.Widget:
        """Create widget for model provider control"""
        frame = ttk.Frame(parent)
        
        if self.external_app_integration:
            # Integration point for your external app
            info_label = ttk.Label(frame, text="External Model Provider Control App Integration")
            info_label.pack(pady=20)
            
            # Button to launch/embed external app
            launch_btn = ttk.Button(frame, text="Launch Model Provider Control", 
                                  command=self._launch_external_app)
            launch_btn.pack(pady=10)
            
            # Placeholder for embedded control
            control_frame = ttk.LabelFrame(frame, text="Model Provider Controls")
            control_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # This is where your app would be embedded
            embed_label = ttk.Label(control_frame, 
                                  text="Your model provider control app will be embedded here.\n"
                                       "Integration points:\n"
                                       "- Model loading/unloading controls\n"
                                       "- Provider status monitoring\n"
                                       "- Configuration management\n"
                                       "- Performance metrics")
            embed_label.pack(expand=True)
        else:
            # Fallback interface
            self._create_fallback_interface(frame)
        
        self.widget = frame
        return frame
    
    def _create_fallback_interface(self, parent):
        """Create fallback interface when external app not available"""
        title_label = ttk.Label(parent, text="Model Provider Control", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(10, 20))
        
        # Provider status section
        status_frame = ttk.LabelFrame(parent, text="Provider Status")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        providers = ["LM Studio", "Ollama", "vLLM"]
        for provider in providers:
            row_frame = ttk.Frame(status_frame)
            row_frame.pack(fill=tk.X, padx=5, pady=2)
            
            ttk.Label(row_frame, text=f"{provider}:").pack(side=tk.LEFT)
            status_label = ttk.Label(row_frame, text="●", foreground="green")
            status_label.pack(side=tk.LEFT, padx=(5, 0))
            ttk.Label(row_frame, text="Connected").pack(side=tk.LEFT, padx=(5, 0))
        
        # Quick actions
        actions_frame = ttk.LabelFrame(parent, text="Quick Actions")
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        btn_frame = ttk.Frame(actions_frame)
        btn_frame.pack(pady=5)
        
        ttk.Button(btn_frame, text="Refresh All").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Load Model").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Settings").pack(side=tk.LEFT, padx=5)
        
        # Integration note
        note_frame = ttk.LabelFrame(parent, text="Integration Ready")
        note_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        note_text = ("This tab is ready for integration with your model provider control app.\n\n"
                    "Integration features:\n"
                    "• Seamless embedding of your control interface\n"
                    "• Bi-directional data sharing with dashboard\n"
                    "• Unified theming and styling\n"
                    "• Event handling and notifications\n\n"
                    "Your app can be embedded here using the external_app_integration parameter.")
        
        note_label = ttk.Label(note_frame, text=note_text, justify=tk.LEFT)
        note_label.pack(padx=10, pady=10)
    
    def _launch_external_app(self):
        """Launch or focus external model provider app"""
        if self.external_app_integration:
            try:
                self.external_app_integration()
            except Exception as e:
                messagebox.showerror("Integration Error", f"Failed to launch external app: {e}")
        else:
            messagebox.showinfo("Integration", "External app integration not configured")
    
    async def update_data(self) -> Dict[str, Any]:
        """Update model provider data"""
        # This would interface with your external app to get current status
        return {
            "providers": {
                "lmstudio": {"status": "connected", "models": 17, "loaded": 3},
                "ollama": {"status": "connected", "models": 14, "loaded": 12},
                "vllm": {"status": "disconnected", "models": 0, "loaded": 0}
            },
            "total_models": 31,
            "active_models": 15,
            "memory_usage": "4.2GB / 7GB"
        }

class SystemOverviewPlugin(DashboardPlugin):
    """System overview and health monitoring plugin"""
    
    def __init__(self, dashboard_controller):
        self.controller = dashboard_controller
        self.metrics_tree = None
        self.status_text = None
    
    def get_name(self) -> str:
        return "System Overview"
    
    def create_widget(self, parent) -> tk.Widget:
        frame = ttk.Frame(parent)
        
        # System status section
        status_frame = ttk.LabelFrame(frame, text="System Health")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=8, 
                                                    font=("Consolas", 10))
        self.status_text.pack(fill=tk.X, padx=5, pady=5)
        
        # Real-time metrics
        metrics_frame = ttk.LabelFrame(frame, text="Live Metrics")
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Metrics tree
        columns = ("Metric", "Value", "Status", "Trend")
        self.metrics_tree = ttk.Treeview(metrics_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            self.metrics_tree.heading(col, text=col)
            self.metrics_tree.column(col, width=120)
        
        # Scrollbar for metrics
        metrics_scrollbar = ttk.Scrollbar(metrics_frame, orient=tk.VERTICAL, 
                                        command=self.metrics_tree.yview)
        self.metrics_tree.configure(yscrollcommand=metrics_scrollbar.set)
        
        self.metrics_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        metrics_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(frame)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Refresh", 
                  command=self._refresh_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Export Report", 
                  command=self._export_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Clear Alerts", 
                  command=self._clear_alerts).pack(side=tk.LEFT, padx=5)
        
        return frame
    
    def _refresh_data(self):
        """Manually refresh system data"""
        asyncio.create_task(self.controller.update_all_data())
    
    def _export_report(self):
        """Export system report"""
        asyncio.create_task(self.controller.export_system_report())
    
    def _clear_alerts(self):
        """Clear all alerts"""
        self.controller.clear_alerts()
    
    async def update_data(self) -> Dict[str, Any]:
        """Update system overview data"""
        try:
            # Get data from dashboard controller
            system_data = await self.controller.get_system_status()
            
            # Update status text
            if self.status_text:
                self.status_text.delete(1.0, tk.END)
                status_summary = self._format_system_status(system_data)
                self.status_text.insert(1.0, status_summary)
            
            # Update metrics tree
            if self.metrics_tree:
                self._update_metrics_display(system_data)
            
            return system_data
            
        except Exception as e:
            return {"error": str(e)}
    
    def _format_system_status(self, data: Dict) -> str:
        """Format system status for display"""
        lines = []
        lines.append(f"System Status: {data.get('status', 'Unknown')}")
        lines.append(f"Uptime: {data.get('uptime_seconds', 0):.0f} seconds")
        lines.append("")
        
        # Memory status
        memory = data.get('memory', {})
        if memory:
            lines.append("MEMORY:")
            lines.append(f"  VRAM: {memory.get('current_usage_mb', 0)}MB / {memory.get('max_vram_mb', 0)}MB")
            lines.append(f"  Models: {len(memory.get('loaded_models', []))} loaded")
        
        # Intelligence status
        intelligence = data.get('intelligence', {})
        if intelligence:
            lines.append("\nINTELLIGENCE:")
            lines.append(f"  Active Allocations: {intelligence.get('active_allocations', 0)}")
            lines.append(f"  Agents: {intelligence.get('total_agents', 0)}")
        
        # Completion status
        completion = data.get('completion', {})
        if completion:
            lines.append("\nCOMPLETION:")
            lines.append(f"  Total: {completion.get('total_completions', 0)}")
            metrics = completion.get('performance_metrics', {})
            if metrics:
                lines.append(f"  Avg Quality: {metrics.get('average_quality', 0):.1f}/10")
        
        return "\n".join(lines)
    
    def _update_metrics_display(self, data: Dict):
        """Update metrics tree display"""
        # Clear existing items
        for item in self.metrics_tree.get_children():
            self.metrics_tree.delete(item)
        
        # Add current metrics
        metrics = self.controller.get_current_metrics()
        for metric in metrics:
            status_color = {
                "normal": "",
                "warning": "orange",
                "critical": "red"
            }.get(metric.status, "")
            
            trend_symbol = {
                "up": "↑",
                "down": "↓", 
                "stable": "→"
            }.get(metric.trend, "→")
            
            item_id = self.metrics_tree.insert("", tk.END, values=(
                metric.name,
                f"{metric.value} {metric.unit}",
                metric.status.upper(),
                trend_symbol
            ))
            
            if status_color:
                self.metrics_tree.set(item_id, "Status", metric.status.upper())

class WorkflowManagerPlugin(DashboardPlugin):
    """Workflow management and execution plugin"""
    
    def __init__(self, dashboard_controller):
        self.controller = dashboard_controller
        self.workflow_tree = None
        self.execution_log = None
    
    def get_name(self) -> str:
        return "Workflows"
    
    def create_widget(self, parent) -> tk.Widget:
        frame = ttk.Frame(parent)
        
        # Workflow controls
        control_frame = ttk.LabelFrame(frame, text="Workflow Controls")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Template selection
        template_frame = ttk.Frame(control_frame)
        template_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(template_frame, text="Template:").pack(side=tk.LEFT)
        self.template_var = tk.StringVar(value="development")
        template_combo = ttk.Combobox(template_frame, textvariable=self.template_var,
                                    values=["development", "research", "analysis", "testing"])
        template_combo.pack(side=tk.LEFT, padx=5)
        
        # Execution buttons
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Start Workflow", 
                  command=self._start_workflow).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Stop Current", 
                  command=self._stop_workflow).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="View Results", 
                  command=self._view_results).pack(side=tk.LEFT, padx=5)
        
        # Active workflows
        workflows_frame = ttk.LabelFrame(frame, text="Active Workflows")
        workflows_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("ID", "Type", "Status", "Progress", "Started")
        self.workflow_tree = ttk.Treeview(workflows_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.workflow_tree.heading(col, text=col)
            self.workflow_tree.column(col, width=100)
        
        workflow_scrollbar = ttk.Scrollbar(workflows_frame, orient=tk.VERTICAL,
                                         command=self.workflow_tree.yview)
        self.workflow_tree.configure(yscrollcommand=workflow_scrollbar.set)
        
        self.workflow_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        workflow_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Execution log
        log_frame = ttk.LabelFrame(frame, text="Execution Log")
        log_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.execution_log = scrolledtext.ScrolledText(log_frame, height=6,
                                                      font=("Consolas", 9))
        self.execution_log.pack(fill=tk.X, padx=5, pady=5)
        
        return frame
    
    def _start_workflow(self):
        """Start a new workflow"""
        template = self.template_var.get()
        asyncio.create_task(self.controller.start_workflow(template))
        self._log_message(f"Starting {template} workflow...")
    
    def _stop_workflow(self):
        """Stop current workflow"""
        asyncio.create_task(self.controller.stop_current_workflow())
        self._log_message("Stopping current workflow...")
    
    def _view_results(self):
        """View workflow results"""
        selected = self.workflow_tree.selection()
        if selected:
            workflow_id = self.workflow_tree.item(selected[0])['values'][0]
            self._show_workflow_results(workflow_id)
    
    def _show_workflow_results(self, workflow_id: str):
        """Show detailed workflow results"""
        results_window = tk.Toplevel()
        results_window.title(f"Workflow Results - {workflow_id}")
        results_window.geometry("800x600")
        
        results_text = scrolledtext.ScrolledText(results_window, font=("Consolas", 10))
        results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Load and display results
        asyncio.create_task(self._load_workflow_results(workflow_id, results_text))
    
    async def _load_workflow_results(self, workflow_id: str, text_widget):
        """Load workflow results asynchronously"""
        try:
            results = await self.controller.get_workflow_results(workflow_id)
            text_widget.insert(tk.END, json.dumps(results, indent=2))
        except Exception as e:
            text_widget.insert(tk.END, f"Error loading results: {e}")
    
    def _log_message(self, message: str):
        """Add message to execution log"""
        if self.execution_log:
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.execution_log.insert(tk.END, f"[{timestamp}] {message}\n")
            self.execution_log.see(tk.END)
    
    async def update_data(self) -> Dict[str, Any]:
        """Update workflow data"""
        workflows = await self.controller.get_active_workflows()
        
        # Update workflow tree
        if self.workflow_tree:
            # Clear existing items
            for item in self.workflow_tree.get_children():
                self.workflow_tree.delete(item)
            
            # Add current workflows
            for workflow in workflows:
                self.workflow_tree.insert("", tk.END, values=(
                    workflow.get('id', 'Unknown'),
                    workflow.get('type', 'Unknown'),
                    workflow.get('status', 'Unknown'),
                    f"{workflow.get('progress', 0)}%",
                    workflow.get('started', 'Unknown')
                ))
        
        return {"workflows": workflows}

class CompletionManagerPlugin(DashboardPlugin):
    """AI completion management plugin"""
    
    def __init__(self, dashboard_controller):
        self.controller = dashboard_controller
        self.completion_tree = None
        self.prompt_entry = None
        self.result_text = None
    
    def get_name(self) -> str:
        return "AI Completions"
    
    def create_widget(self, parent) -> tk.Widget:
        frame = ttk.Frame(parent)
        
        # Quick completion interface
        completion_frame = ttk.LabelFrame(frame, text="Quick Completion")
        completion_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Prompt input
        prompt_frame = ttk.Frame(completion_frame)
        prompt_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(prompt_frame, text="Prompt:").pack(anchor=tk.W)
        self.prompt_entry = tk.Text(prompt_frame, height=3, wrap=tk.WORD)
        self.prompt_entry.pack(fill=tk.X, pady=2)
        
        # Completion options
        options_frame = ttk.Frame(completion_frame)
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(options_frame, text="Type:").pack(side=tk.LEFT)
        self.type_var = tk.StringVar(value="code")
        type_combo = ttk.Combobox(options_frame, textvariable=self.type_var,
                                 values=["code", "documentation", "analysis", "research"],
                                 width=12)
        type_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(options_frame, text="Quality:").pack(side=tk.LEFT, padx=(10, 0))
        self.quality_var = tk.StringVar(value="standard")
        quality_combo = ttk.Combobox(options_frame, textvariable=self.quality_var,
                                    values=["draft", "standard", "high", "premium"],
                                    width=10)
        quality_combo.pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        action_frame = ttk.Frame(completion_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="Generate", 
                  command=self._generate_completion).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Clear", 
                  command=self._clear_completion).pack(side=tk.LEFT, padx=5)
        
        # Result display
        result_frame = ttk.LabelFrame(frame, text="Generated Result")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(result_frame, height=10,
                                                   font=("Consolas", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Recent completions
        recent_frame = ttk.LabelFrame(frame, text="Recent Completions")
        recent_frame.pack(fill=tk.X, padx=10, pady=5)
        
        columns = ("Time", "Type", "Quality", "Status", "Duration")
        self.completion_tree = ttk.Treeview(recent_frame, columns=columns, 
                                          show="headings", height=6)
        
        for col in columns:
            self.completion_tree.heading(col, text=col)
            self.completion_tree.column(col, width=80)
        
        completion_scrollbar = ttk.Scrollbar(recent_frame, orient=tk.VERTICAL,
                                           command=self.completion_tree.yview)
        self.completion_tree.configure(yscrollcommand=completion_scrollbar.set)
        
        self.completion_tree.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        completion_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        
        # Bind double-click to view completion
        self.completion_tree.bind("<Double-1>", self._view_completion_details)
        
        return frame
    
    def _generate_completion(self):
        """Generate AI completion"""
        prompt = self.prompt_entry.get(1.0, tk.END).strip()
        if not prompt:
            messagebox.showwarning("Input Required", "Please enter a prompt")
            return
        
        completion_type = self.type_var.get()
        quality = self.quality_var.get()
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(1.0, "Generating completion...")
        
        asyncio.create_task(self._run_completion(prompt, completion_type, quality))
    
    async def _run_completion(self, prompt: str, completion_type: str, quality: str):
        """Run completion asynchronously"""
        try:
            result = await self.controller.run_completion(prompt, completion_type, quality)
            
            if result.get('success'):
                content = result.get('content', '')
                metadata = f"Quality: {result.get('quality_score', 0):.1f}/10, " \
                          f"Time: {result.get('processing_time', 0):.1f}s, " \
                          f"Model: {result.get('model_used', 'Unknown')}\n\n"
                
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(1.0, metadata + content)
            else:
                error_msg = f"Completion failed: {result.get('error', 'Unknown error')}"
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(1.0, error_msg)
                
        except Exception as e:
            error_msg = f"Error running completion: {e}"
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, error_msg)
    
    def _clear_completion(self):
        """Clear completion interface"""
        self.prompt_entry.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
    
    def _view_completion_details(self, event):
        """View detailed completion information"""
        selected = self.completion_tree.selection()
        if selected:
            # Get completion details and show in popup
            item_values = self.completion_tree.item(selected[0])['values']
            messagebox.showinfo("Completion Details", f"Details for completion at {item_values[0]}")
    
    async def update_data(self) -> Dict[str, Any]:
        """Update completion data"""
        completions = await self.controller.get_recent_completions()
        
        # Update completion tree
        if self.completion_tree:
            # Clear existing items
            for item in self.completion_tree.get_children():
                self.completion_tree.delete(item)
            
            # Add recent completions
            for completion in completions[-10:]:  # Last 10
                self.completion_tree.insert("", tk.END, values=(
                    completion.get('time', 'Unknown'),
                    completion.get('type', 'Unknown'),
                    f"{completion.get('quality', 0):.1f}",
                    completion.get('status', 'Unknown'),
                    f"{completion.get('duration', 0):.1f}s"
                ))
        
        return {"completions": completions}

class EnhancedDashboardController:
    """Enhanced dashboard controller with plugin architecture"""
    
    def __init__(self, external_app_integration: Optional[Callable] = None):
        self.external_app_integration = external_app_integration
        
        # Core components
        self.memory_manager = None
        self.unified_intelligence = None
        self.orchestrator = None
        self.completion_system = None
        
        # Dashboard state
        self.is_initialized = False
        self.current_metrics: List[DashboardMetric] = []
        self.alerts: List[DashboardAlert] = []
        self.plugins: List[DashboardPlugin] = []
        
        # GUI components
        self.root = None
        self.notebook = None
        self.status_bar = None
        
        # Background tasks
        self.update_task = None
        self.auto_refresh = True
        self.refresh_interval = 5
        
        # Setup logging
        self.logger = logging.getLogger("DashboardController")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    async def initialize(self):
        """Initialize dashboard and all components"""
        try:
            self.logger.info("Initializing Enhanced Dashboard...")
            
            # Initialize core components
            from fixed_memory_manager import MemoryAwareModelManager
            self.memory_manager = MemoryAwareModelManager()
            await self.memory_manager.initialize()
            
            from unified_model_intelligence import UnifiedModelIntelligence
            self.unified_intelligence = UnifiedModelIntelligence(self.memory_manager)
            
            from intelligent_agent_orchestrator_fixed import IntelligentAgentOrchestrator
            self.orchestrator = IntelligentAgentOrchestrator()
            await self.orchestrator.initialize()
            
            from ultimate_ai_completion import UltimateAICompletion
            self.completion_system = UltimateAICompletion()
            await self.completion_system.initialize()
            
            # Initialize plugins
            self._initialize_plugins()
            
            self.is_initialized = True
            self.logger.info("Enhanced Dashboard initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dashboard: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _initialize_plugins(self):
        """Initialize dashboard plugins"""
        self.plugins = [
            SystemOverviewPlugin(self),
            ModelProviderControlPlugin(self.external_app_integration),
            WorkflowManagerPlugin(self),
            CompletionManagerPlugin(self)
        ]
    
    def create_gui(self):
        """Create enhanced GUI with plugin architecture"""
        if not GUI_AVAILABLE:
            self.logger.warning("GUI not available")
            return
        
        self.root = tk.Tk()
        self.root.title("Ultimate Copilot - Enhanced Dashboard")
        self.root.geometry("1400x900")
        
        # Set modern theme
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create notebook for plugin tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Add plugin tabs
        for plugin in self.plugins:
            tab_widget = plugin.create_widget(self.notebook)
            self.notebook.add(tab_widget, text=plugin.get_name())
        
        # Status bar
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_bar, text="Dashboard Ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.time_label = ttk.Label(self.status_bar, text="")
        self.time_label.pack(side=tk.RIGHT, padx=5)
        
        # Update time periodically
        self._update_time()
        
        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _update_time(self):
        """Update time display in status bar"""
        if self.time_label:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=current_time)
            self.root.after(1000, self._update_time)
    
    def _on_tab_changed(self, event):
        """Handle tab change events"""
        selected_tab = event.widget.tab('current')['text']
        
        # Notify plugins of activation/deactivation
        for plugin in self.plugins:
            if plugin.get_name() == selected_tab:
                plugin.on_activate()
            else:
                plugin.on_deactivate()
    
    async def start_background_updates(self):
        """Start background data updates"""
        if not self.update_task:
            self.update_task = asyncio.create_task(self._background_update_loop())
    
    async def _background_update_loop(self):
        """Background update loop"""
        while self.auto_refresh and self.is_initialized:
            try:
                await self.update_all_data()
                await asyncio.sleep(self.refresh_interval)
            except Exception as e:
                self.logger.error(f"Background update error: {e}")
                await asyncio.sleep(10)
    
    async def update_all_data(self):
        """Update data for all plugins"""
        try:
            # Update core metrics
            await self._update_core_metrics()
            
            # Update all plugins
            for plugin in self.plugins:
                try:
                    await plugin.update_data()
                except Exception as e:
                    self.logger.warning(f"Plugin {plugin.get_name()} update failed: {e}")
            
            # Update status bar
            if self.status_label:
                status_text = f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
                if self.alerts:
                    unack_alerts = len([a for a in self.alerts if not a.acknowledged])
                    if unack_alerts > 0:
                        status_text += f" | {unack_alerts} alerts"
                self.status_label.config(text=status_text)
                
        except Exception as e:
            self.logger.error(f"Failed to update dashboard data: {e}")
    
    async def _update_core_metrics(self):
        """Update core system metrics"""
        self.current_metrics.clear()
        
        try:
            # Memory metrics
            if self.memory_manager:
                memory_status = await self.memory_manager.get_memory_status()
                vram_usage = memory_status.get('current_usage_mb', 0)
                vram_max = memory_status.get('max_vram_mb', 8192)
                vram_percent = (vram_usage / vram_max) * 100 if vram_max > 0 else 0
                
                status = "normal"
                if vram_percent > 90:
                    status = "critical"
                elif vram_percent > 75:
                    status = "warning"
                
                self.current_metrics.append(DashboardMetric(
                    name="VRAM Usage",
                    value=f"{vram_usage}MB ({vram_percent:.1f}%)",
                    status=status
                ))
                
                self.current_metrics.append(DashboardMetric(
                    name="Loaded Models",
                    value=len(memory_status.get('loaded_models', [])),
                    unit="models"
                ))
            
            # Intelligence metrics
            if self.unified_intelligence:
                ui_status = await self.unified_intelligence.get_system_status()
                self.current_metrics.append(DashboardMetric(
                    name="Active Allocations",
                    value=ui_status.get('active_allocations', 0),
                    unit="allocations"
                ))
            
            # Completion metrics
            if self.completion_system:
                comp_status = await self.completion_system.get_system_status()
                comp_metrics = comp_status.get('completion_system', {}).get('performance_metrics', {})
                if comp_metrics:
                    avg_quality = comp_metrics.get('average_quality', 0)
                    quality_status = "normal"
                    if avg_quality < 6:
                        quality_status = "warning"
                    elif avg_quality < 4:
                        quality_status = "critical"
                    
                    self.current_metrics.append(DashboardMetric(
                        name="Avg Quality",
                        value=f"{avg_quality:.1f}",
                        unit="/10",
                        status=quality_status
                    ))
            
        except Exception as e:
            self.logger.warning(f"Failed to update core metrics: {e}")
    
    def get_current_metrics(self) -> List[DashboardMetric]:
        """Get current dashboard metrics"""
        return self.current_metrics.copy()
    
    def add_alert(self, severity: str, title: str, message: str):
        """Add new alert"""
        alert = DashboardAlert(
            id=f"alert_{datetime.now().timestamp()}",
            severity=severity,
            title=title,
            message=message
        )
        self.alerts.append(alert)
        self.logger.info(f"Alert added: {title}")
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()
        self.logger.info("All alerts cleared")
    
    # Integration methods for plugins
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            status = {"status": "ready" if self.is_initialized else "initializing"}
            
            if self.memory_manager:
                status["memory"] = await self.memory_manager.get_memory_status()
            
            if self.unified_intelligence:
                status["intelligence"] = await self.unified_intelligence.get_system_status()
            
            if self.completion_system:
                comp_status = await self.completion_system.get_system_status()
                status["completion"] = comp_status.get("completion_system", {})
            
            if self.orchestrator:
                status["orchestrator"] = {
                    "active_workflows": len(self.orchestrator.active_workflows),
                    "agent_pool_size": len(self.orchestrator.agent_pool)
                }
            
            return status
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def start_workflow(self, template: str) -> Dict[str, Any]:
        """Start a new workflow"""
        try:
            if self.orchestrator:
                workflow = await self.orchestrator.create_workflow_from_template(template)
                results = await self.orchestrator.execute_workflow(workflow)
                return {
                    "success": True,
                    "workflow_id": workflow.workflow_id,
                    "results": len(results)
                }
            else:
                return {"success": False, "error": "Orchestrator not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def stop_current_workflow(self):
        """Stop current workflow"""
        # Implementation would depend on orchestrator capabilities
        pass
    
    async def get_active_workflows(self) -> List[Dict]:
        """Get list of active workflows"""
        try:
            if self.orchestrator:
                workflows = []
                for wf_id, workflow in self.orchestrator.active_workflows.items():
                    workflows.append({
                        "id": wf_id,
                        "type": workflow.workflow_type.value,
                        "status": "running",
                        "progress": 50,  # This would be calculated
                        "started": workflow.created_at.strftime("%H:%M:%S")
                    })
                return workflows
            return []
        except Exception as e:
            self.logger.error(f"Failed to get active workflows: {e}")
            return []
    
    async def get_workflow_results(self, workflow_id: str) -> Dict:
        """Get workflow results"""
        # Implementation would load results from orchestrator
        return {"workflow_id": workflow_id, "status": "completed"}
    
    async def run_completion(self, prompt: str, completion_type: str, quality: str) -> Dict:
        """Run AI completion"""
        try:
            if self.completion_system:
                result = await self.completion_system.run_completion(prompt, completion_type, quality)
                return result
            else:
                return {"success": False, "error": "Completion system not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_recent_completions(self) -> List[Dict]:
        """Get recent completions"""
        try:
            if self.completion_system and hasattr(self.completion_system, 'completion_history'):
                completions = []
                for comp in self.completion_system.completion_history[-20:]:
                    completions.append({
                        "time": comp.start_time.strftime("%H:%M:%S"),
                        "type": getattr(comp, 'completion_type', 'unknown'),
                        "quality": comp.quality_score,
                        "status": "success" if comp.success else "failed",
                        "duration": comp.processing_time
                    })
                return completions
            return []
        except Exception as e:
            self.logger.error(f"Failed to get recent completions: {e}")
            return []
    
    async def export_system_report(self):
        """Export comprehensive system report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"dashboard_report_{timestamp}.json"
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "system_status": await self.get_system_status(),
                "metrics": [
                    {
                        "name": m.name,
                        "value": str(m.value),
                        "unit": m.unit,
                        "status": m.status,
                        "timestamp": m.timestamp.isoformat()
                    }
                    for m in self.current_metrics
                ],
                "alerts": [
                    {
                        "severity": a.severity,
                        "title": a.title,
                        "message": a.message,
                        "timestamp": a.timestamp.isoformat(),
                        "acknowledged": a.acknowledged
                    }
                    for a in self.alerts
                ]
            }
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            
            self.logger.info(f"System report exported: {report_file}")
            
            if GUI_AVAILABLE:
                messagebox.showinfo("Export Complete", f"Report saved as {report_file}")
            
        except Exception as e:
            error_msg = f"Failed to export report: {e}"
            self.logger.error(error_msg)
            if GUI_AVAILABLE:
                messagebox.showerror("Export Error", error_msg)
    
    def run(self):
        """Run the enhanced dashboard"""
        if GUI_AVAILABLE:
            self.create_gui()
            
            # Start background updates in a thread
            def run_background():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.start_background_updates())
            
            background_thread = threading.Thread(target=run_background, daemon=True)
            background_thread.start()
            
            # Start GUI main loop
            self.root.mainloop()
        else:
            # Console mode fallback
            asyncio.run(self._run_console_mode())
    
    async def _run_console_mode(self):
        """Run in console mode"""
        print("Enhanced Dashboard - Console Mode")
        await self.start_background_updates()
        
        while True:
            try:
                await asyncio.sleep(1)
            except KeyboardInterrupt:
                break

async def main():
    """Main entry point for enhanced dashboard"""
    
    # This is where you would integrate your external model provider control app
    # Example integration function:
    def integrate_external_app():
        """Integration point for your model provider control app"""
        print("Launching external model provider control app...")
        # Your app launch code here
        # This could open your app window, embed it, or establish communication
    
    # Create dashboard with external app integration
    dashboard = EnhancedDashboardController(external_app_integration=integrate_external_app)
    
    # Initialize
    success = await dashboard.initialize()
    if not success:
        print("Failed to initialize enhanced dashboard")
        return
    
    print("Enhanced Dashboard initialized successfully!")
    print("Features:")
    print("- System Overview with real-time metrics")
    print("- Model Provider Control (ready for your app integration)")
    print("- Workflow Management")
    print("- AI Completion Interface")
    print("- Plugin architecture for easy extensibility")
    
    # Run dashboard
    dashboard.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")
    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()
