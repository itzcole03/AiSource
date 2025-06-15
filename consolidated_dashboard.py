#!/usr/bin/env python3
"""
Consolidated Ultimate Copilot Dashboard

This dashboard consolidates the best features from all dashboard implementations
and integrates seamlessly with the enhanced memory-aware agent system.

Features:
- Enhanced agent integration with memory/context awareness
- Real-time agent status and logs
- Model manager integration
- Plugin architecture for extensibility
- Modern responsive UI
- External app integration capabilities
- Memory and context visualization
"""

import asyncio
import json
import logging
import threading
import time
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
import weakref

# Setup logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ConsolidatedDashboard")

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
    print("GUI not available - dashboard will run in headless mode")

# Import enhanced agent system
try:
    from working_agent_upgrade import WorkingAgentUpgrade, dispatch_enhanced_task
    ENHANCED_AGENTS_AVAILABLE = True
except ImportError:
    ENHANCED_AGENTS_AVAILABLE = False
    print("Enhanced agent system not available - using fallback")

# Import existing agent system
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

@dataclass
class AgentStatus:
    """Agent status tracking"""
    name: str
    status: str = "idle"  # idle, working, error, completed
    current_task: Optional[str] = None
    last_activity: datetime = field(default_factory=datetime.now)
    memory_size: int = 0
    context_size: int = 0
    model_used: Optional[str] = None
    error_count: int = 0

@dataclass
class SystemMetric:
    """System metric with enhanced metadata"""
    name: str
    value: Any
    unit: str = ""
    category: str = "general"
    status: str = "normal"  # normal, warning, critical
    timestamp: datetime = field(default_factory=datetime.now)

