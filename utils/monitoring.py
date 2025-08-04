"""
Production Monitoring and Metrics for AI Agents System
"""
import time
import psutil
from datetime import datetime
from typing import Dict, Any
import logging

class SystemMonitor:
    """Monitor system resources and API performance."""
    
    def __init__(self):
        self.start_time = time.time()
        self.request_count = 0
        self.error_count = 0
        self.logger = logging.getLogger("system_monitor")
    
    def record_request(self) -> None:
        """Record a successful API request."""
        self.request_count += 1
    
    def record_error(self) -> None:
        """Record an API error."""
        self.error_count += 1
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        return {
            "system": {
                "uptime_seconds": uptime,
                "uptime_formatted": self._format_uptime(uptime),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent
            },
            "api": {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate": (self.error_count / max(self.request_count, 1)) * 100,
                "requests_per_second": self.request_count / max(uptime, 1)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _format_uptime(self, uptime_seconds: float) -> str:
        """Format uptime in human-readable format."""
        hours = int(uptime_seconds // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)
        return f"{hours}h {minutes}m {seconds}s"
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall system health status."""
        metrics = self.get_system_metrics()
        
        # Determine health status based on metrics
        cpu_healthy = metrics["system"]["cpu_percent"] < 80
        memory_healthy = metrics["system"]["memory_percent"] < 85
        disk_healthy = metrics["system"]["disk_percent"] < 90
        api_healthy = metrics["api"]["error_rate"] < 10
        
        overall_healthy = all([cpu_healthy, memory_healthy, disk_healthy, api_healthy])
        
        status = {
            "status": "healthy" if overall_healthy else "degraded",
            "components": {
                "cpu": "healthy" if cpu_healthy else "warning",
                "memory": "healthy" if memory_healthy else "warning", 
                "disk": "healthy" if disk_healthy else "warning",
                "api": "healthy" if api_healthy else "error"
            },
            "metrics": metrics
        }
        
        return status


class APIMetrics:
    """Track API endpoint performance."""
    
    def __init__(self):
        self.endpoint_stats = {}
        self.logger = logging.getLogger("api_metrics")
    
    def record_endpoint_call(self, endpoint: str, response_time: float, status_code: int) -> None:
        """Record API endpoint performance."""
        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = {
                "total_calls": 0,
                "total_time": 0,
                "error_count": 0,
                "avg_response_time": 0
            }
        
        stats = self.endpoint_stats[endpoint]
        stats["total_calls"] += 1
        stats["total_time"] += response_time
        stats["avg_response_time"] = stats["total_time"] / stats["total_calls"]
        
        if status_code >= 400:
            stats["error_count"] += 1
    
    def get_endpoint_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all endpoints."""
        return {
            "endpoints": self.endpoint_stats,
            "timestamp": datetime.utcnow().isoformat()
        }