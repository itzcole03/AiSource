"""
Visual Studio Code Insiders Integration
Enables agents to integrate with VS Code Insiders as the lead dev
Inherits all capabilities from BaseEditorIntegration ensuring feature parity with Void Editor.
"""

import os
import json
import asyncio
import logging
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import websockets
import aiofiles
from .base_editor_integration import BaseEditorIntegration

class VSCodeInsidersIntegration(BaseEditorIntegration):
    """Integration with VS Code Insiders - Full feature parity with Void Editor"""
    
    def __init__(self, workspace_path: str, config: Dict):
        # Initialize with full capabilities from base class
        super().__init__(workspace_path, config)
        
        # VS Code Insiders specific properties
        self.insiders_path = self._find_insiders_path()
        self.extension_port = config.get('extension_port', 8766)  # Different port from Void
        self.insiders_process = None
        
        # VS Code specific features
        self.extension_enabled = config.get('extension_enabled', False)
        self.insiders_enabled = config.get('insiders_enabled', True)
        
        # Additional initialization for legacy compatibility
        self.vscode_insiders_path = self.insiders_path
    
    @property
    def editor_name(self) -> str:
        """Return the name of the editor"""
        return "VS Code Insiders"
    
    async def detect_editor(self) -> bool:
        """Detect if VS Code Insiders is installed and available"""
        return self.insiders_path is not None and os.path.exists(self.insiders_path)
    
    async def launch_editor(self) -> bool:
        """Launch VS Code Insiders with workspace"""
        try:
            if not self.insiders_path:
                self.logger.error("VS Code Insiders not found")
                return False
            
            # Launch VS Code Insiders with workspace
            self.insiders_process = subprocess.Popen([
                self.insiders_path,
                str(self.workspace_path),
                "--new-window"
            ])
            
            self.logger.info(f"VS Code Insiders launched with workspace: {self.workspace_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch VS Code Insiders: {e}")
            return False
    
    def get_editor_specific_config(self) -> Dict:
        """Get VS Code Insiders specific configuration"""
        return {
            'editor': 'vscode-insiders',
            'executable_path': self.insiders_path,
            'supports_extensions': True,
            'websocket_protocol': 'vscode-protocol',
            'file_associations': ['*'],  # Support all file types
            'extension_enabled': self.extension_enabled,
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
                'security_analysis': True,
                'extension_marketplace': True,
                'integrated_terminal': True,
                'git_integration': True,
                'debugging': True
            }
        }
        
    def _detect_vscode_insiders(self) -> Optional[str]:
        """Detect VS Code Insiders installation"""
        possible_paths = [
            # Windows paths
            os.path.expanduser("~/AppData/Local/Programs/Microsoft VS Code Insiders/bin/code-insiders.cmd"),
            os.path.expanduser("~/AppData/Local/Programs/Microsoft VS Code Insiders/Code - Insiders.exe"),
            "C:/Program Files/Microsoft VS Code Insiders/bin/code-insiders.cmd",
            # Alternative Windows paths
            os.path.expanduser("~/AppData/Local/Programs/Microsoft VS Code Insiders/bin/code-insiders"),
            # Linux/Mac paths (for completeness)
            "/usr/bin/code-insiders",
            "/usr/local/bin/code-insiders",
            "/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/bin/code"
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.logger.info(f"[DETECT] Found VS Code Insiders at: {path}")
                return path
        
        # Try which/where command
        try:
            result = subprocess.run(['where', 'code-insiders'], capture_output=True, text=True, shell=True)
            if result.returncode == 0 and result.stdout.strip():
                path = result.stdout.strip().split('\n')[0]
                self.logger.info(f"[DETECT] Found VS Code Insiders via where: {path}")
                return path
        except:
            pass
            
        self.logger.warning("[WARNING] VS Code Insiders not found - will use standard VS Code")
        return None
    
    def _find_insiders_path(self) -> Optional[str]:
        """Find VS Code Insiders installation path"""
        # Windows
        if os.name == "nt":
            paths = [
                os.path.expandvars("%LOCALAPPDATA%\\Programs\\Microsoft VS Code Insiders\\Code - Insiders.exe"),
                os.path.expandvars("%PROGRAMFILES%\\Microsoft VS Code Insiders\\Code - Insiders.exe"),
                os.path.expandvars("%PROGRAMFILES(X86)%\\Microsoft VS Code Insiders\\Code - Insiders.exe")
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
        
        # macOS
        elif os.name == "posix" and os.uname().sysname == "Darwin":
            insiders_path = "/Applications/Visual Studio Code - Insiders.app/Contents/Resources/app/bin/code"
            if os.path.exists(insiders_path):
                return insiders_path
        
        # Linux
        elif os.name == "posix":
            paths = [
                "/usr/bin/code-insiders",
                "/usr/local/bin/code-insiders",
                os.path.expanduser("~/.local/bin/code-insiders")
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
        
        return None
    
    async def install_extension(self, extension_id: str) -> bool:
        """Install a VS Code extension"""
        try:
            if not self.insiders_path:
                return False
            
            result = subprocess.run([
                self.insiders_path,
                "--install-extension", extension_id,
                "--force"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                self.logger.info(f"Extension {extension_id} installed successfully")
                return True
            else:
                self.logger.error(f"Failed to install extension {extension_id}: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error installing extension {extension_id}: {e}")
            return False
    
    async def cleanup(self):
        """Clean up VS Code Insiders specific resources"""
        try:
            # Close VS Code Insiders process if we launched it
            if self.insiders_process and self.insiders_process.poll() is None:
                self.insiders_process.terminate()
                self.insiders_process.wait(timeout=5)
        except Exception as e:
            self.logger.error(f"Error closing VS Code Insiders: {e}")
        
        # Call parent cleanup
        await super().cleanup()

    async def start(self):
        """Start the VS Code Insiders integration services"""
        self.logger.info("[START] Starting VS Code Insiders integration services...")
        
        try:
            # Check if VS Code Insiders is available
            if not self.insiders_path:
                self.logger.warning("[WARNING] VS Code Insiders not found, using fallback mode")
            
            # Initialize lead dev mode
            if self.lead_dev_mode:
                await self.initialize_lead_dev_mode()
            
            # Start workspace monitoring
            await self.start_workspace_monitoring()
            
            # Scan workspace on start
            await self.scan_workspace()
            
            # Update git status
            await self.update_git_status()
            
            # Start WebSocket server for extension communication
            if self.config.get('websocket_enabled', True):
                await self.start_websocket_server()
            
            # Start file watcher
            await self.start_file_watcher()
            
            self.logger.info("[OK] VS Code Insiders integration services started")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Failed to start VS Code Insiders integration: {e}")
            # Don't raise - allow system to continue
    
    async def initialize_lead_dev_mode(self):
        """Initialize lead developer mode for swarm coordination"""
        self.logger.info("[LEAD] Initializing lead developer mode...")
        
        # Set up lead dev workspace
        self.workspace_state['dev_session'] = {
            'session_id': f"lead_dev_{asyncio.get_event_loop().time()}",
            'start_time': asyncio.get_event_loop().time(),
            'mode': 'lead_developer',
            'swarm_coordination': True,
            'automation_level': 'high'
        }
        
        # Create swarm coordination structure
        swarm_dir = self.workspace_path / '.swarm'
        swarm_dir.mkdir(exist_ok=True)
        
        # Initialize task queue
        self.workspace_state['swarm_tasks'] = []
        
        self.logger.info("[LEAD] Lead developer mode initialized")
    
    async def start_workspace_monitoring(self):
        """Start monitoring workspace for swarm automation"""
        self.logger.info("[MONITOR] Starting workspace monitoring...")
        
        # Monitor for project changes that need swarm attention
        # This would include watching for:
        # - New feature requests
        # - Bug reports
        # - Code review requests
        # - Build failures
        # - Test failures
        
        pass
        
        self.logger.info("✅ VS Code integration services started")

    async def initialize(self):
        """Initialize VS Code integration"""
        self.logger.info("Initializing VS Code integration...")
        
        # Validate workspace
        if not self.workspace_path.exists():
            raise ValueError(f"Workspace path does not exist: {self.workspace_path}")
        
        # Start WebSocket server for VS Code extension
        await self.start_websocket_server()
        
        # Setup file watching
        self.setup_file_watcher()
        
        # Scan initial workspace state
        await self.scan_workspace()
        
        self.logger.info("VS Code integration initialized")
    
    async def start_websocket_server(self):
        """Start WebSocket server for VS Code extension communication"""
        async def handle_client(websocket, path):
            self.connected_clients.add(websocket)
            self.logger.info(f"VS Code extension connected: {websocket.remote_address}")
            
            try:
                async for message in websocket:
                    await self.handle_extension_message(websocket, message)
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self.connected_clients.discard(websocket)
                self.logger.info("VS Code extension disconnected")
        
        self.websocket_server = await websockets.serve(
            handle_client, 
            "localhost", 
            self.extension_port
        )
        
        self.logger.info(f"WebSocket server started on port {self.extension_port}")
    
    async def handle_extension_message(self, websocket, message):
        """Handle messages from VS Code extension"""
        try:
            data = json.loads(message)
            command = data.get('command')
            
            if command == 'file_opened':
                await self.handle_file_opened(data)
            elif command == 'file_changed':
                await self.handle_file_changed(data)
            elif command == 'file_saved':
                await self.handle_file_saved(data)
            elif command == 'workspace_state':
                await self.handle_workspace_state(data)
            
            # Send acknowledgment
            await websocket.send(json.dumps({'status': 'received', 'command': command}))
            
        except Exception as e:
            self.logger.error(f"Error handling extension message: {e}")
    
    def setup_file_watcher(self):
        """Setup file system watcher for workspace changes"""
        class WorkspaceFileHandler(FileSystemEventHandler):
            def __init__(self, integration):
                self.integration = integration
            
            def on_modified(self, event):
                if not event.is_directory:
                    # Use threading to safely schedule async task
                    try:
                        import threading
                        import asyncio
                        def run_async():
                            try:
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                loop.run_until_complete(self.integration.handle_file_modified(event.src_path))
                                loop.close()
                            except Exception as e:
                                print(f"Error in file watcher: {e}")
                        
                        thread = threading.Thread(target=run_async)
                        thread.daemon = True
                        thread.start()
                    except Exception as e:
                        print(f"Error setting up file watcher task: {e}")
            
            def on_created(self, event):
                if not event.is_directory:
                    try:
                        import threading
                        import asyncio
                        def run_async():
                            try:
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                loop.run_until_complete(self.integration.handle_file_created(event.src_path))
                                loop.close()
                            except Exception as e:
                                print(f"Error in file watcher: {e}")
                        
                        thread = threading.Thread(target=run_async)
                        thread.daemon = True
                        thread.start()
                    except Exception as e:
                        print(f"Error setting up file watcher task: {e}")
            
            def on_deleted(self, event):
                if not event.is_directory:
                    try:
                        import threading
                        import asyncio
                        def run_async():
                            try:
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                loop.run_until_complete(self.integration.handle_file_deleted(event.src_path))
                                loop.close()
                            except Exception as e:
                                print(f"Error in file watcher: {e}")
                        
                        thread = threading.Thread(target=run_async)
                        thread.daemon = True
                        thread.start()
                    except Exception as e:
                        print(f"Error setting up file watcher task: {e}")
        
        self.file_handler = WorkspaceFileHandler(self)
        self.file_observer = Observer()
        self.file_observer.schedule(
            self.file_handler, 
            str(self.workspace_path), 
            recursive=True
        )
        self.file_observer.start()
        
        self.logger.info(f"File watcher started for: {self.workspace_path}")
    
    async def scan_workspace(self):
        """Scan workspace for initial state"""
        self.logger.info("🔍 Scanning workspace...")
        
        # Find all code files
        code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.php', '.rb'}
        
        for file_path in self.workspace_path.rglob('*'):
            if file_path.is_file() and file_path.suffix in code_extensions:
                relative_path = file_path.relative_to(self.workspace_path)
                
                # Read file content
                try:
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                    
                    self.workspace_state['open_files'][str(relative_path)] = {
                        'content': content,
                        'language': self.detect_language(file_path.suffix),
                        'size': len(content),
                        'last_modified': file_path.stat().st_mtime
                    }
                except Exception as e:
                    self.logger.warning(f"Could not read file {file_path}: {e}")
        
        # Get git status if available
        await self.update_git_status()
        
        self.logger.info(f"Workspace scan complete: {len(self.workspace_state['open_files'])} files found")
    
    async def read_file(self, file_path: str) -> Optional[str]:
        """Read file content from workspace"""
        try:
            full_path = self.workspace_path / file_path
            
            if not full_path.exists():
                return None
            
            async with aiofiles.open(full_path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Update workspace state
            relative_path = str(Path(file_path))
            self.workspace_state['open_files'][relative_path] = {
                'content': content,
                'language': self.detect_language(full_path.suffix),
                'size': len(content),
                'last_modified': full_path.stat().st_mtime
            }
            
            return content
            
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    async def write_file(self, file_path: str, content: str, create_backup: bool = True) -> bool:
        """Write content to file in workspace"""
        try:
            full_path = self.workspace_path / file_path
            
            # Create backup if file exists
            if create_backup and full_path.exists():
                backup_path = full_path.with_suffix(full_path.suffix + '.backup')
                async with aiofiles.open(full_path, 'r', encoding='utf-8') as src:
                    backup_content = await src.read()
                async with aiofiles.open(backup_path, 'w', encoding='utf-8') as dst:
                    await dst.write(backup_content)
            
            # Ensure directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write new content
            async with aiofiles.open(full_path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            # Update workspace state
            relative_path = str(Path(file_path))
            self.workspace_state['open_files'][relative_path] = {
                'content': content,
                'language': self.detect_language(full_path.suffix),
                'size': len(content),
                'last_modified': full_path.stat().st_mtime
            }
            
            # Notify VS Code extension
            await self.notify_extension('file_updated', {
                'file_path': file_path,
                'content': content
            })
            
            self.logger.info(f"File written: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error writing file {file_path}: {e}")
            return False
    
    async def create_file(self, file_path: str, content: str = "") -> bool:
        """Create new file in workspace"""
        full_path = self.workspace_path / file_path
        
        if full_path.exists():
            self.logger.warning(f"File already exists: {file_path}")
            return False
        
        return await self.write_file(file_path, content, create_backup=False)
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file from workspace"""
        try:
            full_path = self.workspace_path / file_path
            
            if not full_path.exists():
                return False
            
            full_path.unlink()
            
            # Remove from workspace state
            relative_path = str(Path(file_path))
            self.workspace_state['open_files'].pop(relative_path, None)
            
            # Notify VS Code extension
            await self.notify_extension('file_deleted', {'file_path': file_path})
            
            self.logger.info(f"File deleted: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting file {file_path}: {e}")
            return False
    
    async def list_files(self, pattern: str = "*", include_content: bool = False) -> List[Dict]:
        """List files in workspace matching pattern"""
        files = []
        
        for file_path in self.workspace_path.rglob(pattern):
            if file_path.is_file():
                relative_path = file_path.relative_to(self.workspace_path)
                
                file_info = {
                    'path': str(relative_path),
                    'size': file_path.stat().st_size,
                    'modified': file_path.stat().st_mtime,
                    'language': self.detect_language(file_path.suffix)
                }
                
                if include_content:
                    try:
                        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                            file_info['content'] = await f.read()
                    except:
                        file_info['content'] = None
                
                files.append(file_info)
        
        return files
    
    async def search_in_files(self, query: str, file_pattern: str = "*.py") -> List[Dict]:
        """Search for text in workspace files"""
        results = []
        
        for file_path in self.workspace_path.rglob(file_pattern):
            if file_path.is_file():
                try:
                    async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                        content = await f.read()
                    
                    lines = content.split('\n')
                    for line_num, line in enumerate(lines, 1):
                        if query.lower() in line.lower():
                            results.append({
                                'file': str(file_path.relative_to(self.workspace_path)),
                                'line': line_num,
                                'content': line.strip(),
                                'context': lines[max(0, line_num-2):line_num+2]
                            })
                except:
                    continue
        
        return results
    
    async def get_git_status(self) -> Dict:
        """Get git status of workspace"""
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.workspace_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                status = {}
                for line in result.stdout.strip().split('\n'):
                    if line:
                        status_code = line[:2]
                        file_path = line[3:]
                        status[file_path] = status_code
                
                return status
            
        except Exception as e:
            self.logger.warning(f"Could not get git status: {e}")
        
        return {}
    
    async def update_git_status(self):
        """Update git status in workspace state"""
        self.workspace_state['git_status'] = await self.get_git_status()
    
    def detect_language(self, extension: str) -> str:
        """Detect programming language from file extension"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
            '.rb': 'ruby',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown'
        }
        
        return language_map.get(extension.lower(), 'text')
    
    async def notify_extension(self, event_type: str, data: Dict):
        """Notify VS Code extension of events"""
        if not self.connected_clients:
            return
        
        message = json.dumps({
            'type': event_type,
            'data': data,
            'timestamp': asyncio.get_event_loop().time()
        })
        
        # Send to all connected clients
        disconnected = set()
        for client in self.connected_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
        
        # Remove disconnected clients
        self.connected_clients -= disconnected
    
    async def handle_file_opened(self, data):
        """Handle file opened event from VS Code"""
        file_path = data.get('file_path')
        if file_path:
            content = await self.read_file(file_path)
            self.workspace_state['recent_changes'].append({
                'type': 'opened',
                'file': file_path,
                'timestamp': asyncio.get_event_loop().time()
            })
    
    async def handle_file_changed(self, data):
        """Handle file changed event from VS Code"""
        file_path = data.get('file_path')
        content = data.get('content')
        
        if file_path and content is not None:
            # Update workspace state
            self.workspace_state['open_files'][file_path] = {
                'content': content,
                'language': self.detect_language(Path(file_path).suffix),
                'size': len(content),
                'last_modified': asyncio.get_event_loop().time()
            }
            
            self.workspace_state['recent_changes'].append({
                'type': 'changed',
                'file': file_path,
                'timestamp': asyncio.get_event_loop().time()
            })
    
    async def handle_file_saved(self, data):
        """Handle file saved event from VS Code"""
        file_path = data.get('file_path')
        if file_path:
            self.workspace_state['recent_changes'].append({
                'type': 'saved',
                'file': file_path,
                'timestamp': asyncio.get_event_loop().time()
            })
    
    async def handle_workspace_state(self, data):
        """Handle workspace state update from VS Code"""
        if 'open_files' in data:
            self.workspace_state['open_files'].update(data['open_files'])
    
    async def handle_file_modified(self, file_path: str):
        """Handle file modified event from file watcher"""
        relative_path = str(Path(file_path).relative_to(self.workspace_path))
        content = await self.read_file(relative_path)
        
        if content is not None:
            self.workspace_state['recent_changes'].append({
                'type': 'modified',
                'file': relative_path,
                'timestamp': asyncio.get_event_loop().time()
            })
    
    async def handle_file_created(self, file_path: str):
        """Handle file created event from file watcher"""
        relative_path = str(Path(file_path).relative_to(self.workspace_path))
        content = await self.read_file(relative_path)
        
        self.workspace_state['recent_changes'].append({
            'type': 'created',
            'file': relative_path,
            'timestamp': asyncio.get_event_loop().time()
        })
    
    async def handle_file_deleted(self, file_path: str):
        """Handle file deleted event from file watcher"""
        relative_path = str(Path(file_path).relative_to(self.workspace_path))
        
        # Remove from workspace state
        self.workspace_state['open_files'].pop(relative_path, None)
        
        self.workspace_state['recent_changes'].append({
            'type': 'deleted',
            'file': relative_path,
            'timestamp': asyncio.get_event_loop().time()
        })
    
    def get_workspace_state(self) -> Dict:
        """Get current workspace state"""
        return self.workspace_state.copy()
    
    async def stop(self):
        """Stop VS Code integration"""
        self.logger.info("🛑 Stopping VS Code integration...")
        
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
        
        if self.websocket_server:
            self.websocket_server.close()
            await self.websocket_server.wait_closed()
        
        self.logger.info("✅ VS Code integration stopped")