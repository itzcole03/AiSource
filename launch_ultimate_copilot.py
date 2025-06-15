#!/usr/bin/env python3
"""
Ultimate Copilot System Launcher
Starts all services in the correct order
"""

import asyncio
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/system_launcher.log')
    ]
)
logger = logging.getLogger("SystemLauncher")

class SystemLauncher:
    """Launches and manages all Ultimate Copilot services"""
    
    def __init__(self):
        self.services = {}
        self.service_order = [
            "database",
            "api_server", 
            "agent_system",
            "frontend"
        ]
    
    async def start_database(self):
        """Initialize database"""
        logger.info("Initializing database...")
        try:
            from core.database_manager import get_database
            db = await get_database()
            logger.info("Database service started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start database: {e}")
            return False
    
    def start_api_server(self):
        """Start FastAPI server"""
        logger.info("Starting API server...")
        try:
            process = subprocess.Popen([
                sys.executable, "main_api_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.services["api_server"] = process
            time.sleep(2)  # Give it time to start
            logger.info("API server started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
            return False
    
    def start_agent_system(self):
        """Start agent system"""
        logger.info("Starting agent system...")
        try:
            process = subprocess.Popen([
                sys.executable, "run_fast_completion.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.services["agent_system"] = process
            time.sleep(1)
            logger.info("Agent system started successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to start agent system: {e}")
            return False
    
    def start_frontend(self):
        """Start frontend development server"""
        logger.info("Starting frontend...")
        try:
            frontend_dir = Path("frontend")
            if frontend_dir.exists() and (frontend_dir / "package.json").exists():
                process = subprocess.Popen([
                    "npm", "start"
                ], cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.services["frontend"] = process
                logger.info("Frontend development server started")
                return True
            else:
                logger.warning("Frontend not found, using existing dashboard")
                process = subprocess.Popen([
                    sys.executable, "start_dashboard.py"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.services["dashboard"] = process
                return True
        except Exception as e:
            logger.error(f"Failed to start frontend: {e}")
            return False
    
    async def start_all_services(self):
        """Start all services in order"""
        logger.info("=" * 60)
        logger.info("   ULTIMATE COPILOT SYSTEM LAUNCHER")
        logger.info("=" * 60)
        
        success_count = 0
        
        # Start database
        if await self.start_database():
            success_count += 1
        
        # Start API server
        if self.start_api_server():
            success_count += 1
        
        # Start agent system
        if self.start_agent_system():
            success_count += 1
        
        # Start frontend
        if self.start_frontend():
            success_count += 1
        
        logger.info(f"System startup complete: {success_count}/4 services started")
        
        if success_count >= 3:
            logger.info("Ultimate Copilot is ready!")
            logger.info("- API Server: http://localhost:8000")
            logger.info("- API Docs: http://localhost:8000/docs")
            logger.info("- Dashboard: http://localhost:8501 (if using Streamlit)")
            logger.info("- Frontend: http://localhost:3000 (if React app)")
        
        return success_count
    
    def stop_all_services(self):
        """Stop all running services"""
        logger.info("Stopping all services...")
        for name, process in self.services.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"Stopped {name}")
            except Exception as e:
                logger.error(f"Error stopping {name}: {e}")
                try:
                    process.kill()
                except:
                    pass

async def main():
    """Main launcher entry point"""
    launcher = SystemLauncher()
    
    try:
        await launcher.start_all_services()
        
        # Keep running
        logger.info("Press Ctrl+C to stop all services")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutdown requested by user")
    except Exception as e:
        logger.error(f"System error: {e}")
    finally:
        launcher.stop_all_services()

if __name__ == "__main__":
    asyncio.run(main())
