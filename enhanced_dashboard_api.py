#!/usr/bin/env python3
"""
Enhanced Dashboard API

RESTful API for the enhanced agent system that can be used by any frontend.
Provides endpoints for agent management, task execution, and system monitoring.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("⚠️ FastAPI not available. Install with: pip install fastapi uvicorn")
    print("   Or run: pip install -r requirements-dashboard.txt")
    
    # Create mock classes for when FastAPI is not available
    class MockFastAPI:
        def __init__(self, *args, **kwargs): pass
        def add_middleware(self, *args, **kwargs): pass
        def include_router(self, *args, **kwargs): pass
        def get(self, *args, **kwargs): 
            def decorator(func): return func
            return decorator
        def post(self, *args, **kwargs):
            def decorator(func): return func 
            return decorator
    
    class MockBaseModel:
        def __init__(self, *args, **kwargs): 
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class MockHTTPException(Exception):
        def __init__(self, status_code=500, detail="Error", **kwargs):
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)
    
    class MockBackgroundTasks:
        def add_task(self, func, *args, **kwargs):
            # In mock mode, just execute immediately
            try:
                func(*args, **kwargs)
            except:
                pass
    
    class MockUvicorn:
        @staticmethod
        def run(*args, **kwargs):
            print("Mock uvicorn server - FastAPI not available")
    
    class MockCORSMiddleware:
        pass
    
    FastAPI = MockFastAPI
    BaseModel = MockBaseModel  
    HTTPException = MockHTTPException
    BackgroundTasks = MockBackgroundTasks
    uvicorn = MockUvicorn
    CORSMiddleware = MockCORSMiddleware
    JSONResponse = dict

logger = logging.getLogger("DashboardAPI")

# Pydantic models for API
class TaskRequest(BaseModel):
    agent_name: str
    task_description: str

class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None

class AgentStatus(BaseModel):
    name: str
    status: str
    current_task: Optional[str] = None
    last_activity: str
    error_count: int = 0

class SystemStatus(BaseModel):
    timestamp: str
    agents_total: int
    agents_active: int
    tasks_completed: int
    tasks_total: int
    success_rate: float
    enhanced_agents_available: bool

class EnhancedDashboardAPI:
    """Enhanced Dashboard API service"""
    
    def __init__(self):
        self.logger = logging.getLogger("DashboardAPI")
        self.enhanced_agents = None
        self.agent_statuses = {}
        self.task_history = []
        self.task_counter = 0
          # FastAPI app
        if FASTAPI_AVAILABLE:
            self.app = self._create_app()
        else:
            self.app = None
    
    def _create_app(self):
        """Create FastAPI application"""
        app = FastAPI(
            title="Enhanced Dashboard API",
            description="API for Ultimate Copilot Enhanced Agent System",
            version="1.0.0"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Define routes
        @app.get("/")
        async def root():
            return {
                "service": "Enhanced Dashboard API",
                "version": "1.0.0",
                "status": "running",
                "enhanced_agents": self.enhanced_agents is not None
            }
        
        @app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "enhanced_agents_available": self.enhanced_agents is not None
            }
        
        @app.get("/status", response_model=SystemStatus)
        async def get_system_status():
            """Get current system status"""
            status = self.get_system_status()
            return SystemStatus(
                timestamp=status["timestamp"],
                agents_total=status["agents"]["total"],
                agents_active=status["agents"]["active"],
                tasks_completed=status["tasks"]["completed"],
                tasks_total=status["tasks"]["total"],
                success_rate=status["tasks"]["success_rate"],
                enhanced_agents_available=status["enhanced_agents_available"]
            )
        
        @app.get("/agents")
        async def get_agents():
            """Get all agent statuses"""
            agents = []
            for name, status in self.agent_statuses.items():
                agents.append(AgentStatus(
                    name=name,
                    status=status["status"],
                    current_task=status["current_task"],
                    last_activity=status["last_activity"].isoformat(),
                    error_count=status["error_count"]
                ))
            return {"agents": agents}
        
        @app.get("/agents/{agent_name}")
        async def get_agent_status(agent_name: str):
            """Get specific agent status"""
            if agent_name not in self.agent_statuses:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            status = self.agent_statuses[agent_name]
            return AgentStatus(
                name=agent_name,
                status=status["status"],
                current_task=status["current_task"],
                last_activity=status["last_activity"].isoformat(),
                error_count=status["error_count"]
            )
        
        @app.post("/tasks/execute")
        async def execute_task(task_request, background_tasks):
            """Execute a task with an agent"""
            if task_request.agent_name not in self.agent_statuses:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            task_id = f"task_{self.task_counter}"
            self.task_counter += 1
            
            # Execute task in background
            background_tasks.add_task(
                self._execute_task_background,
                task_id,
                task_request.agent_name,
                task_request.task_description
            )
            
            return {
                "task_id": task_id,
                "status": "accepted",
                "message": f"Task submitted to {task_request.agent_name}"
            }
        
        @app.get("/tasks/history")
        async def get_task_history(limit: int = 50):
            """Get task execution history"""
            return {
                "tasks": self.task_history[-limit:],
                "total": len(self.task_history)
            }
        
        @app.get("/memory")
        async def get_memory_info():
            """Get agent memory information"""
            return self.get_agent_memory_info()
        
        @app.post("/test/all")
        async def test_all_agents():
            """Test all agents"""
            results = await self.test_all_agents()
            return {"test_results": results}
        
        @app.post("/agents/{agent_name}/reset")
        async def reset_agent(agent_name: str):
            """Reset an agent's status and memory"""
            if agent_name not in self.agent_statuses:
                raise HTTPException(status_code=404, detail="Agent not found")
            
            self.agent_statuses[agent_name].update({
                "status": "ready",
                "current_task": None,
                "error_count": 0,
                "last_activity": datetime.now()
            })
            
            return {"message": f"Agent {agent_name} reset successfully"}
        
        return app
    
    async def initialize(self):
        """Initialize the API service"""
        try:
            self.logger.info("🚀 Initializing Enhanced Dashboard API...")
            
            # Initialize enhanced agent system
            try:
                from working_agent_upgrade import WorkingAgentUpgrade, dispatch_enhanced_task
                self.enhanced_agents = WorkingAgentUpgrade()
                await self.enhanced_agents.initialize()
                self.dispatch_task = dispatch_enhanced_task
                self.logger.info("✅ Enhanced agent system initialized")
            except ImportError as e:
                self.logger.error(f"Enhanced agent system not available: {e}")
                return False
            
            # Initialize agent statuses
            agent_names = ["architect", "backend", "frontend", "QA"]
            for name in agent_names:
                self.agent_statuses[name] = {
                    "status": "ready",
                    "last_activity": datetime.now(),
                    "current_task": None,
                    "error_count": 0
                }
            
            self.logger.info("✅ Dashboard API initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"API initialization failed: {e}")
            return False
    
    async def _execute_task_background(self, task_id: str, agent_name: str, task_description: str):
        """Execute task in background"""
        try:
            result = await self.execute_task(agent_name, task_description)
            
            # Store result with task_id for later retrieval
            task_record = {
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "agent": agent_name,
                "task": task_description,
                "status": "completed" if not result.get("error") else "error",
                "result": result
            }
            self.task_history.append(task_record)
            
            self.logger.info(f"Background task {task_id} completed")
            
        except Exception as e:
            self.logger.error(f"Background task {task_id} failed: {e}")
            task_record = {
                "task_id": task_id,
                "timestamp": datetime.now().isoformat(),
                "agent": agent_name,
                "task": task_description,
                "status": "error",
                "result": {"error": str(e)}
            }
            self.task_history.append(task_record)
    
    async def execute_task(self, agent_name: str, task_description: str) -> Dict[str, Any]:
        """Execute a task using the enhanced agent system"""
        try:
            # Update agent status
            self.agent_statuses[agent_name]["status"] = "working"
            self.agent_statuses[agent_name]["current_task"] = task_description[:50] + "..."
            self.agent_statuses[agent_name]["last_activity"] = datetime.now()
            
            self.logger.info(f"Executing task with {agent_name}: {task_description[:100]}...")
            
            # Execute using enhanced agents
            result = await self.dispatch_task(agent_name, task_description)
            
            # Update status based on result
            success = not result.get("error")
            self.agent_statuses[agent_name]["status"] = "completed" if success else "error"
            self.agent_statuses[agent_name]["current_task"] = None
            self.agent_statuses[agent_name]["last_activity"] = datetime.now()
            
            if not success:
                self.agent_statuses[agent_name]["error_count"] += 1
            
            self.logger.info(f"Task completed: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {e}")
            self.agent_statuses[agent_name]["status"] = "error"
            self.agent_statuses[agent_name]["current_task"] = None
            self.agent_statuses[agent_name]["error_count"] += 1
            
            return {"error": str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        active_agents = sum(1 for status in self.agent_statuses.values() 
                          if status["status"] in ["working", "ready"])
        
        total_tasks = len(self.task_history)
        completed_tasks = len([t for t in self.task_history if t["status"] == "completed"])
        error_tasks = len([t for t in self.task_history if t["status"] == "error"])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "agents": {
                "total": len(self.agent_statuses),
                "active": active_agents,
                "statuses": {name: status["status"] for name, status in self.agent_statuses.items()}
            },
            "tasks": {
                "total": total_tasks,
                "completed": completed_tasks,
                "errors": error_tasks,
                "success_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            },
            "enhanced_agents_available": self.enhanced_agents is not None
        }
    
    def get_agent_memory_info(self) -> Dict[str, Any]:
        """Get agent memory information"""
        if not self.enhanced_agents:
            return {"error": "Enhanced agents not available"}
        
        try:
            memory_info = {}
            if hasattr(self.enhanced_agents, 'memory_cache'):
                for agent_name, memory_data in self.enhanced_agents.memory_cache.items():
                    memory_info[agent_name] = {
                        "memory_size": len(str(memory_data)),
                        "last_updated": datetime.now().isoformat(),
                        "has_context": bool(memory_data.get("context"))
                    }
            
            return memory_info
        except Exception as e:
            return {"error": str(e)}
    
    async def test_all_agents(self) -> Dict[str, Any]:
        """Test all agents with a simple connectivity check"""
        test_task = "Test agent connectivity and basic functionality"
        results = {}
        
        for agent_name in self.agent_statuses.keys():
            self.logger.info(f"Testing agent: {agent_name}")
            result = await self.execute_task(agent_name, test_task)
            results[agent_name] = {
                "success": not result.get("error"),
                "result": result
            }
        
        return results
    
    def run_server(self, host: str = "127.0.0.1", port: int = 8001):
        """Run the API server"""
        if not FASTAPI_AVAILABLE:
            self.logger.error("FastAPI not available - cannot start server")
            return False
        
        if not self.app:
            self.logger.error("App not initialized")
            return False
        
        self.logger.info(f"🚀 Starting Enhanced Dashboard API server on {host}:{port}")
        uvicorn.run(self.app, host=host, port=port, log_level="info")
        return True

async def main():
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    api = EnhancedDashboardAPI()
    
    # Initialize
    if not await api.initialize():
        logger.error("❌ API initialization failed")
        return
    
    # Run server
    if FASTAPI_AVAILABLE:
        api.run_server()
    else:
        logger.error("FastAPI not available - install with: pip install fastapi uvicorn")

if __name__ == "__main__":
    asyncio.run(main())
