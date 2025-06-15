#!/usr/bin/env python3
"""
Dashboard Backend API Server

FastAPI backend that provides system integration and real-time data
for the Ultimate Copilot Das        @self.app.post("/system/control")
        async def control_system(command: SystemCommandModel):
            """Control system operations"""
            return await self.handle_system_command(command)rd.
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

# System imports
try:
    from core.enhanced_system_manager import EnhancedSystemManager
    from core.enhanced_llm_manager import EnhancedLLMManager
    from core.vram_manager import VRAMManager
    from core.agent_manager import AgentManager
    SYSTEM_AVAILABLE = True
except ImportError:
    SYSTEM_AVAILABLE = False
    EnhancedSystemManager = EnhancedLLMManager = VRAMManager = AgentManager = None

# Data models
class SystemCommand:
    """System command data structure"""
    def __init__(self, action: str, parameters: Optional[Dict[str, Any]] = None):
        self.action = action
        self.parameters = parameters or {}

class ModelCommand:
    """Model command data structure"""
    def __init__(self, provider: str, model: str, action: str):
        self.provider = provider
        self.model = model
        self.action = action

class AgentCommand:
    """Agent command data structure"""
    def __init__(self, agent_id: str, action: str, config: Optional[Dict[str, Any]] = None):
        self.agent_id = agent_id
        self.action = action
        self.config = config or {}

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

class DashboardBackend:
    """Backend API server for the Ultimate Copilot Dashboard"""
    
    def __init__(self):
        self.logger = logging.getLogger("DashboardBackend")
        self.app = None
        self.system_manager = None
        self.llm_manager = None
        self.vram_manager = None
        self.agent_manager = None
        
        # WebSocket connections for real-time updates
        self.websocket_connections = []
        
        # System state
        self.system_state = {
            "status": "initializing",
            "uptime_start": datetime.now(),
            "metrics": {},
            "last_update": datetime.now()
        }
        
        # Plugin registry
        self.plugins = {}
        
        if WEB_AVAILABLE:
            self.setup_fastapi()
    
    def setup_fastapi(self):
        """Setup FastAPI application"""
        self.app = FastAPI(
            title="Ultimate Copilot Dashboard API",
            description="Backend API for the Ultimate Copilot Dashboard",
            version="2.0.0"
        )
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self.setup_routes()
    
    def setup_routes(self):
        """Setup API routes"""
        
        @self.app.get("/")
        async def root():
            return {"message": "Ultimate Copilot Dashboard API", "status": "running"}
        
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
                self.logger.warning("System components not available")
                self.system_state["status"] = "limited"
                return True
            
            # Initialize VRAM manager
            self.vram_manager = VRAMManager()
            await self.vram_manager.initialize()
            
            # Initialize LLM manager
            self.llm_manager = EnhancedLLMManager()
            await self.llm_manager.initialize()
            
            # Initialize system manager
            self.system_manager = EnhancedSystemManager()
            await self.system_manager.initialize()
            
            # Initialize agent manager
            self.agent_manager = AgentManager()
            
            self.system_state["status"] = "running"
            self.logger.info("Dashboard Backend initialized successfully")
            
            # Start background monitoring
            asyncio.create_task(self.monitor_system())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize backend: {e}")
            self.system_state["status"] = "error"
            return False
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Calculate uptime
            uptime = datetime.now() - self.system_state["uptime_start"]
            uptime_str = str(uptime).split('.')[0]  # Remove microseconds
            
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get VRAM info
            vram_info = {}
            if self.vram_manager:
                vram_info = await self.vram_manager.get_current_usage()
            
            # Check component status
            components = {
                "system_manager": self.system_manager is not None,
                "llm_manager": self.llm_manager is not None,
                "vram_manager": self.vram_manager is not None,
                "agent_manager": self.agent_manager is not None
            }
            
            return {
                "status": self.system_state["status"],
                "uptime": uptime_str,
                "timestamp": datetime.now().isoformat(),
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory": {
                        "total": memory.total,
                        "available": memory.available,
                        "percent": memory.percent,
                        "used": memory.used
                    },
                    "disk": {
                        "total": disk.total,
                        "free": disk.free,
                        "used": disk.used,
                        "percent": (disk.used / disk.total) * 100
                    }
                },
                "vram": vram_info,
                "components": components,
                "active_connections": len(self.websocket_connections)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        try:
            metrics = {
                "requests_total": getattr(self, 'requests_total', 0),
                "requests_per_minute": getattr(self, 'requests_per_minute', 0),
                "average_response_time": getattr(self, 'avg_response_time', 0.0),
                "error_rate": getattr(self, 'error_rate', 0.0),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add LLM manager metrics
            if self.llm_manager:
                llm_metrics = await self.llm_manager.get_performance_metrics()
                metrics.update(llm_metrics)
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {e}")
            return {"error": str(e)}
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get model provider status"""
        try:
            if not self.llm_manager:
                return {"error": "LLM manager not available"}
            
            return await self.llm_manager.get_provider_status()
            
        except Exception as e:
            self.logger.error(f"Error getting model status: {e}")
            return {"error": str(e)}
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get agent status"""
        try:
            if not self.agent_manager:
                return {"agents": [], "status": "agent_manager_unavailable"}
            
            return await self.agent_manager.get_status()
            
        except Exception as e:
            self.logger.error(f"Error getting agent status: {e}")
            return {"error": str(e)}
    
    async def get_system_logs(self) -> Dict[str, Any]:
        """Get recent system logs"""
        try:
            # Get recent log entries (implement based on your logging system)
            logs = []
            
            # Try to read from log files
            log_file = Path("logs/system.log")
            if log_file.exists():
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    logs = [line.strip() for line in lines[-100:]]  # Last 100 lines
            
            return {
                "logs": logs,
                "count": len(logs),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting logs: {e}")
            return {"error": str(e)}
    
    async def handle_system_command(self, command: SystemCommandModel) -> Dict[str, Any]:
        """Handle system control commands"""
        try:
            action = command.action
            params = command.parameters or {}
            
            if action == "restart":
                # Restart system components
                await self.restart_system()
                return {"status": "success", "message": "System restart initiated"}
            
            elif action == "shutdown":
                # Graceful shutdown
                await self.shutdown_system()
                return {"status": "success", "message": "System shutdown initiated"}
            
            elif action == "reload_config":
                # Reload configuration
                await self.reload_configuration()
                return {"status": "success", "message": "Configuration reloaded"}
            
            else:
                return {"status": "error", "message": f"Unknown action: {action}"}
            
        except Exception as e:
            self.logger.error(f"Error handling system command: {e}")
            return {"status": "error", "message": str(e)}
    
    async def handle_model_command(self, command: ModelCommandModel) -> Dict[str, Any]:
        """Handle model control commands"""
        try:
            if not self.llm_manager:
                return {"status": "error", "message": "LLM manager not available"}
            
            # Delegate to LLM manager
            return await self.llm_manager.handle_model_command(
                command.provider, command.model, command.action
            )
            
        except Exception as e:
            self.logger.error(f"Error handling model command: {e}")
            return {"status": "error", "message": str(e)}
    
    async def handle_agent_command(self, command: AgentCommandModel) -> Dict[str, Any]:
        """Handle agent control commands"""
        try:
            if not self.agent_manager:
                return {"status": "error", "message": "Agent manager not available"}
            
            # Delegate to agent manager
            return await self.agent_manager.handle_command(
                command.agent_id, command.action, command.config
            )
            
        except Exception as e:
            self.logger.error(f"Error handling agent command: {e}")
            return {"status": "error", "message": str(e)}
    
    async def handle_websocket(self, websocket: WebSocket):
        """Handle WebSocket connections for real-time updates"""
        await websocket.accept()
        self.websocket_connections.append(websocket)
        
        try:
            while True:
                # Send periodic updates
                status = await self.get_system_status()
                await websocket.send_json(status)
                await asyncio.sleep(5)  # Update every 5 seconds
                
        except Exception as e:
            self.logger.error(f"WebSocket error: {e}")
        finally:
            if websocket in self.websocket_connections:
                self.websocket_connections.remove(websocket)
    
    async def monitor_system(self):
        """Background system monitoring"""
        while True:
            try:
                # Update system metrics
                self.system_state["last_update"] = datetime.now()
                
                # Broadcast updates to WebSocket clients
                if self.websocket_connections:
                    status = await self.get_system_status()
                    for websocket in self.websocket_connections.copy():
                        try:
                            await websocket.send_json(status)
                        except:
                            self.websocket_connections.remove(websocket)
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in system monitor: {e}")
                await asyncio.sleep(30)
    
    async def restart_system(self):
        """Restart system components"""
        self.logger.info("Restarting system components...")
        # Implementation depends on your system architecture
        pass
    
    async def shutdown_system(self):
        """Graceful system shutdown"""
        self.logger.info("Shutting down system...")
        # Implementation depends on your system architecture
        pass
    
    async def reload_configuration(self):
        """Reload system configuration"""
        self.logger.info("Reloading configuration...")
        # Implementation depends on your configuration system
        pass
    
    def run(self, host: str = "127.0.0.1", port: int = 8001):
        """Run the dashboard backend server"""
        if not WEB_AVAILABLE:
            self.logger.error("FastAPI not available, cannot start backend server")
            return
        
        self.logger.info(f"Starting Dashboard Backend on {host}:{port}")
        
        # Initialize system first
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.initialize())
        
        # Run server
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info"
        )

# Standalone execution
if __name__ == "__main__":
    import os
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Get port from environment variable if set
    port = int(os.environ.get('DASHBOARD_BACKEND_PORT', 8001))
    
    backend = DashboardBackend()
    backend.run(port=port)
