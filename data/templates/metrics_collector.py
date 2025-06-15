"""
System Metrics Collector for Ultimate Copilot
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import psutil

class MetricsCollector:
    """Collect and store system metrics"""
    
    def __init__(self):
        self.workspace_root = Path(__file__).parent.parent
        self.metrics_file = self.workspace_root / "data" / "system_metrics.json"
        self.collection_interval = 60  # seconds
          async def start_collection(self):
        """Start metrics collection"""
        print("Starting metrics collection...")
        
        while True:
            try:
                metrics = await self.collect_current_metrics()
                await self.store_metrics(metrics)
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                print(f"Metrics collection error: {e}")
                await asyncio.sleep(30)
    
    async def collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "percent": cpu_percent,
                "count": psutil.cpu_count()
            },
            "memory": {
                "total_gb": memory.total / (1024**3),
                "available_gb": memory.available / (1024**3),
                "percent": memory.percent
            },
            "disk": {
                "total_gb": disk.total / (1024**3),
                "free_gb": disk.free / (1024**3),
                "percent": (disk.used / disk.total) * 100
            }
        }
    
    async def store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics to file"""
        self.metrics_file.parent.mkdir(exist_ok=True, parents=True)
        
        # Read existing metrics
        existing = []
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    existing = json.load(f)
            except:
                existing = []
        
        # Add new metrics
        existing.append(metrics)
        
        # Keep only last 1440 entries (24 hours at 1 minute intervals)
        if len(existing) > 1440:
            existing = existing[-1440:]
        
        # Save back to file
        with open(self.metrics_file, 'w') as f:
            json.dump(existing, f, indent=2)

if __name__ == "__main__":
    collector = MetricsCollector()
    asyncio.run(collector.start_collection())
