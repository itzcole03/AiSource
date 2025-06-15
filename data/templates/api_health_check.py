"""
API Health Check Endpoint for Ultimate Copilot
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import psutil
import json

router = APIRouter()

@router.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check system resources
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3)
            },
            "services": {
                "api": "running",
                "agents": "active"
            }
        }
        
        # Mark as unhealthy if resources are critically low
        if cpu_percent > 95 or memory.percent > 95:
            health_status["status"] = "degraded"
        
        return health_status
        
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")

@router.get("/metrics")
async def metrics():
    """Prometheus-style metrics endpoint"""
    try:
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        metrics_text = f"""# HELP cpu_usage_percent CPU usage percentage
# TYPE cpu_usage_percent gauge
cpu_usage_percent {cpu_percent}

# HELP memory_usage_percent Memory usage percentage  
# TYPE memory_usage_percent gauge
memory_usage_percent {memory.percent}

# HELP memory_available_bytes Available memory in bytes
# TYPE memory_available_bytes gauge
memory_available_bytes {memory.available}
"""
        
        return {"metrics": metrics_text}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics collection failed: {str(e)}")
