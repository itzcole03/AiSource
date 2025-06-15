#!/usr/bin/env python3
"""
Simplified Dashboard Backend

A lightweight backend that works without complex dependencies.
Provides basic system information and health checking.
"""

import asyncio
import logging
import json
import psutil
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SimplifiedBackend")

class SimplifiedDashboardBackend:
    """Simplified backend for the dashboard that works reliably"""
    
    def __init__(self):
        self.port = int(os.environ.get('DASHBOARD_BACKEND_PORT', 8001))
        self.host = "127.0.0.1"
        self.running = False
        
        # System state
        self.system_state = {
            "status": "running",
            "uptime_start": datetime.now(),
            "metrics": {},
            "last_update": datetime.now()
        }
    def get_system_metrics_sync(self) -> Dict[str, Any]:
        """Get basic system metrics synchronously"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # System info
            uptime = datetime.now() - self.system_state["uptime_start"]
            
            metrics = {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": cpu_count
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": (disk.used / disk.total) * 100
                },
                "system": {
                    "uptime_seconds": uptime.total_seconds(),
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            self.system_state["metrics"] = metrics
            self.system_state["last_update"] = datetime.now()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return {"error": str(e)}
    
    def get_health_status_sync(self) -> Dict[str, Any]:
        """Get backend health status synchronously"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "port": self.port,
            "uptime": (datetime.now() - self.system_state["uptime_start"]).total_seconds()
        }
    async def start_simple_server(self):
        """Start a simple HTTP-like server without FastAPI"""
        import http.server
        import socketserver
        import threading
        import urllib.parse
        import json
        
        backend_instance = self  # Store reference for closure
        
        class SimpleDashboardHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                """Handle GET requests"""
                try:                    if self.path == '/':
                        response = {"message": "Dashboard Backend", "status": "running"}
                    elif self.path == '/health':
                        response = backend_instance.get_health_status_sync()
                    elif self.path == '/system/metrics':
                        response = backend_instance.get_system_metrics_sync()
                    else:
                        self.send_error(404)
                        return
                    
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(response, indent=2).encode())
                    
                except Exception as e:
                    logger.error(f"Error handling GET request: {e}")
                    self.send_error(500)
            
            def do_OPTIONS(self):
                """Handle CORS preflight requests"""
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
            
            def log_message(self, format, *args):
                """Suppress default logging"""
                pass
        
        try:
            with socketserver.TCPServer((self.host, self.port), SimpleDashboardHandler) as httpd:
                logger.info(f"Simplified backend server running on {self.host}:{self.port}")
                self.running = True
                httpd.serve_forever()
        except OSError as e:
            if "Address already in use" in str(e):
                logger.warning(f"Port {self.port} is in use, trying next port...")
                self.port += 1
                return await self.start_simple_server()
            else:
                raise e
    
    def run(self, host: Optional[str] = None, port: Optional[int] = None):
        """Run the simplified backend server"""
        if host:
            self.host = host
        if port:
            self.port = port
            
        logger.info(f"Starting Simplified Dashboard Backend on {self.host}:{self.port}")
        
        try:
            # Run the simple server
            asyncio.run(self.start_simple_server())
        except KeyboardInterrupt:
            logger.info("Backend stopped by user")
        except Exception as e:
            logger.error(f"Backend error: {e}")
            raise e

# Standalone execution
if __name__ == "__main__":
    import os
    
    # Get port from environment variable if set
    port = int(os.environ.get('DASHBOARD_BACKEND_PORT', 8001))
    
    backend = SimplifiedDashboardBackend()
    backend.run(port=port)
