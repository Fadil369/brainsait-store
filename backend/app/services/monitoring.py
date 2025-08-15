"""
Application and Infrastructure Monitoring Service
Provides comprehensive monitoring, alerting and performance tracking
"""

import asyncio
import json
import logging
import psutil
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from decimal import Decimal

from sqlalchemy import and_, desc, func, text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.orders import Order, OrderStatus
from app.models.users import User

# Configure logger
logger = logging.getLogger(__name__)


class MonitoringService:
    """Advanced monitoring and alerting service"""

    def __init__(self, db: Session):
        self.db = db
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "error_rate": 5.0,
            "response_time": 2000,  # milliseconds
        }

    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health metrics"""
        
        # CPU and Memory metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network metrics
        network = psutil.net_io_counters()
        
        # Database health check
        db_health = await self._check_database_health()
        
        # Application metrics
        app_metrics = await self._get_application_metrics()
        
        return {
            "system": {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "memory_available_mb": memory.available // (1024 * 1024),
                "disk_usage_percent": (disk.used / disk.total) * 100,
                "disk_free_gb": disk.free // (1024 * 1024 * 1024),
                "network_bytes_sent": network.bytes_sent,
                "network_bytes_recv": network.bytes_recv,
            },
            "database": db_health,
            "application": app_metrics,
            "timestamp": datetime.now().isoformat(),
            "alerts": await self._check_alert_conditions(cpu_percent, memory.percent, (disk.used / disk.total) * 100)
        }

    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database connection and performance"""
        try:
            start_time = time.time()
            
            # Test database connection
            result = self.db.execute(text("SELECT 1")).scalar()
            connection_time = (time.time() - start_time) * 1000
            
            # Get database size and active connections
            db_size_query = text("""
                SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                       (SELECT count(*) FROM pg_stat_activity WHERE state = 'active') as active_connections
            """)
            
            db_stats = self.db.execute(db_size_query).fetchone()
            
            # Get slow queries (if any)
            slow_queries = self.db.execute(text("""
                SELECT query, calls, total_time, mean_time 
                FROM pg_stat_statements 
                WHERE mean_time > 1000
                ORDER BY mean_time DESC 
                LIMIT 5
            """)).fetchall() if hasattr(self.db, 'execute') else []
            
            return {
                "status": "healthy" if connection_time < 100 else "warning",
                "connection_time_ms": connection_time,
                "database_size": db_stats[0] if db_stats else "unknown",
                "active_connections": db_stats[1] if db_stats else 0,
                "slow_queries_count": len(slow_queries),
                "slow_queries": [
                    {
                        "query": q[0][:100] + "..." if len(q[0]) > 100 else q[0],
                        "calls": q[1],
                        "total_time": q[2],
                        "mean_time": q[3]
                    } for q in slow_queries
                ] if slow_queries else []
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "connection_time_ms": None
            }

    async def _get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific metrics"""
        try:
            # Get recent orders and error rates
            now = datetime.now()
            hour_ago = now - timedelta(hours=1)
            
            # Orders in last hour
            recent_orders = self.db.query(func.count(Order.id)).filter(
                Order.created_at >= hour_ago
            ).scalar() or 0
            
            # Failed orders in last hour
            failed_orders = self.db.query(func.count(Order.id)).filter(
                Order.created_at >= hour_ago,
                Order.status == OrderStatus.FAILED
            ).scalar() or 0
            
            # Calculate error rate
            error_rate = (failed_orders / recent_orders * 100) if recent_orders > 0 else 0
            
            # Active users in last hour
            active_users = self.db.query(func.count(func.distinct(Order.user_id))).filter(
                Order.created_at >= hour_ago
            ).scalar() or 0
            
            return {
                "orders_last_hour": recent_orders,
                "failed_orders_last_hour": failed_orders,
                "error_rate_percent": error_rate,
                "active_users_last_hour": active_users,
                "status": "healthy" if error_rate < self.alert_thresholds["error_rate"] else "warning"
            }
            
        except Exception as e:
            logger.error(f"Application metrics collection failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _check_alert_conditions(self, cpu: float, memory: float, disk: float) -> List[Dict[str, Any]]:
        """Check for alert conditions and return active alerts"""
        alerts = []
        
        if cpu > self.alert_thresholds["cpu_usage"]:
            alerts.append({
                "type": "cpu_high",
                "severity": "warning",
                "message": f"CPU usage is {cpu:.1f}%, exceeding threshold of {self.alert_thresholds['cpu_usage']}%",
                "value": cpu,
                "threshold": self.alert_thresholds["cpu_usage"]
            })
        
        if memory > self.alert_thresholds["memory_usage"]:
            alerts.append({
                "type": "memory_high",
                "severity": "warning",
                "message": f"Memory usage is {memory:.1f}%, exceeding threshold of {self.alert_thresholds['memory_usage']}%",
                "value": memory,
                "threshold": self.alert_thresholds["memory_usage"]
            })
        
        if disk > self.alert_thresholds["disk_usage"]:
            alerts.append({
                "type": "disk_high",
                "severity": "critical",
                "message": f"Disk usage is {disk:.1f}%, exceeding threshold of {self.alert_thresholds['disk_usage']}%",
                "value": disk,
                "threshold": self.alert_thresholds["disk_usage"]
            })
        
        return alerts

    async def get_performance_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get performance metrics over specified time period"""
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        # Simulated response time data (in real implementation, this would come from APM)
        response_times = await self._get_response_time_metrics(start_time, end_time)
        
        # Error tracking
        error_metrics = await self._get_error_metrics(start_time, end_time)
        
        # Throughput metrics
        throughput = await self._get_throughput_metrics(start_time, end_time)
        
        return {
            "period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours
            },
            "response_times": response_times,
            "errors": error_metrics,
            "throughput": throughput,
            "summary": {
                "avg_response_time": response_times.get("average", 0),
                "error_rate": error_metrics.get("error_rate", 0),
                "total_requests": throughput.get("total_requests", 0)
            }
        }

    async def _get_response_time_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get response time metrics (placeholder - would integrate with APM)"""
        # In a real implementation, this would pull from APM tools like DataDog, New Relic, etc.
        return {
            "average": 245.5,  # milliseconds
            "p50": 180.0,
            "p95": 650.0,
            "p99": 1200.0,
            "samples": 15420
        }

    async def _get_error_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get error rate and error details"""
        try:
            # Count total orders and failed orders in time period
            total_orders = self.db.query(func.count(Order.id)).filter(
                Order.created_at >= start_time,
                Order.created_at <= end_time
            ).scalar() or 0
            
            failed_orders = self.db.query(func.count(Order.id)).filter(
                Order.created_at >= start_time,
                Order.created_at <= end_time,
                Order.status == OrderStatus.FAILED
            ).scalar() or 0
            
            error_rate = (failed_orders / total_orders * 100) if total_orders > 0 else 0
            
            return {
                "error_rate": error_rate,
                "total_errors": failed_orders,
                "total_requests": total_orders,
                "error_types": {
                    "payment_failed": failed_orders,  # Simplified - would break down by error type
                    "validation_error": 0,
                    "timeout": 0,
                    "internal_error": 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error metrics collection failed: {e}")
            return {"error_rate": 0, "total_errors": 0, "total_requests": 0}

    async def _get_throughput_metrics(self, start_time: datetime, end_time: datetime) -> Dict[str, Any]:
        """Get throughput metrics"""
        try:
            # Hourly breakdown of orders
            hourly_data = self.db.query(
                func.date_trunc('hour', Order.created_at).label('hour'),
                func.count(Order.id).label('order_count')
            ).filter(
                Order.created_at >= start_time,
                Order.created_at <= end_time
            ).group_by(
                func.date_trunc('hour', Order.created_at)
            ).order_by('hour').all()
            
            total_requests = sum(count for _, count in hourly_data)
            hours_delta = (end_time - start_time).total_seconds() / 3600
            avg_per_hour = total_requests / hours_delta if hours_delta > 0 else 0
            
            return {
                "total_requests": total_requests,
                "average_per_hour": avg_per_hour,
                "peak_hour_requests": max((count for _, count in hourly_data), default=0),
                "hourly_breakdown": [
                    {
                        "hour": hour.isoformat(),
                        "requests": count
                    } for hour, count in hourly_data
                ]
            }
            
        except Exception as e:
            logger.error(f"Throughput metrics collection failed: {e}")
            return {"total_requests": 0, "average_per_hour": 0}

    async def create_alert(self, alert_type: str, severity: str, message: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create and log an alert"""
        alert = {
            "id": f"alert_{int(time.time())}_{alert_type}",
            "type": alert_type,
            "severity": severity,
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Log the alert
        logger.warning(f"ALERT [{severity.upper()}] {alert_type}: {message}")
        
        # In a real implementation, this would:
        # - Store in database
        # - Send notifications (email, Slack, etc.)
        # - Integrate with incident management systems
        
        return alert

    async def get_uptime_status(self) -> Dict[str, Any]:
        """Get uptime and availability metrics"""
        # In a real implementation, this would track actual uptime
        # For now, providing a basic structure
        
        uptime_seconds = time.time() - psutil.boot_time()
        uptime_days = uptime_seconds / (24 * 3600)
        
        return {
            "uptime_seconds": uptime_seconds,
            "uptime_days": uptime_days,
            "availability_percent": 99.9,  # Would be calculated from actual monitoring data
            "last_outage": None,
            "status": "operational"
        }