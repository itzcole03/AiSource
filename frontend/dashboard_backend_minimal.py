#!/usr/bin/env python3
"""
Minimal Dashboard Backend

A very simple backend that provides basic health and metrics endpoints.
Works without complex dependencies.
"""

import http.server
import socketserver
import json
import psutil
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MinimalBackend")

class MinimalBackend:
    """Minimal backend for dashboard"""
    
    def __init__(self):
        self.port = int(os.environ.get('DASHBOARD_BACKEND_PORT', 8001))
        self.host = "127.0.0.1"
        self.start_time = datetime.now()
    
    def get_health(self) -> Dict[str, Any]:
        """Get health status"""
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "port": self.port,
            "uptime": (datetime.now() - self.start_time).total_seconds()
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu": {
                    "usage_percent": psutil.cpu_percent(),
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total": memory.total,
                    "used": memory.used,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "percent": (disk.used / disk.total) * 100
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}

# Create global backend instance
backend = MinimalBackend()

class RequestHandler(http.server.BaseHTTPRequestHandler):
    """Simple request handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        try:
            if self.path == '/':
                response = {"message": "Minimal Dashboard Backend", "status": "running"}
            elif self.path == '/health':
                response = backend.get_health()
            elif self.path == '/system/metrics':
                response = backend.get_metrics()
            else:
                self.send_error(404)
                return
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.send_error(500)
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass

def main():
    """Run the minimal backend server"""
    try:
        with socketserver.TCPServer((backend.host, backend.port), RequestHandler) as httpd:
            logger.info(f"Minimal backend running on {backend.host}:{backend.port}")
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            backend.port += 1
            logger.info(f"Port in use, trying {backend.port}")
            main()
        else:
            raise e
    except KeyboardInterrupt:
        logger.info("Backend stopped by user")

if __name__ == "__main__":
    main()