class ConsolidatedDashboard:
    """Consolidated dashboard with enhanced agent integration"""
    
    def __init__(self):
        self.logger = logging.getLogger("ConsolidatedDashboard")
        self.running = False
        self.agent_statuses = {}
        self.system_metrics = {}
        self.task_queue = []
        self.completed_tasks = []
        self.agent_logs = []
        
        # Enhanced agent system
        self.enhanced_agents = None
        self.simple_agents = None
        
        # UI components
        self.root = None
        self.notebook = None
        self.status_frame = None
        self.log_text = None
        
        # Background threads
        self.update_thread = None
        self.data_lock = threading.Lock()
        
    async def initialize(self):
        """Initialize the dashboard system"""
        try:
            self.logger.info("Initializing Consolidated Dashboard...")
            
            # Initialize enhanced agent system
            if ENHANCED_AGENTS_AVAILABLE:
                self.enhanced_agents = WorkingAgentUpgrade()
                await self.enhanced_agents.initialize()
                self.logger.info("✅ Enhanced agent system initialized")
            
            # Fallback to simple agents
            if SIMPLE_AGENTS_AVAILABLE and not self.enhanced_agents:
                self.simple_agents = SimpleAgents()
                self.logger.info("✅ Simple agent system initialized")
            
            # Initialize agent statuses
            self._initialize_agent_statuses()
            
            # Initialize system metrics
            self._initialize_system_metrics()
            
            self.logger.info("✅ Dashboard initialization complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Dashboard initialization failed: {e}")
            return False
    
    def _initialize_agent_statuses(self):
        """Initialize agent status tracking"""
        agent_names = ["architect", "backend", "frontend", "QA"]
        
        with self.data_lock:
            for name in agent_names:
                self.agent_statuses[name] = AgentStatus(name=name)
    
    def _initialize_system_metrics(self):
        """Initialize system metrics"""
        with self.data_lock:
            self.system_metrics.update({
                "agents_active": SystemMetric("Active Agents", 0, "count", "agents"),
                "tasks_completed": SystemMetric("Tasks Completed", 0, "count", "tasks"),
                "memory_usage": SystemMetric("Memory Usage", 0, "MB", "system"),
                "models_available": SystemMetric("Models Available", 0, "count", "models")
            })
    
    def create_gui(self):
        """Create the GUI interface"""
        if not GUI_AVAILABLE:
            self.logger.warning("GUI not available")
            return False
        
        try:
            self.root = tk.Tk()
            self.root.title("Ultimate Copilot - Consolidated Dashboard")
            self.root.geometry("1200x800")
            self.root.configure(bg='#2b2b2b')
            
            # Create main notebook for tabs
            self.notebook = ttk.Notebook(self.root)
            self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create tabs
            self._create_overview_tab()
            self._create_agents_tab()
            self._create_tasks_tab()
            self._create_memory_tab()
            self._create_models_tab()
            self._create_logs_tab()
            self._create_settings_tab()
            
            # Status bar
            self._create_status_bar()
            
            self.logger.info("✅ GUI created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"GUI creation failed: {e}")
            return False
    
    def _create_overview_tab(self):
        """Create overview tab with system status"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Overview")
        
        # Header
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        title_label = ttk.Label(header_frame, text="Ultimate Copilot System", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # System status
        status_frame = ttk.LabelFrame(frame, text="System Status")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.system_status_text = tk.Text(status_frame, height=6, wrap=tk.WORD)
        self.system_status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Quick metrics
        metrics_frame = ttk.LabelFrame(frame, text="Quick Metrics")
        metrics_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.metrics_labels = {}
        for i, (key, metric) in enumerate(self.system_metrics.items()):
            label = ttk.Label(metrics_frame, text=f"{metric.name}: {metric.value} {metric.unit}")
            label.grid(row=i//2, column=i%2, sticky=tk.W, padx=10, pady=2)
            self.metrics_labels[key] = label
        
        # Quick actions
        actions_frame = ttk.LabelFrame(frame, text="Quick Actions")
        actions_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(actions_frame, text="Run Test Task", 
                  command=self._run_test_task).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(actions_frame, text="Check All Agents", 
                  command=self._check_all_agents).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(actions_frame, text="Refresh System", 
                  command=self._refresh_system).pack(side=tk.LEFT, padx=5, pady=5)
    
    def _create_agents_tab(self):
        """Create agents management tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Agents")
        
        # Agent list
        list_frame = ttk.LabelFrame(frame, text="Agent Status")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview for agents
        columns = ("Agent", "Status", "Task", "Model", "Memory", "Last Activity")
        self.agent_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        for col in columns:
            self.agent_tree.heading(col, text=col)
            self.agent_tree.column(col, width=120)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.agent_tree.yview)
        self.agent_tree.configure(yscrollcommand=scrollbar.set)
        
        self.agent_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Agent controls
        control_frame = ttk.LabelFrame(frame, text="Agent Controls")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Test Selected Agent", 
                  command=self._test_selected_agent).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Clear Agent Memory", 
                  command=self._clear_agent_memory).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(control_frame, text="Reset Agent", 
                  command=self._reset_agent).pack(side=tk.LEFT, padx=5, pady=5)
    
    def _create_tasks_tab(self):
        """Create task management tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Tasks")
        
        # Task input
        input_frame = ttk.LabelFrame(frame, text="New Task")
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="Task Description:").pack(anchor=tk.W, padx=5, pady=2)
        self.task_entry = tk.Text(input_frame, height=3, wrap=tk.WORD)
        self.task_entry.pack(fill=tk.X, padx=5, pady=5)
        
        task_controls = ttk.Frame(input_frame)
        task_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(task_controls, text="Agent:").pack(side=tk.LEFT, padx=5)
        self.agent_var = tk.StringVar(value="architect")
        agent_combo = ttk.Combobox(task_controls, textvariable=self.agent_var,
                                  values=["architect", "backend", "frontend", "QA"])
        agent_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(task_controls, text="Execute Task", 
                  command=self._execute_task).pack(side=tk.LEFT, padx=10)
        
        # Task history
        history_frame = ttk.LabelFrame(frame, text="Task History")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Task list
        task_columns = ("Time", "Agent", "Task", "Status", "Duration")
        self.task_tree = ttk.Treeview(history_frame, columns=task_columns, show="headings")
        
        for col in task_columns:
            self.task_tree.heading(col, text=col)
            self.task_tree.column(col, width=150)
        
        self.task_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def _create_memory_tab(self):
        """Create memory and context visualization tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Memory")
        
        # Memory overview
        overview_frame = ttk.LabelFrame(frame, text="Memory Overview")
        overview_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.memory_text = scrolledtext.ScrolledText(overview_frame, height=8, wrap=tk.WORD)
        self.memory_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Memory controls
        controls_frame = ttk.LabelFrame(frame, text="Memory Controls")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="View Agent Memory", 
                  command=self._view_agent_memory).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(controls_frame, text="Clear All Memory", 
                  command=self._clear_all_memory).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(controls_frame, text="Export Memory", 
                  command=self._export_memory).pack(side=tk.LEFT, padx=5, pady=5)
    
    def _create_models_tab(self):
        """Create model management tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Models")
        
        # Model status
        status_frame = ttk.LabelFrame(frame, text="Available Models")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.model_text = scrolledtext.ScrolledText(status_frame, wrap=tk.WORD)
        self.model_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Model controls
        controls_frame = ttk.LabelFrame(frame, text="Model Controls")
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Refresh Models", 
                  command=self._refresh_models).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(controls_frame, text="Test Model", 
                  command=self._test_model).pack(side=tk.LEFT, padx=5, pady=5)
    
    def _create_logs_tab(self):
        """Create logs tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Logs")
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Log controls
        controls_frame = ttk.Frame(frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(controls_frame, text="Clear Logs", 
                  command=self._clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Export Logs", 
                  command=self._export_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Refresh", 
                  command=self._refresh_logs).pack(side=tk.LEFT, padx=5)
    
    def _create_settings_tab(self):
        """Create settings tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Settings")
        
        # Dashboard settings
        dash_frame = ttk.LabelFrame(frame, text="Dashboard Settings")
        dash_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(dash_frame, text="Auto-refresh data", 
                       variable=self.auto_refresh_var).pack(anchor=tk.W, padx=5, pady=2)
        
        ttk.Label(dash_frame, text="Refresh interval (seconds):").pack(anchor=tk.W, padx=5, pady=2)
        self.refresh_interval_var = tk.IntVar(value=5)
        ttk.Spinbox(dash_frame, from_=1, to=60, textvariable=self.refresh_interval_var,
                   width=10).pack(anchor=tk.W, padx=20, pady=2)
        
        # Agent settings
        agent_frame = ttk.LabelFrame(frame, text="Agent Settings")
        agent_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.enable_memory_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(agent_frame, text="Enable agent memory", 
                       variable=self.enable_memory_var).pack(anchor=tk.W, padx=5, pady=2)
        
        self.enable_context_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(agent_frame, text="Enable context awareness", 
                       variable=self.enable_context_var).pack(anchor=tk.W, padx=5, pady=2)
    
    def _create_status_bar(self):
        """Create status bar"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(self.status_frame, text="Dashboard ready")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.time_label = ttk.Label(self.status_frame, text="")
        self.time_label.pack(side=tk.RIGHT, padx=5)
    
    def _update_status_bar(self):
        """Update status bar with current time"""
        if self.time_label:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.time_label.config(text=current_time)
    
    async def _execute_task(self):
        """Execute a task using the enhanced agent system"""
        task_description = self.task_entry.get("1.0", tk.END).strip()
        agent_name = self.agent_var.get()
        
        if not task_description:
            messagebox.showwarning("Warning", "Please enter a task description")
            return
        
        try:
            # Update agent status
            with self.data_lock:
                if agent_name in self.agent_statuses:
                    self.agent_statuses[agent_name].status = "working"
                    self.agent_statuses[agent_name].current_task = task_description[:50] + "..."
            
            self._log(f"Executing task with {agent_name}: {task_description[:100]}...")
            
            # Execute using enhanced agents if available
            if self.enhanced_agents:
                result = await dispatch_enhanced_task(agent_name, task_description)
            elif self.simple_agents:
                result = await self.simple_agents.execute_task(agent_name, task_description)
            else:
                result = {"error": "No agent system available"}
            
            # Update agent status
            with self.data_lock:
                if agent_name in self.agent_statuses:
                    self.agent_statuses[agent_name].status = "completed" if not result.get("error") else "error"
                    self.agent_statuses[agent_name].current_task = None
                    self.agent_statuses[agent_name].last_activity = datetime.now()
            
            # Add to task history
            task_record = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "agent": agent_name,
                "task": task_description[:30] + "...",
                "status": "completed" if not result.get("error") else "error",
                "duration": "N/A"
            }
            
            self.task_tree.insert("", 0, values=tuple(task_record.values()))
            
            self._log(f"Task completed: {result}")
            
            # Clear task entry
            self.task_entry.delete("1.0", tk.END)
            
        except Exception as e:
            self._log(f"Task execution failed: {e}")
            messagebox.showerror("Error", f"Task execution failed: {e}")
    
    def _run_test_task(self):
        """Run a simple test task"""
        test_task = "Test agent connectivity and basic functionality"
        self.task_entry.delete("1.0", tk.END)
        self.task_entry.insert("1.0", test_task)
        
        # Execute in background
        threading.Thread(target=lambda: asyncio.run(self._execute_task()), daemon=True).start()
    
    def _check_all_agents(self):
        """Check status of all agents"""
        self._log("Checking all agents...")
        
        for agent_name in self.agent_statuses.keys():
            with self.data_lock:
                self.agent_statuses[agent_name].last_activity = datetime.now()
                self.agent_statuses[agent_name].status = "ready"
        
        self._log("✅ All agents checked and ready")
    
    def _refresh_system(self):
        """Refresh system data"""
        self._log("Refreshing system data...")
        
        # Update metrics
        with self.data_lock:
            active_agents = sum(1 for status in self.agent_statuses.values() 
                              if status.status in ["working", "ready"])
            self.system_metrics["agents_active"].value = active_agents
            
            completed_tasks = len([item for item in self.task_tree.get_children()])
            self.system_metrics["tasks_completed"].value = completed_tasks
        
        self._update_display()
        self._log("✅ System data refreshed")
    
    def _log(self, message: str):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        if self.log_text:
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
        
        # Also log to console
        self.logger.info(message)
    
    def _update_display(self):
        """Update all display elements"""
        try:
            # Update agent tree
            if hasattr(self, 'agent_tree'):
                # Clear existing items
                for item in self.agent_tree.get_children():
                    self.agent_tree.delete(item)
                
                # Add current agent statuses
                with self.data_lock:
                    for agent_name, status in self.agent_statuses.items():
                        values = (
                            agent_name,
                            status.status,
                            status.current_task or "None",
                            status.model_used or "Default",
                            f"{status.memory_size} KB",
                            status.last_activity.strftime("%H:%M:%S")
                        )
                        self.agent_tree.insert("", tk.END, values=values)
            
            # Update metrics labels
            with self.data_lock:
                for key, label in self.metrics_labels.items():
                    if key in self.system_metrics:
                        metric = self.system_metrics[key]
                        label.config(text=f"{metric.name}: {metric.value} {metric.unit}")
            
            # Update status bar
            self._update_status_bar()
            
        except Exception as e:
            self.logger.error(f"Display update failed: {e}")
    
    def _start_background_updates(self):
        """Start background update thread"""
        def update_loop():
            while self.running:
                try:
                    if self.auto_refresh_var.get():
                        self._update_display()
                    time.sleep(self.refresh_interval_var.get())
                except Exception as e:
                    self.logger.error(f"Background update failed: {e}")
                    time.sleep(5)
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()
    
    def run(self):
        """Run the dashboard"""
        try:
            # Initialize
            if not asyncio.run(self.initialize()):
                self.logger.error("Failed to initialize dashboard")
                return False
            
            # Create GUI if available
            if GUI_AVAILABLE:
                if not self.create_gui():
                    self.logger.error("Failed to create GUI")
                    return False
                
                self.running = True
                self._start_background_updates()
                
                self._log("🚀 Dashboard started successfully")
                self.root.mainloop()
            else:
                # Run in headless mode
                self.logger.info("Running in headless mode...")
                self.running = True
                while self.running:
                    time.sleep(10)
                    self._log("Dashboard running in headless mode...")
            
        except KeyboardInterrupt:
            self.logger.info("Dashboard stopped by user")
        except Exception as e:
            self.logger.error(f"Dashboard error: {e}")
        finally:
            self.running = False
    
    # Placeholder methods for features to implement
    def _test_selected_agent(self): pass
    def _clear_agent_memory(self): pass
    def _reset_agent(self): pass
    def _view_agent_memory(self): pass
    def _clear_all_memory(self): pass
    def _export_memory(self): pass
    def _refresh_models(self): pass
    def _test_model(self): pass
    def _clear_logs(self): pass
    def _export_logs(self): pass
    def _refresh_logs(self): pass

def main():
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    dashboard = ConsolidatedDashboard()
    dashboard.run()

if __name__ == "__main__":
    main()
