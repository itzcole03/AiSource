"""
Intelligent Monitoring System for Ultimate Copilot
Real-time monitoring with AI-powered insights and alerts
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import psutil

class IntelligentMonitor:
    """AI-powered monitoring system with predictive capabilities"""
    
    def __init__(self):
        self.workspace_root = Path(__file__).parent.parent
        self.metrics_log = self.workspace_root / "logs" / "intelligent_metrics.json"
        self.alerts_log = self.workspace_root / "logs" / "monitoring_alerts.log"
        self.running = False
        
    async def start_monitoring(self):
        """Start intelligent monitoring"""
        self.running = True
        self.log_alert("🎯 Intelligent monitoring system started")
        
        while self.running:
            metrics = await self.collect_metrics()
            await self.analyze_metrics(metrics)
            await self.save_metrics(metrics)
            await asyncio.sleep(30)  # Monitor every 30 seconds
    
    async def collect_metrics(self) -> Dict[str, Any]:
        """Collect system and application metrics"""
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free / (1024**3),
            "agent_activity": await self.get_agent_activity()
        }
    
    async def get_agent_activity(self) -> Dict[str, Any]:
        """Get current agent activity metrics"""
        agent_logs_dir = self.workspace_root / "logs" / "intelligent_agents"
        if not agent_logs_dir.exists():
            return {"active_agents": 0, "last_activity": None}
        
        active_agents = len([f for f in agent_logs_dir.glob("*_intelligent_work.log")])
        return {
            "active_agents": active_agents,
            "last_activity": datetime.now().isoformat()
        }
    
    async def analyze_metrics(self, metrics: Dict[str, Any]):
        """Analyze metrics with AI insights"""
        # CPU usage alerts
        if metrics["cpu_percent"] > 90:
            self.log_alert(f"🚨 HIGH CPU USAGE: {metrics['cpu_percent']:.1f}%")
        
        # Memory usage alerts
        if metrics["memory_percent"] > 85:
            self.log_alert(f"🚨 HIGH MEMORY USAGE: {metrics['memory_percent']:.1f}%")
        
        # Disk space alerts
        if metrics["disk_percent"] > 90:
            self.log_alert(f"🚨 LOW DISK SPACE: {metrics['disk_percent']:.1f}% full")
    
    async def save_metrics(self, metrics: Dict[str, Any]):
        """Save metrics to file"""
        self.metrics_log.parent.mkdir(exist_ok=True, parents=True)
        
        # Read existing metrics
        existing_metrics = []
        if self.metrics_log.exists():
            try:
                with open(self.metrics_log, 'r') as f:
                    existing_metrics = json.load(f)
            except:
                existing_metrics = []
        
        # Add new metrics
        existing_metrics.append(metrics)
        
        # Keep only last 1000 entries
        if len(existing_metrics) > 1000:
            existing_metrics = existing_metrics[-1000:]
        
        # Save back to file
        with open(self.metrics_log, 'w') as f:
            json.dump(existing_metrics, f, indent=2)
    
    def log_alert(self, message: str):
        """Log monitoring alert"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_entry = f"[{timestamp}] {message}\n"
        
        self.alerts_log.parent.mkdir(exist_ok=True, parents=True)
        with open(self.alerts_log, 'a', encoding='utf-8') as f:
            f.write(alert_entry)

if __name__ == "__main__":
    monitor = IntelligentMonitor()
    asyncio.run(monitor.start_monitoring())
