#!/usr/bin/env python3
"""
Dashboard Backend API Server

FastAPI backend that provides system integration and real-time data
for the Ultimate Copilot Dashboard.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import psutil
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
    WEB_AVAILABLE = True
    print("FastAPI imports successful")
except ImportError as e:
    print(f"FastAPI import failed: {e}")
    WEB_AVAILABLE = False
    FastAPI = WebSocket = HTTPException = BackgroundTasks = None
    CORSMiddleware = JSONResponse = uvicorn = None

# Try pydantic separately for better error handling
try:
    from pydantic import BaseModel
    PYDANTIC_AVAILABLE = True
    print("Pydantic imports successful")
except ImportError as e:
    print(f"Pydantic import failed: {e}")
    PYDANTIC_AVAILABLE = False
    BaseModel = None

# Update WEB_AVAILABLE to require both FastAPI and Pydantic
WEB_AVAILABLE = WEB_AVAILABLE and PYDANTIC_AVAILABLE

# System imports - make optional for testing
try:
    from core.enhanced_system_manager import EnhancedSystemManager
    from core.enhanced_llm_manager import EnhancedLLMManager
    from core.vram_manager import VRAMManager
    from core.agent_manager import AgentManager
    SYSTEM_AVAILABLE = True
except ImportError:
    SYSTEM_AVAILABLE = False
    EnhancedSystemManager = EnhancedLLMManager = VRAMManager = AgentManager = None

# Pydantic models (if available)
if WEB_AVAILABLE:
    class SystemCommandModel(BaseModel):
        action: str
        parameters: Optional[Dict[str, Any]] = None

    class ModelCommandModel(BaseModel):
        provider: str
        model: str
        action: str  # load, unload, switch

    class AgentCommandModel(BaseModel):
        agent_id: str
        action: str  # start, stop, restart, configure
        config: Optional[Dict[str, Any]] = None
else:
    # Dummy classes when Pydantic not available
    class SystemCommandModel:
        def __init__(self, action: str, parameters: Optional[Dict[str, Any]] = None):
            self.action = action
            self.parameters = parameters

    class ModelCommandModel:
        def __init__(self, provider: str, model: str, action: str):
            self.provider = provider
            self.model = model
            self.action = action

    class AgentCommandModel:
        def __init__(self, agent_id: str, action: str, config: Optional[Dict[str, Any]] = None):
            self.agent_id = agent_id
            self.action = action
            self.config = config

class DashboardBackend:
    """Backend API server for the Ultimate Copilot Dashboard"""
    
    def __init__(self):
        self.logger = logging.getLogger("DashboardBackend")
        self.app = None
        self.system_manager = None
        self.llm_manager = None
        self.vram_manager = None
        self.agent_manager = None
        self.active_websockets: List[WebSocket] = []
        
        # Basic system state for when components aren't available
        self.system_state = {
            "status": "running",
            "uptime_start": datetime.now(),
            "components": {
                "web_framework": WEB_AVAILABLE,
                "system_integration": SYSTEM_AVAILABLE,
                "vram_management": False,
                "llm_management": False,
                "agent_management": False
            }
        }
        
        if WEB_AVAILABLE:
            self.setup_fastapi()
    
    def setup_fastapi(self):
        """Setup FastAPI application and routes"""
        if not WEB_AVAILABLE:
            self.logger.error("FastAPI/Pydantic not available")
            return
            
        self.app = FastAPI(
            title="Ultimate Copilot Dashboard API",
            description="Backend API for the Ultimate Copilot Dashboard",
            version="2.0.0"
        )
        
        # Enable CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self.register_routes()
    
    def register_routes(self):
        """Register all API routes"""
        
        @self.app.get("/")
        async def root():
            """Root endpoint with API information"""
            return {"message": "Ultimate Copilot Dashboard API", "version": "2.0.0"}
        
        @self.app.get("/system/status")
        async def get_system_status():
            """Get overall system status"""
            return await self.get_system_status()
        
        @self.app.get("/system/metrics")
        async def get_system_metrics():
            """Get system performance metrics"""
            return await self.get_performance_metrics()
        
        @self.app.post("/system/control")
        async def control_system(command: SystemCommandModel):
            """Control system operations"""
            return await self.handle_system_command(command)
        
        @self.app.get("/models/status")
        async def get_model_status():
            """Get model provider status"""
            return await self.get_model_status()
        
        @self.app.post("/models/control")
        async def control_model(command: ModelCommandModel):
            """Control model operations"""
            return await self.handle_model_command(command)
        
        @self.app.get("/agents/status")
        async def get_agent_status():
            """Get agent status"""
            return await self.get_agent_status()
        
        @self.app.post("/agents/control")
        async def control_agent(command: AgentCommandModel):
            """Control agent operations"""
            return await self.handle_agent_command(command)
        
        @self.app.get("/logs")
        async def get_logs():
            """Get recent system logs"""
            return await self.get_system_logs()
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            await self.handle_websocket(websocket)
    
    async def initialize(self):
        """Initialize system components"""
        try:
            self.logger.info("Initializing Dashboard Backend...")
            
            if not SYSTEM_AVAILABLE:
                self.logger.warning("System components not available - running in basic mode")
                return
            
            # Initialize VRAM manager
            if VRAMManager:
                self.vram_manager = VRAMManager()
                self.system_state["components"]["vram_management"] = True
            
            # Initialize LLM manager
            if EnhancedLLMManager:
                self.llm_manager = EnhancedLLMManager({})  # Empty config for basic functionality
                self.system_state["components"]["llm_management"] = True
            
            # Initialize system manager
            if EnhancedSystemManager:
                self.system_manager = EnhancedSystemManager()
                self.system_state["components"]["system_integration"] = True
            
            # Initialize agent manager
            if AgentManager:
                self.agent_manager = AgentManager()
                self.system_state["components"]["agent_management"] = True
                
            self.logger.info("Backend initialization complete")
            
        except Exception as e:
            self.logger.error(f"Error during initialization: {e}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            # Basic system information
            uptime = datetime.now() - self.system_state["uptime_start"]
            
            status = {
                "status": "running",
                "uptime_seconds": uptime.total_seconds(),
                "components": self.system_state["components"],
                "timestamp": datetime.now().isoformat()
            }
            
            # Add VRAM information if available
            if self.vram_manager:
                try:
                    vram_info = self.get_basic_vram_info()
                    status["vram"] = vram_info
                except Exception as e:
                    self.logger.warning(f"Error getting VRAM info: {e}")
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_basic_vram_info(self) -> Dict[str, Any]:
        """Get basic VRAM information"""
        try:
            import subprocess
            
            # Try to get GPU info using nvidia-smi
            try:
                result = subprocess.run(
                    ["nvidia-smi", "--query-gpu=memory.total,memory.used,memory.free", "--format=csv,noheader,nounits"],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    gpus = []
                    for i, line in enumerate(lines):
                        parts = line.split(', ')
                        if len(parts) == 3:
                            total, used, free = map(int, parts)
                            gpus.append({
                                "gpu_id": i,
                                "total_mb": total,
                                "used_mb": used,
                                "free_mb": free,
                                "usage_percent": (used / total) * 100 if total > 0 else 0
                            })
                    return {"gpus": gpus, "available": True}
            except Exception:
                pass
            
            return {"available": False, "message": "NVIDIA GPU not detected or nvidia-smi not available"}
            
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            
            metrics = {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "core_count": cpu_count
                },
                "memory": {
                    "total_bytes": memory.total,
                    "used_bytes": memory.used,
                    "available_bytes": memory.available,
                    "usage_percent": memory.percent
                },
                "disk": {
                    "total_bytes": disk.total,
                    "used_bytes": disk.used,
                    "free_bytes": disk.free,
                    "usage_percent": (disk.used / disk.total) * 100
                },
                "timestamp": datetime.now().isoformat()
            }
            
            # Add LLM metrics if available
            if self.llm_manager:
                try:
                    llm_metrics = await self.get_basic_llm_metrics()
                    metrics["llm"] = llm_metrics
                except Exception as e:
                    self.logger.warning(f"Error getting LLM metrics: {e}")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    async def get_basic_llm_metrics(self) -> Dict[str, Any]:
        """Get basic LLM metrics"""
        return {
            "providers_available": 0,
            "models_loaded": 0,
            "active_sessions": 0
        }
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get model provider status"""
        try:
            if not self.llm_manager:
                return {
                    "available": False,
                    "message": "LLM Manager not available",
                    "providers": []
                }
            
            # Basic model status
            return {
                "available": True,
                "providers": [],
                "loaded_models": []
            }
            
        except Exception as e:
            self.logger.error(f"Error getting model status: {e}")
            return {"error": str(e)}
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status"""
        try:
            if not self.agent_manager:
                return {
                    "available": False,
                    "message": "Agent Manager not available",
                    "agents": []
                }
            
            # Basic agent status
            return {
                "available": True,
                "agents": [],
                "active_count": 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting agent status: {e}")
            return {"error": str(e)}
    
    async def get_system_logs(self) -> Dict[str, Any]:
        """Get recent system logs"""
        try:
            # Return basic log information
            return {
                "logs": [
                    {
                        "timestamp": datetime.now().isoformat(),
                        "level": "INFO",
                        "message": "Dashboard backend running",
                        "component": "dashboard"
                    }
                ],
                "total_count": 1
            }
            
        except Exception as e:
            self.logger.error(f"Error getting logs: {e}")
            return {"error": str(e)}
    
    async def handle_system_command(self, command: SystemCommandModel) -> Dict[str, Any]:
        """Handle system commands"""
        try:
            action = command.action
            params = command.parameters or {}
            
            self.logger.info(f"Handling system command: {action}")
            
            if action == "restart":
                return {"status": "success", "message": "System restart initiated"}
            elif action == "shutdown":
                return {"status": "success", "message": "System shutdown initiated"}
            elif action == "status":
                return await self.get_system_status()
            else:
                return {"status": "error", "message": f"Unknown action: {action}"}
                
        except Exception as e:
            self.logger.error(f"Error handling system command: {e}")
            return {"status": "error", "message": str(e)}
    
    async def handle_model_command(self, command: ModelCommandModel) -> Dict[str, Any]:
        """Handle model commands"""
        try:
            self.logger.info(f"Handling model command: {command.action} for {command.provider}/{command.model}")
            
            if not self.llm_manager:
                return {"status": "error", "message": "LLM Manager not available"}
            
            # Basic command handling
            return {
                "status": "success", 
                "message": f"Model command {command.action} processed",
                "provider": command.provider,
                "model": command.model
            }
            
        except Exception as e:
            self.logger.error(f"Error handling model command: {e}")
            return {"status": "error", "message": str(e)}
    
    async def handle_agent_command(self, command: AgentCommandModel) -> Dict[str, Any]:
        """Handle agent commands"""
        try:
            self.logger.info(f"Handling agent command: {command.action} for agent {command.agent_id}")
            
            if not self.agent_manager:
                return {"status": "error", "message": "Agent Manager not available"}
            
            # Basic command handling
            return {
                "status": "success",
                "message": f"Agent command {command.action} processed",
                "agent_id": command.agent_id
            }
            
        except Exception as e:
            self.logger.error(f"Error handling agent command: {e}")
            return {"status": "error", "message": str(e)}
    
    async def handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connections"""
        await websocket.accept()
        self.active_websockets.append(websocket)
        
        try:
            while True:
                # Send periodic updates
                await asyncio.sleep(5)
                status = await self.get_system_status()
                await websocket.send_json(status)
                
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        finally:
            if websocket in self.active_websockets:
                self.active_websockets.remove(websocket)
    
    async def start_server(self, host: str = "127.0.0.1", port: int = 8001):
        """Start the FastAPI server"""
        if not WEB_AVAILABLE:
            self.logger.error("Cannot start server - FastAPI/Pydantic not available")
            return False
            
        await self.initialize()
        
        self.logger.info(f"Starting Dashboard Backend on {host}:{port}")
        
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        
        try:
            await server.serve()
        except Exception as e:
            self.logger.error(f"Server error: {e}")
            return False
        
        return True

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dashboard Backend Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    parser.add_argument("--test", action="store_true", help="Test mode - exit after initialization")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    backend = DashboardBackend()
    
    if args.test:
        print("Testing backend initialization...")
        if WEB_AVAILABLE:
            print("✓ FastAPI and Pydantic available")
            await backend.initialize()
            print("✓ Backend initialization complete")
        else:
            print("✗ FastAPI or Pydantic not available")
        return
    
    if not WEB_AVAILABLE:
        print("Error: FastAPI and Pydantic are required but not available")
        print("Please install: pip install fastapi uvicorn pydantic")
        return
    
    await backend.start_server(host=args.host, port=args.port)

if __name__ == "__main__":
    asyncio.run(main())
