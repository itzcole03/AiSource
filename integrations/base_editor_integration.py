"""
Unified Editor Integration Base Class
Provides identical capabilities for both Void Editor and VS Code Insiders
"""

import os
import json
import asyncio
import logging
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import websockets
import aiofiles
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from abc import ABC, abstractmethod

class EditorFileHandler(FileSystemEventHandler):
    """File system event handler for editor workspace changes"""
    
    def __init__(self, editor_integration):
        self.editor = editor_integration
    
    def on_modified(self, event):
        if not event.is_directory:
            asyncio.create_task(self.editor.handle_file_changed(event.src_path))
    
    def on_created(self, event):
        if not event.is_directory:
            asyncio.create_task(self.editor.handle_file_created(event.src_path))
    
    def on_deleted(self, event):
        if not event.is_directory:
            asyncio.create_task(self.editor.handle_file_deleted(event.src_path))

class BaseEditorIntegration(ABC):
    """Base class providing identical capabilities for all supported editors"""
    
    def __init__(self, workspace_path: str, config: Dict):
        self.workspace_path = Path(workspace_path)
        self.config = config
        self.logger = logging.getLogger(f"{self.editor_name}Integration")
        
        # Core capabilities (identical for all editors)
        self.websocket_port = config.get('websocket_port', 8765)
        self.websocket_server = None
        self.connected_clients = set()
        
        # AI Integration capabilities
        self.ai_assistance_enabled = config.get('ai_assistance', True)
        self.real_time_collaboration = config.get('real_time_collaboration', True)
        self.code_completion = config.get('code_completion', True)
        self.code_explanation = config.get('code_explanation', True)
        self.code_refactoring = config.get('code_refactoring', True)
        self.error_detection = config.get('error_detection', True)
        self.documentation_generation = config.get('documentation_generation', True)
        
        # Advanced features (identical for all editors)
        self.swarm_automation = config.get('swarm_automation', True)
        self.multi_agent_coordination = config.get('multi_agent_coordination', True)
        self.project_analysis = config.get('project_analysis', True)
        self.architecture_suggestions = config.get('architecture_suggestions', True)
        self.performance_optimization = config.get('performance_optimization', True)
        self.security_analysis = config.get('security_analysis', True)
        
        # File watching for workspace changes
        self.file_observer = None
        self.file_handler = EditorFileHandler(self)
        
        # Workspace state tracking (identical for all editors)
        self.workspace_state = {
            'open_files': {},
            'recent_changes': [],
            'active_projects': [],
            'git_status': {},
            'ai_tasks': [],
            'agent_sessions': {},
            'code_context': {},
            'project_structure': {},
            'dependencies': {},
            'test_coverage': {},
            'performance_metrics': {}
        }
        
        # Agent integration
        self.agent_manager = None
        self.llm_manager = None
        
        # Event handlers
        self.event_handlers = {
            'file_changed': [],
            'file_created': [],
            'file_deleted': [],
            'code_completion_request': [],
            'ai_assistance_request': [],
            'refactor_request': [],
            'explanation_request': [],
            'documentation_request': [],
            'architecture_analysis': [],
            'performance_analysis': [],
            'security_analysis': []
        }
    
    @property
    @abstractmethod
    def editor_name(self) -> str:
        """Return the name of the editor"""
        pass
    
    @abstractmethod
    async def detect_editor(self) -> bool:
        """Detect if the editor is installed and available"""
        pass
    
    @abstractmethod
    async def launch_editor(self) -> bool:
        """Launch the editor with workspace"""
        pass
    
    @abstractmethod
    def get_editor_specific_config(self) -> Dict:
        """Get editor-specific configuration"""
        pass
    
    async def initialize(self):
        """Initialize the editor integration with full capabilities"""
        try:
            self.logger.info(f"Initializing {self.editor_name} integration...")
            
            # Detect editor installation
            if not await self.detect_editor():
                self.logger.warning(f"{self.editor_name} not detected, integration disabled")
                return False
            
            # Start WebSocket server for real-time communication
            await self.start_websocket_server()
            
            # Initialize file watching
            await self.start_file_watching()
            
            # Initialize workspace analysis
            await self.analyze_workspace()
            
            # Set up AI agent connections
            await self.setup_agent_connections()
            
            self.logger.info(f"{self.editor_name} integration initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize {self.editor_name} integration: {e}")
            return False
    
    async def start_websocket_server(self):
        """Start WebSocket server for real-time communication"""
        try:
            self.websocket_server = await websockets.serve(
                self.handle_websocket_connection,
                "localhost",
                self.websocket_port
            )
            self.logger.info(f"WebSocket server started on port {self.websocket_port}")
        except Exception as e:
            self.logger.error(f"Failed to start WebSocket server: {e}")
    
    async def handle_websocket_connection(self, websocket, path):
        """Handle WebSocket connections from editor"""
        self.connected_clients.add(websocket)
        self.logger.info(f"New {self.editor_name} client connected")
        
        try:
            async for message in websocket:
                await self.process_websocket_message(json.loads(message))
        except websockets.exceptions.ConnectionClosed:
            self.logger.info(f"{self.editor_name} client disconnected")
        finally:
            self.connected_clients.discard(websocket)
    
    async def process_websocket_message(self, message: Dict):
        """Process incoming WebSocket messages"""
        message_type = message.get('type')
        
        if message_type == 'file_sync':
            await self.handle_file_sync(message['data'])
        elif message_type == 'ai_request':
            await self.handle_ai_request(message['data'])
        elif message_type == 'code_completion':
            await self.handle_code_completion(message['data'])
        elif message_type == 'refactor_request':
            await self.handle_refactor_request(message['data'])
        elif message_type == 'explanation_request':
            await self.handle_explanation_request(message['data'])
        elif message_type == 'documentation_request':
            await self.handle_documentation_request(message['data'])
        elif message_type == 'architecture_analysis':
            await self.handle_architecture_analysis(message['data'])
        elif message_type == 'performance_analysis':
            await self.handle_performance_analysis(message['data'])
        elif message_type == 'security_analysis':
            await self.handle_security_analysis(message['data'])
        else:
            self.logger.warning(f"Unknown message type: {message_type}")
    
    async def start_file_watching(self):
        """Start file system watching for workspace changes"""
        if self.workspace_path.exists():
            self.file_observer = Observer()
            self.file_observer.schedule(
                self.file_handler,
                str(self.workspace_path),
                recursive=True
            )
            self.file_observer.start()
            self.logger.info("File watching started")
    
    async def analyze_workspace(self):
        """Analyze workspace structure and content"""
        try:
            # Analyze project structure
            self.workspace_state['project_structure'] = await self.get_project_structure()
            
            # Detect project type and frameworks
            self.workspace_state['project_type'] = await self.detect_project_type()
            
            # Analyze dependencies
            self.workspace_state['dependencies'] = await self.analyze_dependencies()
            
            # Get Git status
            self.workspace_state['git_status'] = await self.get_git_status()
            
            self.logger.info("Workspace analysis completed")
            
        except Exception as e:
            self.logger.error(f"Workspace analysis failed: {e}")
    
    async def setup_agent_connections(self):
        """Set up connections to AI agents"""
        try:
            # This will be set by the system manager
            self.logger.info("Agent connections ready")
        except Exception as e:
            self.logger.error(f"Failed to setup agent connections: {e}")
    
    # File handling methods (identical for all editors)
    async def handle_file_changed(self, file_path: str):
        """Handle file modification events"""
        try:
            relative_path = str(Path(file_path).relative_to(self.workspace_path))
            
            # Update workspace state
            self.workspace_state['recent_changes'].append({
                'type': 'modified',
                'file': relative_path,
                'timestamp': asyncio.get_event_loop().time()
            })
            
            # Trigger AI analysis if enabled
            if self.ai_assistance_enabled:
                await self.trigger_ai_analysis(file_path, 'file_changed')
            
            # Notify connected clients
            await self.broadcast_to_clients({
                'type': 'file_changed',
                'file': relative_path
            })
            
        except Exception as e:
            self.logger.error(f"Error handling file change: {e}")
    
    async def handle_file_created(self, file_path: str):
        """Handle file creation events"""
        try:
            relative_path = str(Path(file_path).relative_to(self.workspace_path))
            
            self.workspace_state['recent_changes'].append({
                'type': 'created',
                'file': relative_path,
                'timestamp': asyncio.get_event_loop().time()
            })
            
            await self.broadcast_to_clients({
                'type': 'file_created',
                'file': relative_path
            })
            
        except Exception as e:
            self.logger.error(f"Error handling file creation: {e}")
    
    async def handle_file_deleted(self, file_path: str):
        """Handle file deletion events"""
        try:
            relative_path = str(Path(file_path).relative_to(self.workspace_path))
            
            self.workspace_state['recent_changes'].append({
                'type': 'deleted',
                'file': relative_path,
                'timestamp': asyncio.get_event_loop().time()
            })
            
            await self.broadcast_to_clients({
                'type': 'file_deleted',
                'file': relative_path
            })
            
        except Exception as e:
            self.logger.error(f"Error handling file deletion: {e}")
    
    # AI assistance methods (identical for all editors)
    async def handle_ai_request(self, data: Dict):
        """Handle general AI assistance requests"""
        try:
            if not self.agent_manager:
                return
            
            agent_type = data.get('agent', 'orchestrator')
            request = data.get('request', '')
            context = data.get('context', {})
            
            # Add workspace context
            context.update({
                'workspace_path': str(self.workspace_path),
                'project_type': self.workspace_state.get('project_type'),
                'recent_changes': self.workspace_state.get('recent_changes', [])[-5:],
                'editor': self.editor_name
            })
            
            # Get agent response
            agent = self.agent_manager.get_agent(agent_type)
            if agent:
                response = await agent.process_request(request, context)
                
                await self.broadcast_to_clients({
                    'type': 'ai_response',
                    'agent': agent_type,
                    'response': response.content,
                    'suggestions': response.code_suggestions
                })
            
        except Exception as e:
            self.logger.error(f"Error handling AI request: {e}")
    
    async def handle_code_completion(self, data: Dict):
        """Handle code completion requests"""
        try:
            code = data.get('code', '')
            position = data.get('position', 0)
            language = data.get('language', 'python')
            
            if self.llm_manager:
                completion = await self.llm_manager.get_code_completion(
                    code=code,
                    position=position,
                    language=language,
                    context=self.workspace_state.get('code_context', {})
                )
                
                await self.broadcast_to_clients({
                    'type': 'code_completion',
                    'completion': completion
                })
                
        except Exception as e:
            self.logger.error(f"Error handling code completion: {e}")
    
    async def handle_refactor_request(self, data: Dict):
        """Handle code refactoring requests"""
        try:
            code = data.get('code', '')
            refactor_type = data.get('type', 'improve')
            
            if self.agent_manager:
                backend_agent = self.agent_manager.get_agent('backend')
                if backend_agent:
                    response = await backend_agent.process_request(
                        f"Refactor this code: {refactor_type}",
                        {'code': code, 'editor': self.editor_name}
                    )
                    
                    await self.broadcast_to_clients({
                        'type': 'refactor_response',
                        'original_code': code,
                        'refactored_code': response.code_suggestions[0]['content'] if response.code_suggestions else '',
                        'explanation': response.content
                    })
                    
        except Exception as e:
            self.logger.error(f"Error handling refactor request: {e}")
    
    async def handle_explanation_request(self, data: Dict):
        """Handle code explanation requests"""
        try:
            code = data.get('code', '')
            
            if self.agent_manager:
                agent = self.agent_manager.get_agent('backend')
                if agent:
                    response = await agent.process_request(
                        f"Explain this code in detail",
                        {'code': code, 'editor': self.editor_name}
                    )
                    
                    await self.broadcast_to_clients({
                        'type': 'explanation_response',
                        'code': code,
                        'explanation': response.content
                    })
                    
        except Exception as e:
            self.logger.error(f"Error handling explanation request: {e}")
    
    async def handle_documentation_request(self, data: Dict):
        """Handle documentation generation requests"""
        try:
            code = data.get('code', '')
            doc_type = data.get('type', 'docstring')
            
            if self.agent_manager:
                agent = self.agent_manager.get_agent('backend')
                if agent:
                    response = await agent.process_request(
                        f"Generate {doc_type} documentation for this code",
                        {'code': code, 'editor': self.editor_name}
                    )
                    
                    await self.broadcast_to_clients({
                        'type': 'documentation_response',
                        'code': code,
                        'documentation': response.content
                    })
                    
        except Exception as e:
            self.logger.error(f"Error handling documentation request: {e}")
    
    async def handle_architecture_analysis(self, data: Dict):
        """Handle architecture analysis requests"""
        try:
            if self.agent_manager:
                architect_agent = self.agent_manager.get_agent('architect')
                if architect_agent:
                    response = await architect_agent.process_request(
                        "Analyze the current project architecture and provide recommendations",
                        {
                            'workspace_path': str(self.workspace_path),
                            'project_structure': self.workspace_state.get('project_structure'),
                            'project_type': self.workspace_state.get('project_type'),
                            'editor': self.editor_name
                        }
                    )
                    
                    await self.broadcast_to_clients({
                        'type': 'architecture_analysis',
                        'analysis': response.content,
                        'suggestions': response.code_suggestions
                    })
                    
        except Exception as e:
            self.logger.error(f"Error handling architecture analysis: {e}")
    
    async def handle_performance_analysis(self, data: Dict):
        """Handle performance analysis requests"""
        try:
            code = data.get('code', '')
            
            if self.agent_manager:
                backend_agent = self.agent_manager.get_agent('backend')
                if backend_agent:
                    response = await backend_agent.process_request(
                        "Analyze this code for performance issues and suggest optimizations",
                        {'code': code, 'editor': self.editor_name}
                    )
                    
                    await self.broadcast_to_clients({
                        'type': 'performance_analysis',
                        'code': code,
                        'analysis': response.content,
                        'optimizations': response.code_suggestions
                    })
                    
        except Exception as e:
            self.logger.error(f"Error handling performance analysis: {e}")
    
    async def handle_security_analysis(self, data: Dict):
        """Handle security analysis requests"""
        try:
            code = data.get('code', '')
            
            if self.agent_manager:
                qa_agent = self.agent_manager.get_agent('qa')
                if qa_agent:
                    response = await qa_agent.process_request(
                        "Analyze this code for security vulnerabilities",
                        {'code': code, 'editor': self.editor_name}
                    )
                    
                    await self.broadcast_to_clients({
                        'type': 'security_analysis',
                        'code': code,
                        'analysis': response.content,
                        'vulnerabilities': response.code_suggestions
                    })
                    
        except Exception as e:
            self.logger.error(f"Error handling security analysis: {e}")
    
    # Utility methods (identical for all editors)
    async def broadcast_to_clients(self, message: Dict):
        """Broadcast message to all connected clients"""
        if self.connected_clients:
            message_str = json.dumps(message)
            await asyncio.gather(
                *[client.send(message_str) for client in self.connected_clients],
                return_exceptions=True
            )
    
    async def trigger_ai_analysis(self, file_path: str, event_type: str):
        """Trigger AI analysis based on file events"""
        # Implement automatic AI analysis based on file changes
        pass
    
    async def get_project_structure(self) -> Dict:
        """Get project structure"""
        structure = {}
        try:
            for root, dirs, files in os.walk(self.workspace_path):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv']]
                
                rel_root = os.path.relpath(root, self.workspace_path)
                if rel_root == '.':
                    rel_root = ''
                
                structure[rel_root] = {
                    'dirs': dirs,
                    'files': [f for f in files if not f.startswith('.')]
                }
        except Exception as e:
            self.logger.error(f"Error getting project structure: {e}")
        
        return structure
    
    async def detect_project_type(self) -> str:
        """Detect project type based on files"""
        try:
            if (self.workspace_path / 'package.json').exists():
                return 'javascript'
            elif (self.workspace_path / 'requirements.txt').exists() or (self.workspace_path / 'pyproject.toml').exists():
                return 'python'
            elif (self.workspace_path / 'Cargo.toml').exists():
                return 'rust'
            elif (self.workspace_path / 'go.mod').exists():
                return 'go'
            elif (self.workspace_path / 'pom.xml').exists():
                return 'java'
            else:
                return 'unknown'
        except Exception as e:
            self.logger.error(f"Error detecting project type: {e}")
            return 'unknown'
    
    async def analyze_dependencies(self) -> Dict:
        """Analyze project dependencies"""
        dependencies = {}
        try:
            # Python
            if (self.workspace_path / 'requirements.txt').exists():
                async with aiofiles.open(self.workspace_path / 'requirements.txt', 'r') as f:
                    content = await f.read()
                    dependencies['python'] = [line.strip() for line in content.split('\n') if line.strip()]
            
            # JavaScript
            if (self.workspace_path / 'package.json').exists():
                async with aiofiles.open(self.workspace_path / 'package.json', 'r') as f:
                    content = await f.read()
                    package_data = json.loads(content)
                    dependencies['javascript'] = {
                        'dependencies': package_data.get('dependencies', {}),
                        'devDependencies': package_data.get('devDependencies', {})
                    }
        except Exception as e:
            self.logger.error(f"Error analyzing dependencies: {e}")
        
        return dependencies
    
    async def get_git_status(self) -> Dict:
        """Get Git repository status"""
        try:
            if (self.workspace_path / '.git').exists():
                result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    cwd=self.workspace_path,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    return {
                        'is_git_repo': True,
                        'status': result.stdout.strip()
                    }
        except Exception as e:
            self.logger.error(f"Error getting git status: {e}")
        
        return {'is_git_repo': False}
    
    def set_agent_manager(self, agent_manager):
        """Set the agent manager for AI integration"""
        self.agent_manager = agent_manager
    
    def set_llm_manager(self, llm_manager):
        """Set the LLM manager for AI integration"""
        self.llm_manager = llm_manager
    
    async def cleanup(self):
        """Clean up resources"""
        try:
            if self.file_observer:
                self.file_observer.stop()
                self.file_observer.join()
            
            if self.websocket_server:
                self.websocket_server.close()
                await self.websocket_server.wait_closed()
            
            self.logger.info(f"{self.editor_name} integration cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
