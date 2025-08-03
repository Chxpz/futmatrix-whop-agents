"""
Health monitoring and metrics collection for the AI agents system.
Provides comprehensive monitoring of all system components.
"""
import logging
import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import psutil
import json

from utils.exceptions import MonitoringError
from config.settings import Settings


@dataclass
class HealthStatus:
    """Health status for a system component."""
    component: str
    status: str  # healthy, degraded, unhealthy
    last_check: str
    response_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class SystemMetrics:
    """System performance metrics."""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_connections: int
    response_times: Dict[str, float]
    error_rates: Dict[str, float]
    agent_metrics: Dict[str, Any]


class MetricsCollector:
    """Collects and stores system metrics."""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.request_counts: Dict[str, int] = defaultdict(int)
        self.logger = logging.getLogger("metrics_collector")
    
    def record_response_time(self, endpoint: str, response_time: float) -> None:
        """Record response time for an endpoint."""
        self.response_times[endpoint].append(response_time)
    
    def record_request(self, endpoint: str, success: bool = True) -> None:
        """Record request count and success/failure."""
        self.request_counts[endpoint] += 1
        if not success:
            self.error_counts[endpoint] += 1
    
    def get_average_response_time(self, endpoint: str) -> float:
        """Get average response time for endpoint."""
        times = self.response_times[endpoint]
        return sum(times) / len(times) if times else 0.0
    
    def get_error_rate(self, endpoint: str) -> float:
        """Get error rate for endpoint."""
        total_requests = self.request_counts[endpoint]
        if total_requests == 0:
            return 0.0
        return self.error_counts[endpoint] / total_requests
    
    def collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        # System resource metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network connections
        connections = len(psutil.net_connections())
        
        # Calculate average response times
        avg_response_times = {
            endpoint: self.get_average_response_time(endpoint)
            for endpoint in self.response_times.keys()
        }
        
        # Calculate error rates
        error_rates = {
            endpoint: self.get_error_rate(endpoint)
            for endpoint in self.request_counts.keys()
        }
        
        metrics = SystemMetrics(
            timestamp=datetime.utcnow().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            active_connections=connections,
            response_times=avg_response_times,
            error_rates=error_rates,
            agent_metrics={}  # Will be populated by agent metrics
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def get_metrics_summary(self, hours: int = 1) -> Dict[str, Any]:
        """Get metrics summary for the specified time period."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m.timestamp) > cutoff_time
        ]
        
        if not recent_metrics:
            return {"error": "No metrics available for the specified period"}
        
        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m.disk_percent for m in recent_metrics) / len(recent_metrics)
        
        # Peak values
        peak_cpu = max(m.cpu_percent for m in recent_metrics)
        peak_memory = max(m.memory_percent for m in recent_metrics)
        
        return {
            "period_hours": hours,
            "metrics_count": len(recent_metrics),
            "averages": {
                "cpu_percent": round(avg_cpu, 2),
                "memory_percent": round(avg_memory, 2),
                "disk_percent": round(avg_disk, 2)
            },
            "peaks": {
                "cpu_percent": round(peak_cpu, 2),
                "memory_percent": round(peak_memory, 2)
            },
            "current": asdict(recent_metrics[-1]) if recent_metrics else None
        }


class HealthChecker:
    """Performs health checks on system components."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger("health_checker")
        self.last_checks: Dict[str, HealthStatus] = {}
    
    async def check_database_health(self) -> HealthStatus:
        """Check database connectivity and performance."""
        start_time = time.time()
        
        try:
            # Import here to avoid circular imports
            from core.database_schema import DatabaseSchemaManager
            
            schema_manager = DatabaseSchemaManager(self.settings)
            await schema_manager.initialize()
            
            # Simple connectivity test
            async with schema_manager.connection_pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            
            await schema_manager.close()
            
            response_time = time.time() - start_time
            
            status = HealthStatus(
                component="database",
                status="healthy",
                last_check=datetime.utcnow().isoformat(),
                response_time=response_time,
                metadata={"database_type": "postgresql"}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            status = HealthStatus(
                component="database",
                status="unhealthy",
                last_check=datetime.utcnow().isoformat(),
                response_time=response_time,
                error_message=str(e)
            )
        
        self.last_checks["database"] = status
        return status
    
    async def check_openai_health(self) -> HealthStatus:
        """Check OpenAI API connectivity."""
        start_time = time.time()
        
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=self.settings.OPENAI_API_KEY)
            
            # Simple test call
            await client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": "health check"}],
                max_tokens=1
            )
            
            response_time = time.time() - start_time
            
            status = HealthStatus(
                component="openai",
                status="healthy",
                last_check=datetime.utcnow().isoformat(),
                response_time=response_time,
                metadata={"model": "gpt-4o"}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            status = HealthStatus(
                component="openai",
                status="unhealthy",
                last_check=datetime.utcnow().isoformat(),
                response_time=response_time,
                error_message=str(e)
            )
        
        self.last_checks["openai"] = status
        return status
    
    async def check_message_broker_health(self) -> HealthStatus:
        """Check message broker connectivity."""
        start_time = time.time()
        
        try:
            import pika
            
            # Test RabbitMQ connection
            connection = pika.BlockingConnection(
                pika.URLParameters(self.settings.RABBITMQ_URL)
            )
            connection.close()
            
            response_time = time.time() - start_time
            
            status = HealthStatus(
                component="message_broker",
                status="healthy",
                last_check=datetime.utcnow().isoformat(),
                response_time=response_time,
                metadata={"broker_type": "rabbitmq"}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            status = HealthStatus(
                component="message_broker",
                status="unhealthy",
                last_check=datetime.utcnow().isoformat(),
                response_time=response_time,
                error_message=str(e)
            )
        
        self.last_checks["message_broker"] = status
        return status
    
    async def check_redis_health(self) -> HealthStatus:
        """Check Redis connectivity."""
        start_time = time.time()
        
        try:
            import redis.asyncio as redis
            
            # Test Redis connection
            redis_client = redis.from_url(self.settings.REDIS_URL)
            await redis_client.ping()
            await redis_client.close()
            
            response_time = time.time() - start_time
            
            status = HealthStatus(
                component="redis",
                status="healthy",
                last_check=datetime.utcnow().isoformat(),
                response_time=response_time,
                metadata={"cache_type": "redis"}
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            status = HealthStatus(
                component="redis",
                status="unhealthy",
                last_check=datetime.utcnow().isoformat(),
                response_time=response_time,
                error_message=str(e)
            )
        
        self.last_checks["redis"] = status
        return status
    
    async def check_agents_health(self, agents: Dict[str, Any]) -> List[HealthStatus]:
        """Check health of all agents."""
        health_statuses = []
        
        for agent_id, agent in agents.items():
            start_time = time.time()
            
            try:
                # Test agent responsiveness
                if hasattr(agent, 'health_check'):
                    await agent.health_check()
                
                response_time = time.time() - start_time
                
                status = HealthStatus(
                    component=f"agent_{agent_id}",
                    status="healthy",
                    last_check=datetime.utcnow().isoformat(),
                    response_time=response_time,
                    metadata={
                        "agent_type": getattr(agent, 'personality_type', 'unknown'),
                        "business_domain": getattr(agent, 'business_domain', 'unknown')
                    }
                )
                
            except Exception as e:
                response_time = time.time() - start_time
                status = HealthStatus(
                    component=f"agent_{agent_id}",
                    status="unhealthy",
                    last_check=datetime.utcnow().isoformat(),
                    response_time=response_time,
                    error_message=str(e)
                )
            
            health_statuses.append(status)
            self.last_checks[f"agent_{agent_id}"] = status
        
        return health_statuses
    
    async def run_all_health_checks(self, agents: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run all health checks and return comprehensive status."""
        start_time = time.time()
        
        # Run health checks concurrently
        tasks = [
            self.check_database_health(),
            self.check_openai_health(),
            self.check_message_broker_health(),
            self.check_redis_health()
        ]
        
        if agents:
            tasks.append(self.check_agents_health(agents))
        
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            health_statuses = []
            agent_statuses = []
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    # Handle exceptions
                    component_name = ["database", "openai", "message_broker", "redis", "agents"][i]
                    error_status = HealthStatus(
                        component=component_name,
                        status="unhealthy",
                        last_check=datetime.utcnow().isoformat(),
                        response_time=0.0,
                        error_message=str(result)
                    )
                    health_statuses.append(error_status)
                elif isinstance(result, list):
                    # Agent health results
                    agent_statuses.extend(result)
                else:
                    # Single health status
                    health_statuses.append(result)
            
            # Combine all statuses
            all_statuses = health_statuses + agent_statuses
            
            # Calculate overall health
            healthy_count = sum(1 for s in all_statuses if s.status == "healthy")
            degraded_count = sum(1 for s in all_statuses if s.status == "degraded")
            unhealthy_count = sum(1 for s in all_statuses if s.status == "unhealthy")
            
            if unhealthy_count > 0:
                overall_status = "unhealthy"
            elif degraded_count > 0:
                overall_status = "degraded"
            else:
                overall_status = "healthy"
            
            total_time = time.time() - start_time
            
            return {
                "overall_status": overall_status,
                "timestamp": datetime.utcnow().isoformat(),
                "total_check_time": round(total_time, 3),
                "component_summary": {
                    "total": len(all_statuses),
                    "healthy": healthy_count,
                    "degraded": degraded_count,
                    "unhealthy": unhealthy_count
                },
                "components": {s.component: asdict(s) for s in all_statuses}
            }
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                "overall_status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }


class MonitoringManager:
    """Main monitoring manager for the AI agents system."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = logging.getLogger("monitoring_manager")
        
        self.metrics_collector = MetricsCollector()
        self.health_checker = HealthChecker(settings)
        
        # Monitoring configuration
        self.health_check_interval = 300  # 5 minutes
        self.metrics_collection_interval = 60  # 1 minute
        
        # Background tasks
        self.monitoring_tasks = []
        self.is_monitoring = False
    
    async def start_monitoring(self) -> None:
        """Start background monitoring tasks."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        
        # Start health check task
        health_task = asyncio.create_task(self._health_check_loop())
        self.monitoring_tasks.append(health_task)
        
        # Start metrics collection task
        metrics_task = asyncio.create_task(self._metrics_collection_loop())
        self.monitoring_tasks.append(metrics_task)
        
        self.logger.info("Background monitoring started")
    
    async def stop_monitoring(self) -> None:
        """Stop background monitoring tasks."""
        self.is_monitoring = False
        
        for task in self.monitoring_tasks:
            task.cancel()
        
        await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)
        self.monitoring_tasks.clear()
        
        self.logger.info("Background monitoring stopped")
    
    async def _health_check_loop(self) -> None:
        """Background health check loop."""
        while self.is_monitoring:
            try:
                await self.health_checker.run_all_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _metrics_collection_loop(self) -> None:
        """Background metrics collection loop."""
        while self.is_monitoring:
            try:
                self.metrics_collector.collect_system_metrics()
                await asyncio.sleep(self.metrics_collection_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Metrics collection loop error: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def get_system_status(self, agents: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get comprehensive system status."""
        try:
            # Get latest health status
            health_status = await self.health_checker.run_all_health_checks(agents)
            
            # Get latest metrics
            current_metrics = self.metrics_collector.collect_system_metrics()
            
            # Get metrics summary
            metrics_summary = self.metrics_collector.get_metrics_summary(hours=1)
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "health": health_status,
                "current_metrics": asdict(current_metrics),
                "metrics_summary": metrics_summary,
                "monitoring_active": self.is_monitoring
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get system status: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
                "monitoring_active": self.is_monitoring
            }
    
    def record_api_request(self, endpoint: str, response_time: float, success: bool = True) -> None:
        """Record API request metrics."""
        self.metrics_collector.record_response_time(endpoint, response_time)
        self.metrics_collector.record_request(endpoint, success)
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get quick health summary."""
        last_checks = self.health_checker.last_checks
        
        if not last_checks:
            return {"status": "unknown", "message": "No health checks performed yet"}
        
        healthy_components = [c for c, s in last_checks.items() if s.status == "healthy"]
        unhealthy_components = [c for c, s in last_checks.items() if s.status == "unhealthy"]
        
        if not unhealthy_components:
            overall_status = "healthy"
        elif len(unhealthy_components) < len(last_checks) / 2:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"
        
        return {
            "overall_status": overall_status,
            "healthy_components": len(healthy_components),
            "unhealthy_components": len(unhealthy_components),
            "last_check": max(s.last_check for s in last_checks.values()) if last_checks else None
        }