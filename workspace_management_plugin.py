#!/usr/bin/env python3
"""
Workspace Management Plugin for Ultimate Copilot Dashboard

This plugin provides a comprehensive interface for managing workspaces within
the Ultimate Copilot dashboard, allowing users to:
- Add, remove, and configure workspaces
- Assign agents to specific workspaces
- Monitor workspace activity
- View workspace context and structure
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from datetime import datetime

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    tk = ttk = filedialog = messagebox = None

from workspace_manager import WorkspaceManager, WorkspaceInfo

class WorkspaceManagementPlugin:
    """Plugin for workspace management in the dashboard"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.workspace_manager = WorkspaceManager()
        self.logger = logging.getLogger("WorkspacePlugin")
        self.ui_widget = None
        self.dashboard_context = None
        
        # UI components
        self.workspace_tree = None
        self.agent_listbox = None
        self.context_text = None
        self.status_label = None
        
        # Data
        self.selected_workspace = None
        self.refresh_interval = 5000  # 5 seconds
        
    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata"""
        return {
            "name": "Workspace Management",
            "version": "1.0.0",
            "description": "Manage workspaces and agent assignments",
            "author": "Ultimate Copilot",
            "category": "workspace",
            "icon": "📁",
            "requires_gui": True
        }
        
    def initialize(self, dashboard_context) -> bool:
        """Initialize the plugin"""
        try:
            self.dashboard_context = dashboard_context
            self.workspace_manager.start_monitoring()
            self.logger.info("Workspace management plugin initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize workspace plugin: {e}")
            return False
              def create_ui(self, parent) -> Any:
        """Create the plugin UI"""
        if not GUI_AVAILABLE:
            self.logger.warning("GUI not available, workspace plugin running in headless mode")
            return None
            
        try:
            # Main container
            main_frame = ttk.Frame(parent)
            main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Create notebook for different views
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill=tk.BOTH, expand=True)
            
            # Workspace overview tab
            overview_frame = ttk.Frame(notebook)
            notebook.add(overview_frame, text="Workspaces")
            self._create_workspace_overview(overview_frame)
            
            # Agent assignments tab
            agents_frame = ttk.Frame(notebook)
            notebook.add(agents_frame, text="Agent Assignments")
            self._create_agent_assignments(agents_frame)
            
            # Workspace details tab
            details_frame = ttk.Frame(notebook)
            notebook.add(details_frame, text="Workspace Details")
            self._create_workspace_details(details_frame)
            
            # Settings tab
            settings_frame = ttk.Frame(notebook)
            notebook.add(settings_frame, text="Settings")
            self._create_settings(settings_frame)
            
            self.ui_widget = main_frame
            
            # Start periodic updates
            self._schedule_update()
            
            return main_frame
            
        except Exception as e:
            self.logger.error(f"Failed to create workspace management UI: {e}")
            return None
            
    def _create_workspace_overview(self, parent):
        """Create workspace overview UI"""
        # Toolbar
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(toolbar_frame, text="Add Workspace", 
                  command=self._add_workspace).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Remove Workspace", 
                  command=self._remove_workspace).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(toolbar_frame, text="Refresh", 
                  command=self._refresh_workspaces).pack(side=tk.LEFT, padx=(0, 5))
        
        # Workspace tree
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Name", "Type", "Status", "Agents", "Size")
        self.workspace_tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings")
        
        # Configure columns
        self.workspace_tree.heading("#0", text="Path")
        for col in columns:
            self.workspace_tree.heading(col, text=col)
            self.workspace_tree.column(col, width=100)
            
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.workspace_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.workspace_tree.xview)
        self.workspace_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack components
        self.workspace_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind events
        self.workspace_tree.bind("<<TreeviewSelect>>", self._on_workspace_select)
        
    def _create_agent_assignments(self, parent):
        """Create agent assignments UI"""
        # Split view
        paned_window = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Available workspaces
        left_frame = ttk.LabelFrame(paned_window, text="Available Workspaces")
        paned_window.add(left_frame)
        
        self.available_workspaces = tk.Listbox(left_frame)
        self.available_workspaces.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right side - Agent assignments
        right_frame = ttk.LabelFrame(paned_window, text="Agent Assignments")
        paned_window.add(right_frame)
        
        # Agent list
        self.agent_listbox = tk.Listbox(right_frame)
        self.agent_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 0))
        
        # Assignment controls
        controls_frame = ttk.Frame(right_frame)
        controls_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(controls_frame, text="Assign Agent", 
                  command=self._assign_agent).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="Remove Agent", 
                  command=self._remove_agent).pack(side=tk.LEFT)
                  
    def _create_workspace_details(self, parent):
        """Create workspace details UI"""
        # Context display
        context_frame = ttk.LabelFrame(parent, text="Workspace Context")
        context_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.context_text = tk.Text(context_frame, wrap=tk.WORD, height=20)
        context_scrollbar = ttk.Scrollbar(context_frame, orient=tk.VERTICAL, 
                                        command=self.context_text.yview)
        self.context_text.configure(yscrollcommand=context_scrollbar.set)
        
        self.context_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        context_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def _create_settings(self, parent):
        """Create settings UI"""
        settings_frame = ttk.LabelFrame(parent, text="Workspace Settings")
        settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Auto-discovery settings
        ttk.Label(settings_frame, text="Auto-discovery enabled:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        auto_discovery_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(settings_frame, variable=auto_discovery_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Monitoring interval
        ttk.Label(settings_frame, text="Monitoring interval (seconds):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        interval_var = tk.StringVar(value="30")
        ttk.Entry(settings_frame, textvariable=interval_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Status display
        status_frame = ttk.LabelFrame(parent, text="Status")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.pack(padx=5, pady=5)
        
    def _add_workspace(self):
        """Add a new workspace"""
        try:
            directory = filedialog.askdirectory(title="Select Workspace Directory")
            if directory:
                name = Path(directory).name
                
                # Ask for workspace type
                type_dialog = WorkspaceTypeDialog(self.ui_widget.winfo_toplevel())
                workspace_type = type_dialog.get_type()
                
                if workspace_type:
                    success = self.workspace_manager.add_workspace(directory, name, workspace_type)
                    if success:
                        self._refresh_workspaces()
                        self.status_label.config(text=f"Added workspace: {name}")
                    else:
                        messagebox.showerror("Error", "Failed to add workspace")
                        
        except Exception as e:
            self.logger.error(f"Error adding workspace: {e}")
            messagebox.showerror("Error", f"Failed to add workspace: {e}")
            
    def _remove_workspace(self):
        """Remove selected workspace"""
        try:
            selection = self.workspace_tree.selection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a workspace to remove")
                return
                
            item = selection[0]
            workspace_path = self.workspace_tree.item(item, "text")
            
            if messagebox.askyesno("Confirm", f"Remove workspace '{workspace_path}'?"):
                success = self.workspace_manager.remove_workspace(workspace_path)
                if success:
                    self._refresh_workspaces()
                    self.status_label.config(text=f"Removed workspace: {workspace_path}")
                else:
                    messagebox.showerror("Error", "Failed to remove workspace")
                    
        except Exception as e:
            self.logger.error(f"Error removing workspace: {e}")
            messagebox.showerror("Error", f"Failed to remove workspace: {e}")
            
    def _refresh_workspaces(self):
        """Refresh workspace list"""
        try:
            # Clear existing items
            for item in self.workspace_tree.get_children():
                self.workspace_tree.delete(item)
                
            # Add workspaces
            workspaces = self.workspace_manager.get_all_workspaces()
            for workspace in workspaces:
                values = (
                    workspace.name,
                    workspace.type,
                    workspace.status,
                    str(workspace.agent_count),
                    f"{workspace.size_mb:.1f} MB"
                )
                self.workspace_tree.insert("", tk.END, text=workspace.path, values=values)
                
            # Update available workspaces list
            if hasattr(self, 'available_workspaces'):
                self.available_workspaces.delete(0, tk.END)
                available = self.workspace_manager.get_available_workspaces()
                for workspace in available:
                    self.available_workspaces.insert(tk.END, f"{workspace.name} ({workspace.path})")
                    
        except Exception as e:
            self.logger.error(f"Error refreshing workspaces: {e}")
            
    def _on_workspace_select(self, event):
        """Handle workspace selection"""
        try:
            selection = self.workspace_tree.selection()
            if selection:
                item = selection[0]
                workspace_path = self.workspace_tree.item(item, "text")
                self.selected_workspace = workspace_path
                self._update_workspace_details(workspace_path)
                
        except Exception as e:
            self.logger.error(f"Error handling workspace selection: {e}")
            
    def _update_workspace_details(self, workspace_path: str):
        """Update workspace details display"""
        try:
            context = self.workspace_manager.get_workspace_context(workspace_path)
            
            if self.context_text:
                self.context_text.delete(1.0, tk.END)
                
                details = [
                    f"Workspace: {workspace_path}",
                    f"Type: {context.get('workspace_info', {}).get('type', 'Unknown')}",
                    f"Language: {context.get('workspace_info', {}).get('language', 'Unknown')}",
                    f"Framework: {context.get('workspace_info', {}).get('framework', 'Unknown')}",
                    f"Status: {context.get('workspace_info', {}).get('status', 'Unknown')}",
                    f"Active Agents: {len(context.get('active_agents', []))}",
                    "",
                    "Project Structure:",
                ]
                
                # Add project structure
                structure = context.get('project_structure', {})
                self._format_structure(structure, details, indent=0)
                
                details.append("")
                details.append("Recent Files:")
                
                # Add recent files
                recent_files = context.get('recent_files', [])
                for file_info in recent_files[:10]:
                    details.append(f"  {file_info.get('path', '')} ({file_info.get('size', 0)} bytes)")
                    
                self.context_text.insert(tk.END, "\n".join(details))
                
        except Exception as e:
            self.logger.error(f"Error updating workspace details: {e}")
            
    def _format_structure(self, structure, details, indent=0):
        """Format project structure for display"""
        prefix = "  " * indent
        for name, content in structure.items():
            if isinstance(content, dict):
                details.append(f"{prefix}{name}")
                self._format_structure(content, details, indent + 1)
            else:
                details.append(f"{prefix}{name}")
                
    def _assign_agent(self):
        """Assign agent to selected workspace"""
        try:
            # This would integrate with the agent system
            # For now, just show a dialog
            messagebox.showinfo("Info", "Agent assignment feature coming soon")
            
        except Exception as e:
            self.logger.error(f"Error assigning agent: {e}")
            
    def _remove_agent(self):
        """Remove agent from workspace"""
        try:
            # This would integrate with the agent system
            messagebox.showinfo("Info", "Agent removal feature coming soon")
            
        except Exception as e:
            self.logger.error(f"Error removing agent: {e}")
            
    def _schedule_update(self):
        """Schedule periodic updates"""
        if self.ui_widget:
            try:
                self._refresh_workspaces()
                self.ui_widget.after(self.refresh_interval, self._schedule_update)
            except Exception as e:
                self.logger.error(f"Error in scheduled update: {e}")
                
    def update(self) -> Dict[str, Any]:
        """Update plugin data"""
        try:
            workspaces = self.workspace_manager.get_all_workspaces()
            return {
                "workspace_count": len(workspaces),
                "active_workspaces": len([w for w in workspaces if w.status == "in_use"]),
                "total_agents": sum(w.agent_count for w in workspaces),
                "selected_workspace": self.selected_workspace
            }
        except Exception as e:
            self.logger.error(f"Error updating plugin data: {e}")
            return {}
            
    def cleanup(self):
        """Cleanup plugin resources"""
        try:
            if self.workspace_manager:
                self.workspace_manager.cleanup()
            self.logger.info("Workspace management plugin cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up workspace plugin: {e}")


class WorkspaceTypeDialog:
    """Dialog for selecting workspace type"""
    
    def __init__(self, parent):
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Select Workspace Type")
        self.dialog.geometry("300x200")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (200 // 2)
        self.dialog.geometry(f"300x200+{x}+{y}")
        
        # Create UI
        ttk.Label(self.dialog, text="Select workspace type:").pack(pady=10)
        
        self.type_var = tk.StringVar(value="general")
        
        types = ["general", "python", "javascript", "web", "data", "docker", "rust", "go", "java", "csharp"]
        
        for workspace_type in types:
            ttk.Radiobutton(self.dialog, text=workspace_type.title(), 
                           variable=self.type_var, value=workspace_type).pack(anchor=tk.W, padx=20)
            
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="OK", command=self._ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side=tk.LEFT, padx=5)
        
    def _ok(self):
        self.result = self.type_var.get()
        self.dialog.destroy()
        
    def _cancel(self):
        self.result = None
        self.dialog.destroy()
        
    def get_type(self):
        self.dialog.wait_window()
        return self.result
