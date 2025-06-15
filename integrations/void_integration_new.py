"""
Void Editor Integration

This module provides integration with the Void Editor for the Ultimate Copilot System.
Inherits all capabilities from BaseEditorIntegration ensuring feature parity with VS Code Insiders.
"""

import os
import json
import logging
import asyncio
import subprocess
import websockets
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from .base_editor_integration import BaseEditorIntegration

logger = logging.getLogger(__name__)

class VoidEditorIntegration(BaseEditorIntegration):
    """Integration with Void Editor - Full feature parity with VS Code Insiders"""
    
    def __init__(self, workspace_path: str, config: Dict[str, Any] = None):
        # Initialize with full capabilities from base class
        super().__init__(workspace_path, config or {})
        
        # Void Editor specific properties
        self.void_path = self._find_void_path()
        self.void_process = None
    
    @property
    def editor_name(self) -> str:
        """Return the name of the editor"""
        return "Void"
    
    async def detect_editor(self) -> bool:
        """Detect if Void Editor is installed and available"""
        return self.void_path is not None and os.path.exists(self.void_path)
    
    async def launch_editor(self) -> bool:
        """Launch Void Editor with workspace"""
        try:
            if not self.void_path:
                self.logger.error("Void Editor not found")
                return False
            
            # Launch Void Editor with workspace
            self.void_process = subprocess.Popen([
                self.void_path,
                str(self.workspace_path)
            ])
            
            self.logger.info(f"Void Editor launched with workspace: {self.workspace_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch Void Editor: {e}")
            return False
    
    def get_editor_specific_config(self) -> Dict:
        """Get Void Editor specific configuration"""
        return {
            'editor': 'void',
            'executable_path': self.void_path,
            'supports_extensions': False,  # Void doesn't have extensions like VS Code
            'websocket_protocol': 'void-protocol',
            'file_associations': ['*'],  # Support all file types
            'features': {
                'ai_assistance': True,
                'real_time_collaboration': True,
                'code_completion': True,
                'code_explanation': True,
                'code_refactoring': True,
                'error_detection': True,
                'documentation_generation': True,
                'swarm_automation': True,
                'multi_agent_coordination': True,
                'project_analysis': True,
                'architecture_suggestions': True,
                'performance_optimization': True,
                'security_analysis': True
            }
        }
    
    def _find_void_path(self) -> Optional[str]:
        """Find the Void Editor installation path"""
        # Windows
        if os.name == "nt":
            # Check common installation paths
            paths = [
                os.path.expandvars("%LOCALAPPDATA%\\Programs\\Void\\Void.exe"),
                os.path.expandvars("%PROGRAMFILES%\\Void\\Void.exe"),
                os.path.expandvars("%PROGRAMFILES(X86)%\\Void\\Void.exe")
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
        
        # macOS
        elif os.name == "posix" and os.uname().sysname == "Darwin":
            void_path = "/Applications/Void.app/Contents/MacOS/Void"
            if os.path.exists(void_path):
                return void_path
        
        # Linux
        elif os.name == "posix":
            paths = [
                os.path.expanduser("~/.local/share/void/Void"),
                "/usr/bin/void",
                "/usr/local/bin/void",
                "/opt/void/Void"
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
        
        return None
    
    async def cleanup(self):
        """Clean up Void Editor specific resources"""
        try:
            # Close Void Editor process if we launched it
            if self.void_process and self.void_process.poll() is None:
                self.void_process.terminate()
                self.void_process.wait(timeout=5)
        except Exception as e:
            self.logger.error(f"Error closing Void Editor: {e}")
        
        # Call parent cleanup
        await super().cleanup()
