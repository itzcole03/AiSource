#!/usr/bin/env python3
"""
Workspace Manager Integration

Integrates workspace management functionality into the Ultimate Copilot dashboard.
This version focuses on the core functionality without complex GUI dependencies.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
from datetime import datetime

from workspace_manager_clean import WorkspaceManager, WorkspaceInfo

class WorkspaceManagementPlugin:
    """Simplified workspace management plugin"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.workspace_manager = WorkspaceManager()
        self.logger = logging.getLogger("WorkspacePlugin")
        self.dashboard_context = None
        
    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata"""
        return {
            "name": "Workspace Management",
            "version": "1.0.0",
            "description": "Manage workspaces and agent assignments",
            "author": "Ultimate Copilot",
            "category": "workspace",
            "icon": "📁",
            "requires_gui": False
        }
        
    def initialize(self, dashboard_context) -> bool:
        """Initialize the plugin"""
        try:
            self.dashboard_context = dashboard_context
            self.workspace_manager.start_monitoring()
            
            # Add some default workspaces if none exist
            self._setup_default_workspaces()
            
            self.logger.info("Workspace management plugin initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize workspace plugin: {e}")
            return False
            
    def _setup_default_workspaces(self):
        """Setup default workspaces"""
        try:
            current_workspaces = self.workspace_manager.get_all_workspaces()
            if not current_workspaces:
                # Add current directory as a workspace
                current_dir = Path.cwd()
                self.workspace_manager.add_workspace(str(current_dir), "Current Project")
                
                # Add common workspace directories if they exist
                common_dirs = [
                    Path.home() / "Documents",
                    Path.home() / "Projects", 
                    Path.home() / "Code",
                    Path.home() / "Development"
                ]
                
                for directory in common_dirs:
                    if directory.exists():
                        self.workspace_manager.add_workspace(str(directory), directory.name)
                        
        except Exception as e:
            self.logger.error(f"Error setting up default workspaces: {e}")
            
    def create_ui(self, parent) -> Any:
        """Create the plugin UI (simplified)"""
        # For now, return a simple text widget showing workspace status
        try:
            import tkinter as tk
            from tkinter import ttk
            
            frame = ttk.Frame(parent)
            
            # Title
            title_label = ttk.Label(frame, text="Workspace Management", font=("Arial", 12, "bold"))
            title_label.pack(pady=5)
            
            # Status text
            status_text = tk.Text(frame, height=20, width=60)
            status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Update status
            self._update_status_display(status_text)
            
            return frame
            
        except ImportError:
            self.logger.warning("GUI not available, workspace plugin running in headless mode")
            return None
        except Exception as e:
            self.logger.error(f"Error creating workspace UI: {e}")
            return None
            
    def _update_status_display(self, text_widget):
        """Update the status display"""
        try:
            workspaces = self.workspace_manager.get_all_workspaces()
            
            status_lines = [
                "=== Workspace Management Status ===",
                f"Total Workspaces: {len(workspaces)}",
                f"Available: {len([w for w in workspaces if w.status == 'available'])}",
                f"In Use: {len([w for w in workspaces if w.status == 'in_use'])}",
                "",
                "Registered Workspaces:",
                ""
            ]
            
            for workspace in workspaces:
                status_lines.extend([
                    f"📁 {workspace.name}",
                    f"   Path: {workspace.path}",
                    f"   Type: {workspace.type}",
                    f"   Status: {workspace.status}",
                    f"   Agents: {workspace.agent_count}",
                    f"   Size: {workspace.size_mb:.1f} MB",
                    ""
                ])
                
            text_widget.delete(1.0, "end")
            text_widget.insert(1.0, "\n".join(status_lines))
            
        except Exception as e:
            self.logger.error(f"Error updating status display: {e}")
            
    def update(self) -> Dict[str, Any]:
        """Update plugin data"""
        try:
            workspaces = self.workspace_manager.get_all_workspaces()
            return {
                "workspace_count": len(workspaces),
                "available_workspaces": len([w for w in workspaces if w.status == "available"]),
                "active_workspaces": len([w for w in workspaces if w.status == "in_use"]),
                "total_agents": sum(w.agent_count for w in workspaces),
                "workspaces": [
                    {
                        "name": w.name,
                        "path": w.path,
                        "type": w.type,
                        "status": w.status,
                        "agent_count": w.agent_count
                    }
                    for w in workspaces
                ]
            }
        except Exception as e:
            self.logger.error(f"Error updating plugin data: {e}")
            return {}
            
    def add_workspace(self, path: str, name: Optional[str] = None, workspace_type: str = "general") -> bool:
        """Add a new workspace"""
        return self.workspace_manager.add_workspace(path, name, workspace_type)
        
    def remove_workspace(self, path: str) -> bool:
        """Remove a workspace"""
        return self.workspace_manager.remove_workspace(path)
        
    def assign_agent_to_workspace(self, agent_id: str, workspace_path: str) -> bool:
        """Assign an agent to a workspace"""
        return self.workspace_manager.assign_agent_to_workspace(agent_id, workspace_path)
        
    def remove_agent_from_workspace(self, agent_id: str) -> bool:
        """Remove an agent from its workspace"""
        return self.workspace_manager.remove_agent_from_workspace(agent_id)
        
    def get_workspace_for_agent(self, agent_id: str) -> Optional[WorkspaceInfo]:
        """Get the workspace assigned to an agent"""
        return self.workspace_manager.get_workspace_for_agent(agent_id)
        
    def get_workspace_context(self, workspace_path: str) -> Dict[str, Any]:
        """Get context for a workspace"""
        return self.workspace_manager.get_workspace_context(workspace_path)
        
    def get_optimal_workspace(self, task_type: Optional[str] = None, language: Optional[str] = None) -> Optional[WorkspaceInfo]:
        """Get optimal workspace for a task"""
        return self.workspace_manager.get_optimal_workspace(task_type, language)
        
    def cleanup(self):
        """Cleanup plugin resources"""
        try:
            if self.workspace_manager:
                self.workspace_manager.cleanup()
            self.logger.info("Workspace management plugin cleaned up")
        except Exception as e:
            self.logger.error(f"Error cleaning up workspace plugin: {e}")


# Workspace routing functions for agent integration
class WorkspaceRouter:
    """Routes agents to appropriate workspaces"""
    
    def __init__(self, workspace_manager: WorkspaceManager):
        self.workspace_manager = workspace_manager
        self.logger = logging.getLogger("WorkspaceRouter")
        
    def route_agent_to_workspace(self, agent_id: str, task_info: Dict[str, Any]) -> Optional[str]:
        """Route an agent to the most appropriate workspace based on task requirements"""
        try:
            # Extract task requirements
            task_type = task_info.get('type', 'general')
            language = task_info.get('language')
            workspace_hint = task_info.get('workspace')
            
            # If workspace is explicitly specified, use it
            if workspace_hint:
                workspaces = self.workspace_manager.get_all_workspaces()
                for workspace in workspaces:
                    if workspace_hint in workspace.path or workspace_hint == workspace.name:
                        if self.workspace_manager.assign_agent_to_workspace(agent_id, workspace.path):
                            return workspace.path
                            
            # Find optimal workspace based on task requirements
            optimal_workspace = self.workspace_manager.get_optimal_workspace(task_type, language)
            if optimal_workspace:
                if self.workspace_manager.assign_agent_to_workspace(agent_id, optimal_workspace.path):
                    return optimal_workspace.path
                    
            # Fallback to any available workspace
            available_workspaces = self.workspace_manager.get_available_workspaces()
            if available_workspaces:
                workspace = available_workspaces[0]
                if self.workspace_manager.assign_agent_to_workspace(agent_id, workspace.path):
                    return workspace.path
                    
            self.logger.warning(f"No suitable workspace found for agent {agent_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error routing agent to workspace: {e}")
            return None
            
    def get_agent_workspace_context(self, agent_id: str) -> Dict[str, Any]:
        """Get workspace context for an agent"""
        try:
            workspace = self.workspace_manager.get_workspace_for_agent(agent_id)
            if workspace:
                return self.workspace_manager.get_workspace_context(workspace.path)
            return {}
        except Exception as e:
            self.logger.error(f"Error getting workspace context for agent: {e}")
            return {}
            
    def update_agent_workspace(self, agent_id: str, new_workspace_path: str) -> bool:
        """Update an agent's workspace assignment"""
        try:
            # Remove from old workspace
            self.workspace_manager.remove_agent_from_workspace(agent_id)
            
            # Assign to new workspace
            return self.workspace_manager.assign_agent_to_workspace(agent_id, new_workspace_path)
            
        except Exception as e:
            self.logger.error(f"Error updating agent workspace: {e}")
            return False
