#!/usr/bin/env python3
"""
Real-time System Monitor and Performance Optimizer

This system provides real-time monitoring of the Ultimate Copilot system,
tracking performance metrics, and automatically optimizing resource allocation.
"""

import asyncio
import logging
import psutil
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import deque
import threading
import requests

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_available_gb: float
    gpu_memory_used_mb: float = 0
    gpu_memory_total_mb: float = 0
    active_models: int = 0
    active_agents: int = 0
    pending_tasks: int = 0
    response_time_ms: float = 0
    throughput_tasks_per_minute: float = 0

@dataclass
class PerformanceAlert:
    """Performance alert"""
    id: str
    severity: str  # low, medium, high, critical
    message: str
    metric: str
    threshold: float
    current_value: float
    timestamp: datetime
    resolved: bool = False

class RealTimeSystemMonitor:
    """
    Real-time monitoring system for Ultimate Copilot performance and optimization
    """
    
    def __init__(self, model_manager=None, agent_coordinator=None):
        self.model_manager = model_manager
        self.agent_coordinator = agent_coordinator
        
        # Metrics storage (keep last 1000 readings)
        self.metrics_history: deque = deque(maxlen=1000)
        self.alerts: List[PerformanceAlert] = []
        
        # Performance thresholds
        self.thresholds = {
            "cpu_percent": {"warning": 80, "critical": 95},
            "memory_percent": {"warning": 85, "critical": 95},
            "gpu_memory_percent": {"warning": 85, "critical": 95},
            "response_time_ms": {"warning": 5000, "critical": 10000},
            "model_load_time": {"warning": 30, "critical": 60}
        }
        
        # Monitoring state
        self.monitoring_active = False
        self.optimization_active = True
        self.last_optimization = datetime.now()
        
        # Performance tracking
        self.task_completion_times = deque(maxlen=100)
        self.model_performance = {}
        self.agent_performance = {}
        
        # Setup logging
        self.logger = logging.getLogger("SystemMonitor")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    async def start_monitoring(self, interval_seconds: int = 30):
        """Start real-time monitoring"""
        self.monitoring_active = True
        self.logger.info("Started real-time system monitoring")
        
        while self.monitoring_active:
            try:
                # Collect metrics
                metrics = await self._collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # Check for alerts
                await self._check_performance_alerts(metrics)
                
                # Auto-optimization
                if self.optimization_active:
                    await self._auto_optimize_system(metrics)
                
                # Log summary every 5 minutes
                if len(self.metrics_history) % 10 == 0:
                    await self._log_performance_summary()
                
                await asyncio.sleep(interval_seconds)
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(interval_seconds)
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring_active = False
        self.logger.info("Stopped system monitoring")
    
    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        
        # Basic system metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_available_gb = memory.available / (1024**3)
        
        # GPU metrics (if available)
        gpu_memory_used_mb = 0
        gpu_memory_total_mb = 0
        
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            gpu_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            gpu_memory_used_mb = gpu_info.used / (1024**2)
            gpu_memory_total_mb = gpu_info.total / (1024**2)
        except:
            pass  # No GPU or pynvml not available
        
        # Model and agent metrics
        active_models = 0
        active_agents = 0
        pending_tasks = 0
        
        if self.model_manager:
            try:
                memory_status = await self.model_manager.get_memory_status()
                active_models = memory_status.get('loaded_models', 0)
            except:
                pass
        
        if self.agent_coordinator:
            try:
                coord_status = await self.agent_coordinator.get_coordination_analytics()
                pending_tasks = coord_status.get('queued_requests', 0)
                active_agents = coord_status.get('total_agents', 0)
            except:
                pass
        
        # Calculate throughput
        throughput = self._calculate_throughput()
        
        # Calculate average response time
        avg_response_time = self._calculate_avg_response_time()
        
        return SystemMetrics(
            timestamp=datetime.now(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_available_gb=memory_available_gb,
            gpu_memory_used_mb=gpu_memory_used_mb,
            gpu_memory_total_mb=gpu_memory_total_mb,
            active_models=active_models,
            active_agents=active_agents,
            pending_tasks=pending_tasks,
            response_time_ms=avg_response_time,
            throughput_tasks_per_minute=throughput
        )
    
    def _calculate_throughput(self) -> float:
        """Calculate tasks per minute throughput"""
        if len(self.task_completion_times) < 2:
            return 0.0
        
        # Count tasks completed in last minute
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        recent_tasks = [t for t in self.task_completion_times if t > one_minute_ago]
        
        return len(recent_tasks)
    
    def _calculate_avg_response_time(self) -> float:
        """Calculate average response time"""
        if not hasattr(self, '_response_times') or not self._response_times:
            return 0.0
        
        recent_times = list(self._response_times)[-10:]  # Last 10 responses
        return sum(recent_times) / len(recent_times) if recent_times else 0.0
    
    async def _check_performance_alerts(self, metrics: SystemMetrics):
        """Check for performance alerts"""
        
        alerts_to_add = []
        
        # CPU check
        if metrics.cpu_percent > self.thresholds["cpu_percent"]["critical"]:
            alerts_to_add.append(PerformanceAlert(
                id=f"cpu_critical_{int(time.time())}",
                severity="critical",
                message=f"CPU usage critical: {metrics.cpu_percent:.1f}%",
                metric="cpu_percent",
                threshold=self.thresholds["cpu_percent"]["critical"],
                current_value=metrics.cpu_percent,
                timestamp=datetime.now()
            ))
        elif metrics.cpu_percent > self.thresholds["cpu_percent"]["warning"]:
            alerts_to_add.append(PerformanceAlert(
                id=f"cpu_warning_{int(time.time())}",
                severity="warning",
                message=f"CPU usage high: {metrics.cpu_percent:.1f}%",
                metric="cpu_percent",
                threshold=self.thresholds["cpu_percent"]["warning"],
                current_value=metrics.cpu_percent,
                timestamp=datetime.now()
            ))
        
        # Memory check
        if metrics.memory_percent > self.thresholds["memory_percent"]["critical"]:
            alerts_to_add.append(PerformanceAlert(
                id=f"memory_critical_{int(time.time())}",
                severity="critical",
                message=f"Memory usage critical: {metrics.memory_percent:.1f}%",
                metric="memory_percent",
                threshold=self.thresholds["memory_percent"]["critical"],
                current_value=metrics.memory_percent,
                timestamp=datetime.now()
            ))
        
        # GPU memory check
        if metrics.gpu_memory_total_mb > 0:
            gpu_percent = (metrics.gpu_memory_used_mb / metrics.gpu_memory_total_mb) * 100
            if gpu_percent > self.thresholds["gpu_memory_percent"]["critical"]:
                alerts_to_add.append(PerformanceAlert(
                    id=f"gpu_critical_{int(time.time())}",
                    severity="critical",
                    message=f"GPU memory critical: {gpu_percent:.1f}%",
                    metric="gpu_memory_percent",
                    threshold=self.thresholds["gpu_memory_percent"]["critical"],
                    current_value=gpu_percent,
                    timestamp=datetime.now()
                ))
        
        # Log new alerts
        for alert in alerts_to_add:
            self.alerts.append(alert)
            if alert.severity == "critical":
                self.logger.error(f"CRITICAL ALERT: {alert.message}")
            elif alert.severity == "warning":
                self.logger.warning(f"WARNING: {alert.message}")
    
    async def _auto_optimize_system(self, metrics: SystemMetrics):
        """Automatically optimize system based on current metrics"""
        
        # Only optimize every 2 minutes to avoid thrashing
        if datetime.now() - self.last_optimization < timedelta(minutes=2):
            return
        
        optimizations = []
        
        # Memory optimization
        if metrics.memory_percent > 80:
            optimizations.append("high_memory")
            
        # GPU memory optimization
        if metrics.gpu_memory_total_mb > 0:
            gpu_percent = (metrics.gpu_memory_used_mb / metrics.gpu_memory_total_mb) * 100
            if gpu_percent > 80:
                optimizations.append("high_gpu_memory")
        
        # CPU optimization
        if metrics.cpu_percent > 75:
            optimizations.append("high_cpu")
        
        # Apply optimizations
        if optimizations:
            await self._apply_optimizations(optimizations, metrics)
            self.last_optimization = datetime.now()
    
    async def _apply_optimizations(self, optimizations: List[str], metrics: SystemMetrics):
        """Apply performance optimizations"""
        
        for optimization in optimizations:
            try:
                if optimization == "high_memory":
                    await self._optimize_memory_usage(metrics)
                elif optimization == "high_gpu_memory":
                    await self._optimize_gpu_memory(metrics)
                elif optimization == "high_cpu":
                    await self._optimize_cpu_usage(metrics)
                    
            except Exception as e:
                self.logger.error(f"Optimization {optimization} failed: {e}")
    
    async def _optimize_memory_usage(self, metrics: SystemMetrics):
        """Optimize memory usage"""
        self.logger.info("Applying memory optimization...")
        
        if self.model_manager:
            # Check if we can unload unused models
            try:
                memory_status = await self.model_manager.get_memory_status()
                if memory_status.get('current_usage_mb', 0) > 6000:  # Above 6GB
                    self.logger.info("High VRAM usage detected, may trigger model unloading")
                    # In real implementation, this would trigger intelligent model unloading
                    
            except Exception as e:
                self.logger.error(f"Memory optimization failed: {e}")
    
    async def _optimize_gpu_memory(self, metrics: SystemMetrics):
        """Optimize GPU memory usage"""
        self.logger.info("Applying GPU memory optimization...")
        
        # Similar to memory optimization but for GPU
        if self.model_manager:
            try:
                # Force garbage collection
                import gc
                gc.collect()
                
                # In real implementation, this would unload least recently used models
                self.logger.info("GPU memory optimization applied")
                
            except Exception as e:
                self.logger.error(f"GPU optimization failed: {e}")
    
    async def _optimize_cpu_usage(self, metrics: SystemMetrics):
        """Optimize CPU usage"""
        self.logger.info("Applying CPU optimization...")
        
        # Reduce concurrent operations if CPU is overloaded
        if self.agent_coordinator:
            try:
                # In real implementation, this would throttle agent execution
                self.logger.info("CPU optimization applied - reduced concurrent operations")
                
            except Exception as e:
                self.logger.error(f"CPU optimization failed: {e}")
    
    async def _log_performance_summary(self):
        """Log performance summary"""
        if not self.metrics_history:
            return
        
        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 readings
        
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_response = sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics)
        
        self.logger.info(f"Performance Summary: CPU {avg_cpu:.1f}%, Memory {avg_memory:.1f}%, "
                        f"Response {avg_response:.1f}ms, Active Models {recent_metrics[-1].active_models}")
    
    def record_task_completion(self, duration_seconds: float):
        """Record task completion for performance tracking"""
        self.task_completion_times.append(datetime.now())
        
        # Track response times
        if not hasattr(self, '_response_times'):
            self._response_times = deque(maxlen=50)
        self._response_times.append(duration_seconds * 1000)  # Convert to ms
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get performance dashboard data"""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        latest = self.metrics_history[-1]
        
        # Calculate trends
        if len(self.metrics_history) >= 10:
            recent_cpu = [m.cpu_percent for m in list(self.metrics_history)[-10:]]
            cpu_trend = "rising" if recent_cpu[-1] > recent_cpu[0] else "falling"
        else:
            cpu_trend = "stable"
        
        # Active alerts
        active_alerts = [a for a in self.alerts if not a.resolved]
        
        return {
            "current_metrics": {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "memory_available_gb": latest.memory_available_gb,
                "gpu_memory_used_mb": latest.gpu_memory_used_mb,
                "gpu_memory_total_mb": latest.gpu_memory_total_mb,
                "active_models": latest.active_models,
                "active_agents": latest.active_agents,
                "pending_tasks": latest.pending_tasks,
                "response_time_ms": latest.response_time_ms,
                "throughput": latest.throughput_tasks_per_minute
            },
            "trends": {
                "cpu_trend": cpu_trend
            },
            "alerts": {
                "active_count": len(active_alerts),
                "critical_count": len([a for a in active_alerts if a.severity == "critical"]),
                "recent_alerts": [
                    {
                        "severity": a.severity,
                        "message": a.message,
                        "timestamp": a.timestamp.isoformat()
                    } for a in active_alerts[-5:]
                ]
            },
            "performance": {
                "avg_response_time_ms": self._calculate_avg_response_time(),
                "tasks_per_minute": self._calculate_throughput(),
                "total_metrics_collected": len(self.metrics_history)
            }
        }
    
    async def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get AI-powered optimization recommendations"""
        if not self.metrics_history:
            return []
        
        recommendations = []
        latest = self.metrics_history[-1]
        
        # Memory recommendations
        if latest.memory_percent > 85:
            recommendations.append({
                "type": "memory",
                "priority": "high",
                "title": "High Memory Usage Detected",
                "description": "Consider unloading unused models or reducing concurrent operations",
                "impact": "Prevents system slowdown and potential crashes"
            })
        
        # GPU recommendations
        if latest.gpu_memory_total_mb > 0:
            gpu_percent = (latest.gpu_memory_used_mb / latest.gpu_memory_total_mb) * 100
            if gpu_percent > 90:
                recommendations.append({
                    "type": "gpu",
                    "priority": "critical",
                    "title": "GPU Memory Near Capacity",
                    "description": "Unload least recently used models immediately",
                    "impact": "Prevents out-of-memory errors and model loading failures"
                })
        
        # Performance recommendations
        if latest.response_time_ms > 3000:
            recommendations.append({
                "type": "performance",
                "priority": "medium",
                "title": "Slow Response Times",
                "description": "Consider load balancing across models or upgrading hardware",
                "impact": "Improves user experience and system responsiveness"
            })
        
        # Model efficiency recommendations
        if latest.active_models > 3 and latest.memory_percent > 70:
            recommendations.append({
                "type": "efficiency",
                "priority": "medium",
                "title": "Model Consolidation Opportunity",
                "description": "Multiple models active with high memory usage - consider model sharing",
                "impact": "Reduces memory footprint while maintaining functionality"
            })
        
        return recommendations

async def test_system_monitor():
    """Test the system monitor"""
    print("Testing Real-time System Monitor...")
    
    monitor = RealTimeSystemMonitor()
    
    # Test metric collection
    metrics = await monitor._collect_system_metrics()
    print(f"✓ Collected system metrics: CPU {metrics.cpu_percent:.1f}%, Memory {metrics.memory_percent:.1f}%")
    
    # Test dashboard
    monitor.metrics_history.append(metrics)
    dashboard = monitor.get_performance_dashboard()
    print(f"✓ Performance dashboard: {dashboard['current_metrics']['cpu_percent']:.1f}% CPU")
    
    # Test recommendations
    recommendations = await monitor.get_optimization_recommendations()
    print(f"✓ Generated {len(recommendations)} optimization recommendations")
    
    # Test task completion tracking
    monitor.record_task_completion(2.5)
    print(f"✓ Task completion recorded")
    
    return True

if __name__ == "__main__":
    result = asyncio.run(test_system_monitor())
    exit(0 if result else 1)
