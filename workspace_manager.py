#!/usr/bin/env python3
"""
Workspace Manager

A comprehensive workspace management system for the Ultimate Copilot that allows
agents to be directed to specific local workspaces and manage workspace context.

Features:
- Workspace discovery and registration
- Agent-to-workspace routing
- Workspace context monitoring
- Cross-workspace intelligence persistence
- Real-time workspace status tracking
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict, field
import threading
import time

@dataclass
class WorkspaceInfo:
    """Information about a workspace"""
    path: str
    name: str
    type: str = "general"  # general, python, web, data, etc.
    status: str = "available"  # available, in_use, error
    description: str = ""
    language: str = ""
    framework: str = ""
    last_accessed: Optional[datetime] = None
    agent_count: int = 0
    file_count: int = 0
    size_mb: float = 0.0
    git_repo: bool = False
    git_branch: str = ""
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = datetime.now()
        if self.metadata is None:
            self.metadata = {}

class WorkspaceManager:
    """Manages workspaces for agent coordination"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "workspaces.json"
        self.workspaces: Dict[str, WorkspaceInfo] = {}
        self.active_agents: Dict[str, str] = {}  # agent_id -> workspace_path
        self.workspace_locks = {}  # For thread safety
        self.logger = logging.getLogger("WorkspaceManager")
        self._load_workspaces()
        self._monitor_thread = None
        self._stop_monitoring = False
        
    def _load_workspaces(self):
        """Load workspaces from config file"""
        try:
            if Path(self.config_file).exists():
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    for workspace_data in data.get('workspaces', []):
                        # Convert datetime strings back to datetime objects
                        if 'last_accessed' in workspace_data:
                            workspace_data['last_accessed'] = datetime.fromisoformat(
                                workspace_data['last_accessed']
                            )
                        workspace = WorkspaceInfo(**workspace_data)
                        self.workspaces[workspace.path] = workspace
                        self.workspace_locks[workspace.path] = threading.Lock()
                        
                self.logger.info(f"Loaded {len(self.workspaces)} workspaces")
        except Exception as e:
            self.logger.error(f"Error loading workspaces: {e}")
              def _save_workspaces(self):
        """Save workspaces to config file"""
        try:
            data = {
                'workspaces': [],
                'last_updated': datetime.now().isoformat()
            }
            
            for workspace in self.workspaces.values():
                workspace_dict = asdict(workspace)
                # Convert datetime to string for JSON serialization
                if workspace.last_accessed:
                    workspace_dict['last_accessed'] = workspace.last_accessed.isoformat()
                else:
                    workspace_dict['last_accessed'] = datetime.now().isoformat()
                data['workspaces'].append(workspace_dict)
                
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving workspaces: {e}")
            
    def add_workspace(self, path: str, name: Optional[str] = None, workspace_type: str = "general") -> bool:
        """Add a new workspace"""
        try:
            abs_path = str(Path(path).resolve())
            
            if not Path(abs_path).exists():
                self.logger.error(f"Workspace path does not exist: {abs_path}")
                return False
                
            if abs_path in self.workspaces:
                self.logger.warning(f"Workspace already exists: {abs_path}")
                return True
                
            # Auto-detect workspace information
            workspace_info = self._analyze_workspace(abs_path)
            workspace_info.name = name or Path(abs_path).name
            workspace_info.type = workspace_type
            
            self.workspaces[abs_path] = workspace_info
            self.workspace_locks[abs_path] = threading.Lock()
            
            self._save_workspaces()
            self.logger.info(f"Added workspace: {abs_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding workspace: {e}")
            return False
            
    def remove_workspace(self, path: str) -> bool:
        """Remove a workspace"""
        try:
            abs_path = str(Path(path).resolve())
            
            if abs_path not in self.workspaces:
                self.logger.warning(f"Workspace not found: {abs_path}")
                return False
                
            # Check if any agents are active in this workspace
            active_agents = [agent_id for agent_id, wp in self.active_agents.items() if wp == abs_path]
            if active_agents:
                self.logger.error(f"Cannot remove workspace with active agents: {active_agents}")
                return False
                
            del self.workspaces[abs_path]
            if abs_path in self.workspace_locks:
                del self.workspace_locks[abs_path]
                
            self._save_workspaces()
            self.logger.info(f"Removed workspace: {abs_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing workspace: {e}")
            return False
            
    def _analyze_workspace(self, path: str) -> WorkspaceInfo:
        """Analyze workspace to determine type and metadata"""
        workspace = WorkspaceInfo(path=path, name=Path(path).name)
        
        try:
            # Check if it's a git repository
            git_dir = Path(path) / '.git'
            if git_dir.exists():
                workspace.git_repo = True
                try:
                    # Try to get current branch
                    head_file = git_dir / 'HEAD'
                    if head_file.exists():
                        with open(head_file, 'r') as f:
                            head_content = f.read().strip()
                            if head_content.startswith('ref: refs/heads/'):
                                workspace.git_branch = head_content.split('/')[-1]
                except Exception:
                    pass
                    
            # Analyze files to determine project type
            files = list(Path(path).rglob('*'))
            workspace.file_count = len([f for f in files if f.is_file()])
            
            # Calculate size
            total_size = sum(f.stat().st_size for f in files if f.is_file())
            workspace.size_mb = total_size / (1024 * 1024)
            
            # Detect project type and language
            workspace.type, workspace.language, workspace.framework = self._detect_project_type(path)
            
        except Exception as e:
            self.logger.warning(f"Error analyzing workspace {path}: {e}")
            
        return workspace
        
    def _detect_project_type(self, path: str) -> Tuple[str, str, str]:
        """Detect project type, language, and framework"""
        path_obj = Path(path)
        
        # Check for specific files that indicate project type
        indicators = {
            'python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
            'javascript': ['package.json', 'yarn.lock', 'package-lock.json'],
            'web': ['index.html', 'main.html', 'app.html'],
            'data': ['data/', 'datasets/', '*.csv', '*.json', 'notebooks/'],
            'docker': ['Dockerfile', 'docker-compose.yml'],
            'rust': ['Cargo.toml'],
            'go': ['go.mod'],
            'java': ['pom.xml', 'build.gradle'],
            'csharp': ['*.csproj', '*.sln'],
        }
        
        detected_types = []
        language = ""
        framework = ""
        
        for project_type, files in indicators.items():
            for pattern in files:
                if any(path_obj.glob(pattern)):
                    detected_types.append(project_type)
                    language = project_type
                    break
                    
        # Detect frameworks
        if language == 'python':
            if any(path_obj.glob('**/django*')):
                framework = "django"
            elif any(path_obj.glob('**/flask*')):
                framework = "flask"
            elif any(path_obj.glob('**/fastapi*')):
                framework = "fastapi"
            elif any(path_obj.glob('*.ipynb')):
                framework = "jupyter"
                
        elif language == 'javascript':
            if (path_obj / 'package.json').exists():
                try:
                    with open(path_obj / 'package.json', 'r') as f:
                        package_data = json.load(f)
                        deps = {**package_data.get('dependencies', {}), 
                               **package_data.get('devDependencies', {})}
                        
                        if 'react' in deps:
                            framework = "react"
                        elif 'vue' in deps:
                            framework = "vue"
                        elif 'angular' in deps:
                            framework = "angular"
                        elif 'express' in deps:
                            framework = "express"
                        elif 'next' in deps:
                            framework = "next.js"
                except Exception:
                    pass
                    
        # Return the most specific type found
        if detected_types:
            return detected_types[0], language, framework
        else:
            return "general", "", ""
            
    def assign_agent_to_workspace(self, agent_id: str, workspace_path: str) -> bool:
        """Assign an agent to a specific workspace"""
        try:
            abs_path = str(Path(workspace_path).resolve())
            
            if abs_path not in self.workspaces:
                self.logger.error(f"Workspace not found: {abs_path}")
                return False
                
            workspace = self.workspaces[abs_path]
            
            # Update agent assignment
            old_workspace = self.active_agents.get(agent_id)
            if old_workspace and old_workspace in self.workspaces:
                self.workspaces[old_workspace].agent_count -= 1
                
            self.active_agents[agent_id] = abs_path
            workspace.agent_count += 1
            workspace.last_accessed = datetime.now()
            workspace.status = "in_use"
            
            self._save_workspaces()
            self.logger.info(f"Assigned agent {agent_id} to workspace {abs_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error assigning agent to workspace: {e}")
            return False
            
    def remove_agent_from_workspace(self, agent_id: str) -> bool:
        """Remove an agent from its workspace"""
        try:
            if agent_id not in self.active_agents:
                return True
                
            workspace_path = self.active_agents[agent_id]
            if workspace_path in self.workspaces:
                self.workspaces[workspace_path].agent_count -= 1
                if self.workspaces[workspace_path].agent_count <= 0:
                    self.workspaces[workspace_path].status = "available"
                    
            del self.active_agents[agent_id]
            self._save_workspaces()
            self.logger.info(f"Removed agent {agent_id} from workspace")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing agent from workspace: {e}")
            return False
            
    def get_workspace_for_agent(self, agent_id: str) -> Optional[WorkspaceInfo]:
        """Get the workspace assigned to an agent"""
        workspace_path = self.active_agents.get(agent_id)
        if workspace_path and workspace_path in self.workspaces:
            return self.workspaces[workspace_path]
        return None
        
    def get_available_workspaces(self) -> List[WorkspaceInfo]:
        """Get list of available workspaces"""
        return [ws for ws in self.workspaces.values() if ws.status == "available"]
        
    def get_all_workspaces(self) -> List[WorkspaceInfo]:
        """Get list of all workspaces"""
        return list(self.workspaces.values())
        
    def get_workspace_context(self, workspace_path: str) -> Dict[str, Any]:
        """Get context information for a workspace"""
        try:
            abs_path = str(Path(workspace_path).resolve())
            
            if abs_path not in self.workspaces:
                return {}
                
            workspace = self.workspaces[abs_path]
            context = {
                'workspace_info': asdict(workspace),
                'current_directory': abs_path,
                'active_agents': [agent_id for agent_id, wp in self.active_agents.items() if wp == abs_path],
                'recent_files': self._get_recent_files(abs_path),
                'project_structure': self._get_project_structure(abs_path),
            }
            
            return context
            
        except Exception as e:
            self.logger.error(f"Error getting workspace context: {e}")
            return {}
            
    def _get_recent_files(self, workspace_path: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recently modified files in workspace"""
        try:
            files = []
            path_obj = Path(workspace_path)
            
            for file_path in path_obj.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    try:
                        stat = file_path.stat()
                        files.append({
                            'path': str(file_path.relative_to(path_obj)),
                            'modified': datetime.fromtimestamp(stat.st_mtime),
                            'size': stat.st_size
                        })
                    except Exception:
                        continue
                        
            # Sort by modification time and return most recent            files.sort(key=lambda x: x['modified'], reverse=True)
            return files[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting recent files: {e}")
            return []
            
    def _get_project_structure(self, workspace_path: str, max_depth: int = 3) -> Dict[str, Any]:
        """Get project structure overview"""
        try:
            path_obj = Path(workspace_path)
            
            def build_tree(current_path: Path, current_depth: int = 0) -> Union[Dict[str, Any], str]:
                if current_depth >= max_depth:
                    return "..."
                    
                result: Dict[str, Any] = {}
                try:
                    for item in current_path.iterdir():
                        if item.name.startswith('.'):
                            continue
                            
                        if item.is_dir():
                            result[f"{item.name}/"] = build_tree(item, current_depth + 1)
                        else:
                            result[item.name] = "file"
                except Exception:
                    pass
                    
                return result
                
            structure = build_tree(path_obj)
            return structure if isinstance(structure, dict) else {}
            
        except Exception as e:
            self.logger.error(f"Error getting project structure: {e}")
            return {}
            
    def start_monitoring(self):
        """Start monitoring workspaces for changes"""
        if self._monitor_thread is None or not self._monitor_thread.is_alive():
            self._stop_monitoring = False
            self._monitor_thread = threading.Thread(target=self._monitor_workspaces)
            self._monitor_thread.daemon = True
            self._monitor_thread.start()
            self.logger.info("Started workspace monitoring")
            
    def stop_monitoring(self):
        """Stop monitoring workspaces"""
        self._stop_monitoring = True
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5)
        self.logger.info("Stopped workspace monitoring")
        
    def _monitor_workspaces(self):
        """Monitor workspaces for changes"""
        while not self._stop_monitoring:
            try:
                for workspace_path, workspace in list(self.workspaces.items()):
                    if not Path(workspace_path).exists():
                        self.logger.warning(f"Workspace path no longer exists: {workspace_path}")
                        workspace.status = "error"
                    elif workspace.status == "error" and Path(workspace_path).exists():
                        workspace.status = "available"
                        
                # Save any changes
                self._save_workspaces()
                
                # Sleep for a bit
                time.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error in workspace monitoring: {e}")
                time.sleep(60)
                
    def get_optimal_workspace(self, task_type: Optional[str] = None, language: Optional[str] = None) -> Optional[WorkspaceInfo]:
        """Get the optimal workspace for a given task"""
        available = self.get_available_workspaces()
        
        if not available:
            return None
            
        # Filter by task requirements
        candidates = available
        
        if language:
            candidates = [ws for ws in candidates if ws.language == language]
            
        if task_type:
            candidates = [ws for ws in candidates if ws.type == task_type]
            
        # If no exact matches, fall back to available workspaces
        if not candidates:
            candidates = available
              # Sort by last accessed time (prefer recently used)
        candidates.sort(key=lambda x: x.last_accessed or datetime.min, reverse=True)
        
        return candidates[0] if candidates else None
        
    def cleanup(self):
        """Cleanup resources"""
        self.stop_monitoring()
        self._save_workspaces()
