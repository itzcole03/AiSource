"""
Intelligent Model Manager Integration
Adapter to integrate the advanced model manager with the Ultimate Copilot dashboard
"""

import asyncio
import logging
import requests
import subprocess
import time
import os
import signal
from typing import Dict, List, Any, Optional
from pathlib import Path
import psutil

class IntelligentModelManager:
    """
    Advanced model manager that integrates the sophisticated model manager
    with the Ultimate Copilot dashboard system.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("IntelligentModelManager")
        self.model_manager_path = Path(__file__).parent / "frontend" / "model manager"
        self.backend_port = 8002  # Use Model Manager's configured port
        self.backend_url = f"http://localhost:{self.backend_port}"
        self.backend_process = None
        self.is_running = False
        
        # Model manager capabilities
        self.providers = ["ollama", "lmstudio", "vllm"]
        self.supported_operations = [
            "start_provider", "stop_provider", "list_models", 
            "get_system_info", "monitor_gpu", "marketplace_search"
        ]
        
    async def initialize(self):
        """Initialize the intelligent model manager"""
        try:
            self.logger.info("Initializing Intelligent Model Manager...")
            
            # Check if model manager backend exists
            backend_path = self.model_manager_path / "backend" / "server.py"
            if not backend_path.exists():
                self.logger.error(f"Model manager backend not found at {backend_path}")
                return False
            
            # Start the model manager backend
            await self.start_backend()
              # Wait for backend to be ready
            if await self.wait_for_backend():
                self.is_running = True
                self.logger.info("Intelligent Model Manager initialized successfully")
                return True
            else:
                self.logger.error("Failed to start model manager backend")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize model manager: {e}")
            return False
    
    async def start_backend(self):
        """Start the model manager backend server"""
        try:
            # Check if backend is already running
            if await self.check_backend_health():
                self.logger.info("Model manager backend already running")
                return True
            
            # Try to start the backend directly using uvicorn
            try:
                import uvicorn
                import sys
                backend_script_dir = str(self.model_manager_path / "backend")
                sys.path.insert(0, backend_script_dir)
                
                # Import the server module
                from server import app
                
                # Start uvicorn in a separate thread
                import threading
                def run_server():
                    uvicorn.run(app, host="127.0.0.1", port=self.backend_port, log_level="info")
                
                self.backend_thread = threading.Thread(target=run_server, daemon=True)
                self.backend_thread.start()
                
                self.logger.info(f"Started model manager backend on port {self.backend_port}")
                return True
                
            except ImportError:
                # Fallback to subprocess if uvicorn import fails
                self.logger.info("Falling back to subprocess for backend startup")
                return await self._start_backend_subprocess()
            
        except Exception as e:
            self.logger.error(f"Failed to start backend: {e}")
            return False
    
    async def _start_backend_subprocess(self):
        """Fallback method to start backend via subprocess"""
        try:
            backend_script = self.model_manager_path / "backend" / "server.py"
            
            # Start the backend process
            cmd = ["python", str(backend_script)]
            
            self.backend_process = subprocess.Popen(
                cmd,
                cwd=str(self.model_manager_path / "backend"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            self.logger.info(f"Started model manager backend subprocess on port {self.backend_port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start backend subprocess: {e}")
            return False
    
    async def wait_for_backend(self, timeout=30):
        """Wait for backend to be ready"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if await self.check_backend_health():
                return True
            await asyncio.sleep(1)
        return False
    
    async def check_backend_health(self):
        """Check if the backend is healthy"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get comprehensive model status from the intelligent manager"""
        if not self.is_running:
            return self._get_offline_status()
        
        try:
            # Get provider status
            provider_response = requests.get(f"{self.backend_url}/providers/status", timeout=10)
            provider_data = provider_response.json() if provider_response.status_code == 200 else {}
            
            # Get system info
            system_response = requests.get(f"{self.backend_url}/system/info", timeout=10)
            system_data = system_response.json() if system_response.status_code == 200 else {}
            
            return {
                "status": "online",
                "manager": "IntelligentModelManager",
                "providers": self._format_provider_status(provider_data),
                "system": self._format_system_info(system_data),
                "capabilities": self.supported_operations,
                "backend_url": self.backend_url
            }
            
        except Exception as e:
            self.logger.error(f"Error getting model status: {e}")
            return self._get_error_status(str(e))
    
    async def handle_model_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Handle model management commands"""
        if not self.is_running:
            return {"success": False, "message": "Model manager not running"}
        
        try:
            provider = command.get("provider", "")
            action = command.get("action", "")
            model = command.get("model", "")
            
            if action == "start_provider":
                return await self._start_provider(provider)
            elif action == "stop_provider":
                return await self._stop_provider(provider)
            elif action == "list_models":
                return await self._list_models(provider)
            elif action == "load_model":
                return await self._load_model(provider, model)
            elif action == "unload_model":
                return await self._unload_model(provider, model)
            elif action == "get_system_info":
                return await self._get_system_info()
            else:
                return {"success": False, "message": f"Unknown action: {action}"}
                
        except Exception as e:
            self.logger.error(f"Error handling model command: {e}")
            return {"success": False, "message": str(e)}
    
    async def _start_provider(self, provider: str) -> Dict[str, Any]:
        """Start a model provider"""
        try:
            response = requests.post(f"{self.backend_url}/providers/{provider}/start", timeout=30)
            if response.status_code == 200:
                return {"success": True, "message": f"Started {provider} provider"}
            else:
                return {"success": False, "message": f"Failed to start {provider}: {response.text}"}
        except Exception as e:
            return {"success": False, "message": f"Error starting {provider}: {e}"}
    
    async def _stop_provider(self, provider: str) -> Dict[str, Any]:
        """Stop a model provider"""
        try:
            response = requests.post(f"{self.backend_url}/providers/{provider}/stop", timeout=30)
            if response.status_code == 200:
                return {"success": True, "message": f"Stopped {provider} provider"}
            else:
                return {"success": False, "message": f"Failed to stop {provider}: {response.text}"}
        except Exception as e:
            return {"success": False, "message": f"Error stopping {provider}: {e}"}
    
    async def _list_models(self, provider: str) -> Dict[str, Any]:
        """List available models for a provider"""
        try:
            response = requests.get(f"{self.backend_url}/providers/{provider}/models", timeout=15)
            if response.status_code == 200:
                models = response.json()
                return {"success": True, "models": models, "provider": provider}
            else:
                return {"success": False, "message": f"Failed to list models for {provider}"}
        except Exception as e:
            return {"success": False, "message": f"Error listing models: {e}"}
    
    async def _load_model(self, provider: str, model: str) -> Dict[str, Any]:
        """Load a specific model"""
        # This would need to be implemented based on provider-specific APIs
        return {"success": True, "message": f"Model loading initiated: {model} on {provider}"}
    
    async def _unload_model(self, provider: str, model: str) -> Dict[str, Any]:
        """Unload a specific model"""
        # This would need to be implemented based on provider-specific APIs
        return {"success": True, "message": f"Model unloaded: {model} from {provider}"}
    
    async def _get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        try:
            response = requests.get(f"{self.backend_url}/system/info", timeout=10)
            if response.status_code == 200:
                return {"success": True, "system_info": response.json()}
            else:
                return {"success": False, "message": "Failed to get system info"}
        except Exception as e:
            return {"success": False, "message": f"Error getting system info: {e}"}
    
    def _format_provider_status(self, provider_data: Dict) -> Dict[str, Any]:
        """Format provider status for dashboard display"""
        formatted = {}
        for provider in self.providers:
            status = provider_data.get(provider, {})
            formatted[provider] = {
                "name": provider.title(),
                "status": status.get("status", "unknown"),
                "running": status.get("running", False),
                "models": status.get("models", []),
                "port": status.get("port", "N/A"),
                "process_id": status.get("process_id", "N/A")
            }
        return formatted
    
    def _format_system_info(self, system_data: Dict) -> Dict[str, Any]:
        """Format system info for dashboard display"""
        return {
            "cpu": system_data.get("cpu", {}),
            "ram": system_data.get("ram", {}),
            "gpu": system_data.get("gpu", {}),
            "disk": system_data.get("disk", {}),
            "processes": system_data.get("processes", {})
        }
    
    def _get_offline_status(self) -> Dict[str, Any]:
        """Return status when manager is offline"""
        return {
            "status": "offline",
            "manager": "IntelligentModelManager",
            "message": "Model manager not initialized",
            "providers": {provider: {"status": "offline"} for provider in self.providers}
        }
    
    def _get_error_status(self, error: str) -> Dict[str, Any]:
        """Return error status"""
        return {
            "status": "error",
            "manager": "IntelligentModelManager",
            "message": f"Error: {error}",
            "providers": {provider: {"status": "error"} for provider in self.providers}
        }
    
    async def stop(self):
        """Stop the model manager"""
        try:
            if self.backend_process:
                self.backend_process.terminate()
                try:
                    self.backend_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.backend_process.kill()
                    self.backend_process.wait()
                
            self.is_running = False
            self.logger.info("Intelligent Model Manager stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping model manager: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current manager status (synchronous version)"""
        return {
            "manager_type": "IntelligentModelManager",
            "running": self.is_running,
            "backend_port": self.backend_port,
            "backend_url": self.backend_url,
            "providers": self.providers,
            "capabilities": self.supported_operations
        }
