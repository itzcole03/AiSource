"""
Main API Server for Ultimate Copilot
Combines all API endpoints into a single FastAPI application
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import Dict, Any

# Import all API modules
from api.agent_control import router as agent_control_routerfrom api.system_monitoring import router as system_monitoring_routerfrom api.task_management import router as task_management_router

from core.database_manager import get_database

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Ultimate Copilot API",
    description="API for the Ultimate Copilot multi-agent system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(agent_control_router, prefix='/agent_control', tags=['agent_control'])app.include_router(system_monitoring_router, prefix='/system_monitoring', tags=['system_monitoring'])app.include_router(task_management_router, prefix='/task_management', tags=['task_management'])

@app.on_startup
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Ultimate Copilot API server...")
    db = await get_database()
    logger.info("API server startup complete")

@app.on_shutdown
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Ultimate Copilot API server...")
    db = await get_database()
    await db.close()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ultimate Copilot API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            {"path": "/docs", "description": "API documentation"},
            {"path": "/agent_control", "description": "Agent control endpoints"},
            {"path": "/task_management", "description": "Task management endpoints"},
            {"path": "/system_monitoring", "description": "System monitoring endpoints"}
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        db = await get_database()
        # Simple database connectivity check
        await db.execute_query("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the API server"""
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    run_server()
