#!/usr/bin/env python3
"""
Ultimate Copilot Dashboard

A comprehensive dashboard for monitoring and controlling the Ultimate Copilot system
with real-time metrics, model management, and agent coordination.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import threading
from pathlib import Path
import time

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("GUI not available, using console mode")

class UltimateCopilotDashboard:
    """
    Comprehensive dashboard for the Ultimate Copilot system
    """
    
    def __init__(self):
        # Core components
        self.memory_manager = None
        self.unified_intelligence = None
        self.orchestrator = None
        self.completion_system = None
        
        # Dashboard state
        self.system_status = {}
        self.metrics_history = []
        self.refresh_interval = 5  # seconds
        self.auto_refresh = True
        
        # GUI components (if available)
        self.root = None
        self.status_text = None
        self.metrics_tree = None
        self.log_text = None
        
        # Setup logging
        self.logger = logging.getLogger("Dashboard")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.log_messages = []
    
    async def initialize(self):
        """Initialize all system components"""
        try:
            self.logger.info("Initializing Ultimate Copilot Dashboard...")
            
            # Initialize memory manager
            from fixed_memory_manager import MemoryAwareModelManager
            self.memory_manager = MemoryAwareModelManager()
            await self.memory_manager.initialize()
            
            # Initialize unified intelligence
            from unified_model_intelligence import UnifiedModelIntelligence
            self.unified_intelligence = UnifiedModelIntelligence(self.memory_manager)
            
            # Initialize orchestrator
            from intelligent_agent_orchestrator_fixed import IntelligentAgentOrchestrator
            self.orchestrator = IntelligentAgentOrchestrator()
            await self.orchestrator.initialize()
            
            # Initialize completion system
            from ultimate_ai_completion import UltimateAICompletion
            self.completion_system = UltimateAICompletion()
            await self.completion_system.initialize()
            
            # Start background monitoring
            asyncio.create_task(self._monitor_system())
            
            self.logger.info("Ultimate Copilot Dashboard initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize dashboard: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def _monitor_system(self):
        """Background system monitoring"""
        while self.auto_refresh:
            try:
                await self._update_system_status()
                await asyncio.sleep(self.refresh_interval)
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(10)
    
    async def _update_system_status(self):
        """Update system status and metrics"""
        try:
            # Collect status from all components
            status = {
                "timestamp": datetime.now().isoformat(),
                "memory_manager": {},
                "unified_intelligence": {},
                "orchestrator": {},
                "completion_system": {}
            }
            
            # Memory manager status
            if self.memory_manager:
                try:
                    memory_status = await self.memory_manager.get_memory_status()
                    status["memory_manager"] = memory_status
                except Exception as e:
                    status["memory_manager"] = {"error": str(e)}
            
            # Unified intelligence status
            if self.unified_intelligence:
                try:
                    ui_status = await self.unified_intelligence.get_system_status()
                    status["unified_intelligence"] = ui_status
                except Exception as e:
                    status["unified_intelligence"] = {"error": str(e)}
            
            # Orchestrator status
            if self.orchestrator:
                try:
                    status["orchestrator"] = {
                        "active_workflows": len(self.orchestrator.active_workflows),
                        "agent_pool_size": len(self.orchestrator.agent_pool),
                        "execution_results": len(self.orchestrator.execution_results)
                    }
                except Exception as e:
                    status["orchestrator"] = {"error": str(e)}
            
            # Completion system status
            if self.completion_system:
                try:
                    comp_status = await self.completion_system.get_system_status()
                    status["completion_system"] = comp_status["completion_system"]
                except Exception as e:
                    status["completion_system"] = {"error": str(e)}
            
            self.system_status = status
            self.metrics_history.append(status)
            
            # Keep only last 100 entries
            if len(self.metrics_history) > 100:
                self.metrics_history.pop(0)
            
            # Update GUI if available
            if self.root:
                self._update_gui()
                
        except Exception as e:
            self.logger.error(f"Status update failed: {e}")
    
    def create_gui(self):
        """Create the GUI dashboard"""
        if not GUI_AVAILABLE:
            self.logger.warning("GUI not available, skipping GUI creation")
            return
        
        self.root = tk.Tk()
        self.root.title("Ultimate Copilot Dashboard")
        self.root.geometry("1200x800")
        
        # Create main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # System Status Tab
        status_frame = ttk.Frame(notebook)
        notebook.add(status_frame, text="System Status")
        self._create_status_tab(status_frame)
        
        # Models Tab
        models_frame = ttk.Frame(notebook)
        notebook.add(models_frame, text="Models")
        self._create_models_tab(models_frame)
        
        # Agents Tab
        agents_frame = ttk.Frame(notebook)
        notebook.add(agents_frame, text="Agents")
        self._create_agents_tab(agents_frame)
        
        # Completions Tab
        completions_frame = ttk.Frame(notebook)
        notebook.add(completions_frame, text="Completions")
        self._create_completions_tab(completions_frame)
        
        # Logs Tab
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="Logs")
        self._create_logs_tab(logs_frame)
        
        # Control buttons
        control_frame = ttk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(control_frame, text="Refresh", command=self._refresh_gui).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Save Report", command=self._save_report).pack(side=tk.LEFT, padx=5)
        
        auto_refresh_var = tk.BooleanVar(value=self.auto_refresh)
        ttk.Checkbutton(control_frame, text="Auto Refresh", variable=auto_refresh_var,
                       command=lambda: setattr(self, 'auto_refresh', auto_refresh_var.get())).pack(side=tk.LEFT, padx=5)
    
    def _create_status_tab(self, parent):
        """Create system status tab"""
        # Overall status
        status_label_frame = ttk.LabelFrame(parent, text="System Overview")
        status_label_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(status_label_frame, height=10)
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Metrics tree
        metrics_label_frame = ttk.LabelFrame(parent, text="Live Metrics")
        metrics_label_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("Component", "Metric", "Value", "Status")
        self.metrics_tree = ttk.Treeview(metrics_label_frame, columns=columns, show="headings")
        
        for col in columns:
            self.metrics_tree.heading(col, text=col)
            self.metrics_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(metrics_label_frame, orient=tk.VERTICAL, command=self.metrics_tree.yview)
        self.metrics_tree.configure(yscrollcommand=scrollbar.set)
        
        self.metrics_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_models_tab(self, parent):
        """Create models management tab"""
        # Available models
        models_label_frame = ttk.LabelFrame(parent, text="Available Models")
        models_label_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("Provider", "Model ID", "Status", "VRAM", "Last Used")
        self.models_tree = ttk.Treeview(models_label_frame, columns=columns, show="headings")
        
        for col in columns:
            self.models_tree.heading(col, text=col)
            self.models_tree.column(col, width=120)
        
        models_scrollbar = ttk.Scrollbar(models_label_frame, orient=tk.VERTICAL, command=self.models_tree.yview)
        self.models_tree.configure(yscrollcommand=models_scrollbar.set)
        
        self.models_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        models_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Model controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Load Model", command=self._load_model).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Unload Model", command=self._unload_model).pack(side=tk.LEFT, padx=5)
        ttk.Button(controls_frame, text="Test Model", command=self._test_model).pack(side=tk.LEFT, padx=5)
    
    def _create_agents_tab(self, parent):
        """Create agents management tab"""
        # Active agents
        agents_label_frame = ttk.LabelFrame(parent, text="Active Agents")
        agents_label_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("Agent ID", "Role", "Status", "Current Task", "Model Used")
        self.agents_tree = ttk.Treeview(agents_label_frame, columns=columns, show="headings")
        
        for col in columns:
            self.agents_tree.heading(col, text=col)
            self.agents_tree.column(col, width=120)
        
        agents_scrollbar = ttk.Scrollbar(agents_label_frame, orient=tk.VERTICAL, command=self.agents_tree.yview)
        self.agents_tree.configure(yscrollcommand=agents_scrollbar.set)
        
        self.agents_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        agents_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_completions_tab(self, parent):
        """Create completions management tab"""
        # Completion history
        completions_label_frame = ttk.LabelFrame(parent, text="Recent Completions")
        completions_label_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("Request ID", "Type", "Quality", "Time", "Model", "Status")
        self.completions_tree = ttk.Treeview(completions_label_frame, columns=columns, show="headings")
        
        for col in columns:
            self.completions_tree.heading(col, text=col)
            self.completions_tree.column(col, width=100)
        
        completions_scrollbar = ttk.Scrollbar(completions_label_frame, orient=tk.VERTICAL, command=self.completions_tree.yview)
        self.completions_tree.configure(yscrollcommand=completions_scrollbar.set)
        
        self.completions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        completions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Quick completion test
        test_frame = ttk.LabelFrame(parent, text="Quick Completion Test")
        test_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(test_frame, text="Prompt:").pack(anchor=tk.W, padx=5)
        self.test_prompt_entry = tk.Entry(test_frame, width=80)
        self.test_prompt_entry.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Button(test_frame, text="Run Completion", command=self._run_test_completion).pack(padx=5, pady=5)
    
    def _create_logs_tab(self, parent):
        """Create logs tab"""
        logs_label_frame = ttk.LabelFrame(parent, text="System Logs")
        logs_label_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(logs_label_frame)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Log controls
        log_controls = ttk.Frame(parent)
        log_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(log_controls, text="Clear Logs", command=self._clear_logs).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_controls, text="Export Logs", command=self._export_logs).pack(side=tk.LEFT, padx=5)
    
    def _update_gui(self):
        """Update GUI with current system status"""
        if not self.root:
            return
        
        try:
            # Update status text
            if self.status_text:
                self.status_text.delete(1.0, tk.END)
                status_summary = self._format_status_summary()
                self.status_text.insert(1.0, status_summary)
            
            # Update metrics tree
            if self.metrics_tree:
                # Clear existing items
                for item in self.metrics_tree.get_children():
                    self.metrics_tree.delete(item)
                
                # Add current metrics
                self._populate_metrics_tree()
            
            # Update models tree
            if hasattr(self, 'models_tree') and self.models_tree:
                self._update_models_tree()
            
            # Update agents tree
            if hasattr(self, 'agents_tree') and self.agents_tree:
                self._update_agents_tree()
            
            # Update completions tree
            if hasattr(self, 'completions_tree') and self.completions_tree:
                self._update_completions_tree()
            
            # Update logs
            if self.log_text:
                self._update_logs()
                
        except Exception as e:
            self.logger.error(f"GUI update failed: {e}")
    
    def _format_status_summary(self) -> str:
        """Format system status summary"""
        if not self.system_status:
            return "No status data available"
        
        summary = []
        summary.append(f"Last Updated: {self.system_status.get('timestamp', 'Unknown')}")
        summary.append("")
        
        # Memory status
        memory = self.system_status.get('memory_manager', {})
        if memory and 'error' not in memory:
            summary.append("MEMORY MANAGER:")
            summary.append(f"  VRAM Usage: {memory.get('current_usage_mb', 0)}MB / {memory.get('max_vram_mb', 0)}MB")
            summary.append(f"  Loaded Models: {len(memory.get('loaded_models', []))}")
            summary.append(f"  Available Models: {len(memory.get('available_models', []))}")
        else:
            summary.append("MEMORY MANAGER: Error or unavailable")
        
        summary.append("")
        
        # Unified intelligence
        ui = self.system_status.get('unified_intelligence', {})
        if ui and 'error' not in ui:
            summary.append("MODEL INTELLIGENCE:")
            summary.append(f"  Active Allocations: {ui.get('active_allocations', 0)}")
            summary.append(f"  Total Agents: {ui.get('total_agents', 0)}")
        else:
            summary.append("MODEL INTELLIGENCE: Error or unavailable")
        
        summary.append("")
        
        # Orchestrator
        orch = self.system_status.get('orchestrator', {})
        if orch and 'error' not in orch:
            summary.append("ORCHESTRATOR:")
            summary.append(f"  Active Workflows: {orch.get('active_workflows', 0)}")
            summary.append(f"  Agent Pool Size: {orch.get('agent_pool_size', 0)}")
        else:
            summary.append("ORCHESTRATOR: Error or unavailable")
        
        summary.append("")
        
        # Completion system
        comp = self.system_status.get('completion_system', {})
        if comp and 'error' not in comp:
            summary.append("COMPLETION SYSTEM:")
            summary.append(f"  Active Requests: {comp.get('active_requests', 0)}")
            summary.append(f"  Total Completions: {comp.get('total_completions', 0)}")
            
            metrics = comp.get('performance_metrics', {})
            if metrics:
                summary.append(f"  Average Quality: {metrics.get('average_quality', 0):.1f}/10")
                summary.append(f"  Average Time: {metrics.get('average_processing_time', 0):.1f}s")
        else:
            summary.append("COMPLETION SYSTEM: Error or unavailable")
        
        return "\n".join(summary)
    
    def _populate_metrics_tree(self):
        """Populate metrics tree with current data"""
        if not self.system_status:
            return
        
        # Add memory metrics
        memory = self.system_status.get('memory_manager', {})
        if memory and 'error' not in memory:
            vram_usage = memory.get('current_usage_mb', 0)
            vram_max = memory.get('max_vram_mb', 8192)
            vram_percent = (vram_usage / vram_max) * 100 if vram_max > 0 else 0
            
            status = "Good" if vram_percent < 80 else "High" if vram_percent < 95 else "Critical"
            
            self.metrics_tree.insert("", tk.END, values=(
                "Memory", "VRAM Usage", f"{vram_usage}MB ({vram_percent:.1f}%)", status
            ))
            
            self.metrics_tree.insert("", tk.END, values=(
                "Memory", "Loaded Models", len(memory.get('loaded_models', [])), "Info"
            ))
        
        # Add orchestrator metrics
        orch = self.system_status.get('orchestrator', {})
        if orch and 'error' not in orch:
            self.metrics_tree.insert("", tk.END, values=(
                "Orchestrator", "Active Workflows", orch.get('active_workflows', 0), "Info"
            ))
            
            self.metrics_tree.insert("", tk.END, values=(
                "Orchestrator", "Agent Pool", orch.get('agent_pool_size', 0), "Info"
            ))
        
        # Add completion metrics
        comp = self.system_status.get('completion_system', {})
        if comp and 'error' not in comp:
            metrics = comp.get('performance_metrics', {})
            
            if metrics:
                quality = metrics.get('average_quality', 0)
                quality_status = "Excellent" if quality >= 8 else "Good" if quality >= 6 else "Poor"
                
                self.metrics_tree.insert("", tk.END, values=(
                    "Completion", "Avg Quality", f"{quality:.1f}/10", quality_status
                ))
                
                avg_time = metrics.get('average_processing_time', 0)
                time_status = "Fast" if avg_time < 5 else "Normal" if avg_time < 15 else "Slow"
                
                self.metrics_tree.insert("", tk.END, values=(
                    "Completion", "Avg Time", f"{avg_time:.1f}s", time_status
                ))
    
    def _update_models_tree(self):
        """Update models tree"""
        # Clear existing items
        for item in self.models_tree.get_children():
            self.models_tree.delete(item)
        
        memory = self.system_status.get('memory_manager', {})
        available_models = memory.get('available_models', {})
        
        for model_key, model_info in available_models.items():
            status = "Loaded" if model_info.get('is_loaded', False) else "Available"
            last_used = model_info.get('last_used', 'Never')
            if last_used != 'Never' and hasattr(last_used, 'strftime'):
                last_used = last_used.strftime('%H:%M:%S')
            
            self.models_tree.insert("", tk.END, values=(
                model_info.get('provider', 'Unknown'),
                model_info.get('model_id', model_key),
                status,
                f"{model_info.get('estimated_vram_mb', 0)}MB",
                str(last_used)
            ))
    
    def _update_agents_tree(self):
        """Update agents tree"""
        # Clear existing items
        for item in self.agents_tree.get_children():
            self.agents_tree.delete(item)
        
        # Get agent information from orchestrator
        if self.orchestrator and hasattr(self.orchestrator, 'agent_pool'):
            for agent_id, agent_info in self.orchestrator.agent_pool.items():
                if isinstance(agent_info, dict):
                    self.agents_tree.insert("", tk.END, values=(
                        agent_id,
                        agent_info.get('role', 'Unknown'),
                        agent_info.get('status', 'Unknown'),
                        agent_info.get('current_task', 'Idle'),
                        agent_info.get('model_used', 'None')
                    ))
    
    def _update_completions_tree(self):
        """Update completions tree"""
        # Clear existing items
        for item in self.completions_tree.get_children():
            self.completions_tree.delete(item)
        
        # Show recent completions
        if self.completion_system and hasattr(self.completion_system, 'completion_history'):
            recent_completions = self.completion_system.completion_history[-20:]  # Last 20
            
            for completion in recent_completions:
                status = "Success" if completion.success else "Failed"
                
                self.completions_tree.insert("", tk.END, values=(
                    completion.request_id[:20],  # Truncate long IDs
                    getattr(completion, 'completion_type', 'Unknown'),
                    f"{completion.quality_score:.1f}",
                    f"{completion.processing_time:.1f}s",
                    completion.model_used or 'None',
                    status
                ))
    
    def _update_logs(self):
        """Update log display"""
        # This would show recent log messages
        # For now, just show a placeholder
        if len(self.log_messages) > 0:
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(1.0, "\n".join(self.log_messages[-100:]))  # Last 100 messages
    
    def _refresh_gui(self):
        """Manually refresh GUI"""
        asyncio.create_task(self._update_system_status())
    
    def _save_report(self):
        """Save comprehensive system report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = f"dashboard_report_{timestamp}.json"
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "system_status": self.system_status,
                "metrics_history": self.metrics_history[-10:],  # Last 10 entries
                "dashboard_config": {
                    "refresh_interval": self.refresh_interval,
                    "auto_refresh": self.auto_refresh
                }
            }
            
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            if GUI_AVAILABLE:
                messagebox.showinfo("Report Saved", f"System report saved to {report_file}")
            else:
                print(f"System report saved to {report_file}")
                
        except Exception as e:
            error_msg = f"Failed to save report: {e}"
            if GUI_AVAILABLE:
                messagebox.showerror("Error", error_msg)
            else:
                print(error_msg)
    
    def _load_model(self):
        """Load selected model"""
        if GUI_AVAILABLE:
            messagebox.showinfo("Load Model", "Model loading functionality to be implemented")
    
    def _unload_model(self):
        """Unload selected model"""
        if GUI_AVAILABLE:
            messagebox.showinfo("Unload Model", "Model unloading functionality to be implemented")
    
    def _test_model(self):
        """Test selected model"""
        if GUI_AVAILABLE:
            messagebox.showinfo("Test Model", "Model testing functionality to be implemented")
    
    def _run_test_completion(self):
        """Run a test completion"""
        if GUI_AVAILABLE and hasattr(self, 'test_prompt_entry'):
            prompt = self.test_prompt_entry.get()
            if prompt:
                messagebox.showinfo("Test Completion", f"Would run completion for: {prompt}")
    
    def _clear_logs(self):
        """Clear log display"""
        if self.log_text:
            self.log_text.delete(1.0, tk.END)
        self.log_messages.clear()
    
    def _export_logs(self):
        """Export logs to file"""
        if GUI_AVAILABLE:
            messagebox.showinfo("Export Logs", "Log export functionality to be implemented")    async def run_console_mode(self):
        """Run dashboard in console mode"""
        print("=== Ultimate Copilot Dashboard - Console Mode ===")
        
        while True:
            try:
                print("\n" + "="*60)
                print(f"System Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*60)
                
                if self.system_status:
                    print(self._format_status_summary())
                else:
                    print("No status data available")
                
                print("\nCommands:")
                print("  r - Refresh status")
                print("  s - Save report")
                print("  m - Show models")
                print("  a - Show agents") 
                print("  c - Show completions")
                print("  q - Quit")
                
                try:
                    # Use a separate thread for input to avoid blocking
                    import concurrent.futures
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(input, "\nEnter command: ")
                        try:
                            choice = future.result(timeout=1.0).lower().strip()
                        except concurrent.futures.TimeoutError:
                            choice = 'r'  # Auto-refresh
                    
                    if choice == 'q':
                        break
                    elif choice == 'r':
                        print("Refreshing...")
                        await self._update_system_status()
                    elif choice == 's':
                        self._save_report()
                    elif choice == 'm':
                        self._show_models_console()
                    elif choice == 'a':
                        self._show_agents_console()
                    elif choice == 'c':
                        self._show_completions_console()
                    else:
                        if choice != 'r':  # Don't show error for auto-refresh
                            print("Unknown command")
                        
                except KeyboardInterrupt:
                    break
                except EOFError:
                    break
                except Exception as e:
                    print(f"Input error: {e}")
                    await asyncio.sleep(1)
                    
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(1)
        
        print("\nDashboard stopped.")
    
    def _show_models_console(self):
        """Show models in console"""
        memory = self.system_status.get('memory_manager', {})
        available_models = memory.get('available_models', {})
        
        if not available_models:
            print("No models available")
            return
        
        print("\nAvailable Models:")
        print(f"{'Provider':<12} {'Model ID':<25} {'Status':<10} {'VRAM':<8}")
        print("-" * 60)
        
        for model_key, model_info in available_models.items():
            status = "Loaded" if model_info.get('is_loaded', False) else "Available"
            
            print(f"{model_info.get('provider', 'Unknown'):<12} "
                  f"{model_info.get('model_id', model_key):<25} "
                  f"{status:<10} "
                  f"{model_info.get('estimated_vram_mb', 0)}MB")
    
    def _show_agents_console(self):
        """Show agents in console"""
        if not self.orchestrator or not hasattr(self.orchestrator, 'agent_pool'):
            print("No agent information available")
            return
        
        print("\nActive Agents:")
        print(f"{'Agent ID':<15} {'Role':<12} {'Status':<10}")
        print("-" * 40)
        
        for agent_id, agent_info in self.orchestrator.agent_pool.items():
            if isinstance(agent_info, dict):
                print(f"{agent_id:<15} "
                      f"{agent_info.get('role', 'Unknown'):<12} "
                      f"{agent_info.get('status', 'Unknown'):<10}")
    
    def _show_completions_console(self):
        """Show completions in console"""
        if not self.completion_system or not hasattr(self.completion_system, 'completion_history'):
            print("No completion history available")
            return
        
        recent = self.completion_system.completion_history[-10:]  # Last 10
        
        if not recent:
            print("No recent completions")
            return
        
        print("\nRecent Completions:")
        print(f"{'Request ID':<20} {'Type':<15} {'Quality':<8} {'Time':<8} {'Status':<8}")
        print("-" * 70)
        
        for completion in recent:
            status = "Success" if completion.success else "Failed"
            comp_type = getattr(completion, 'completion_type', 'Unknown')
            
            print(f"{completion.request_id[:20]:<20} "
                  f"{str(comp_type)[:15]:<15} "
                  f"{completion.quality_score:.1f}/10   "
                  f"{completion.processing_time:.1f}s     "
                  f"{status:<8}")
    
    def run_gui_mode(self):
        """Run dashboard in GUI mode"""
        if not GUI_AVAILABLE:
            print("GUI not available, falling back to console mode")
            return asyncio.run(self.run_console_mode())
        
        self.create_gui()
        
        # Start the GUI in a separate thread
        def run_gui():
            self.root.mainloop()
        
        gui_thread = threading.Thread(target=run_gui, daemon=True)
        gui_thread.start()
        
        return gui_thread

async def run_dashboard():
    """Run the Ultimate Copilot Dashboard"""
    dashboard = UltimateCopilotDashboard()
    
    # Initialize
    success = await dashboard.initialize()
    if not success:
        print("Failed to initialize dashboard")
        return False
    
    print("Dashboard initialized successfully")
    
    # Choose mode
    if GUI_AVAILABLE:
        print("GUI available - starting GUI mode")
        gui_thread = dashboard.run_gui_mode()
        
        # Keep the main thread alive
        try:
            while gui_thread.is_alive():
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down dashboard...")
    else:
        print("Starting console mode")
        await dashboard.run_console_mode()
    
    return True

if __name__ == "__main__":
    try:
        asyncio.run(run_dashboard())
    except KeyboardInterrupt:
        print("\nDashboard stopped by user")
    except Exception as e:
        print(f"Dashboard error: {e}")
        import traceback
        traceback.print_exc()
