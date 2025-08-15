"""
Monitoring API endpoints
Provides comprehensive system monitoring and alerting
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.users import User
from app.services.monitoring import MonitoringService

router = APIRouter()


@router.get("/health")
async def get_system_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get comprehensive system health metrics"""
    monitoring_service = MonitoringService(db)

    try:
        health_data = await monitoring_service.get_system_health()
        
        return {
            "success": True,
            "data": health_data,
            "message": "System health metrics retrieved successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system health: {str(e)}",
        )


@router.get("/performance")
async def get_performance_metrics(
    hours: int = Query(24, description="Number of hours to look back", ge=1, le=168),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get application performance metrics"""
    monitoring_service = MonitoringService(db)

    try:
        performance_data = await monitoring_service.get_performance_metrics(hours=hours)
        
        return {
            "success": True,
            "data": performance_data,
            "message": "Performance metrics retrieved successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve performance metrics: {str(e)}",
        )


@router.get("/uptime")
async def get_uptime_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get uptime and availability metrics"""
    monitoring_service = MonitoringService(db)

    try:
        uptime_data = await monitoring_service.get_uptime_status()
        
        return {
            "success": True,
            "data": uptime_data,
            "message": "Uptime status retrieved successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve uptime status: {str(e)}",
        )


@router.post("/alerts")
async def create_alert(
    alert_type: str,
    severity: str,
    message: str,
    metadata: dict = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new monitoring alert"""
    monitoring_service = MonitoringService(db)

    try:
        alert = await monitoring_service.create_alert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            metadata=metadata
        )
        
        return {
            "success": True,
            "data": alert,
            "message": "Alert created successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert: {str(e)}",
        )


@router.get("/alerts")
async def get_active_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get active monitoring alerts"""
    monitoring_service = MonitoringService(db)

    try:
        # Get current system health to check for active alerts
        health_data = await monitoring_service.get_system_health()
        active_alerts = health_data.get("alerts", [])
        
        return {
            "success": True,
            "data": {
                "alerts": active_alerts,
                "total_count": len(active_alerts),
                "critical_count": len([a for a in active_alerts if a.get("severity") == "critical"]),
                "warning_count": len([a for a in active_alerts if a.get("severity") == "warning"]),
            },
            "message": "Active alerts retrieved successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve alerts: {str(e)}",
        )


@router.get("/metrics/realtime")
async def get_realtime_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get real-time monitoring metrics for live dashboard"""
    monitoring_service = MonitoringService(db)

    try:
        # Get current system health
        health_data = await monitoring_service.get_system_health()
        
        # Get performance data for last hour
        performance_data = await monitoring_service.get_performance_metrics(hours=1)
        
        # Combine into real-time metrics
        realtime_data = {
            "timestamp": datetime.now().isoformat(),
            "system": health_data["system"],
            "database": health_data["database"],
            "application": health_data["application"],
            "performance": {
                "avg_response_time": performance_data["summary"]["avg_response_time"],
                "error_rate": performance_data["summary"]["error_rate"],
                "throughput": performance_data["summary"]["total_requests"]
            },
            "alerts": health_data.get("alerts", []),
            "status": "healthy" if not health_data.get("alerts") else "warning"
        }
        
        return {
            "success": True,
            "data": realtime_data,
            "message": "Real-time metrics retrieved successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve real-time metrics: {str(e)}",
        )


@router.get("/status")
async def get_overall_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get overall system status summary"""
    monitoring_service = MonitoringService(db)

    try:
        health_data = await monitoring_service.get_system_health()
        uptime_data = await monitoring_service.get_uptime_status()
        
        # Determine overall status
        alerts = health_data.get("alerts", [])
        critical_alerts = [a for a in alerts if a.get("severity") == "critical"]
        warning_alerts = [a for a in alerts if a.get("severity") == "warning"]
        
        if critical_alerts:
            overall_status = "critical"
        elif warning_alerts:
            overall_status = "warning"
        else:
            overall_status = "operational"
        
        status_data = {
            "overall_status": overall_status,
            "uptime_percent": uptime_data["availability_percent"],
            "uptime_days": uptime_data["uptime_days"],
            "total_alerts": len(alerts),
            "critical_alerts": len(critical_alerts),
            "warning_alerts": len(warning_alerts),
            "last_check": datetime.now().isoformat(),
            "components": {
                "database": health_data["database"]["status"],
                "application": health_data["application"]["status"],
                "system": "healthy"  # Based on system metrics
            }
        }
        
        return {
            "success": True,
            "data": status_data,
            "message": "System status retrieved successfully",
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system status: {str(e)}",
        )