"""
Performance monitoring API endpoints
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import time
import psutil
import json
import logging
from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.core.cache import get_cache_health, cache_stats
from app.core.config import settings
from app.models.users import User

router = APIRouter()

@router.get("/health")
async def get_performance_health(
    current_user: User = Depends(get_current_admin_user),
):
    """Get overall system performance health"""
    
    # Get cache health
    cache_health = await get_cache_health()
    
    # Get system metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "cache": cache_health,
        "system": {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used,
            },
            "disk": {
                "total": disk.total,
                "free": disk.free,
                "used": disk.used,
                "percent": (disk.used / disk.total) * 100,
            },
        },
    }

@router.get("/database")
async def get_database_performance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Get database performance metrics"""
    
    try:
        # Test database connection speed
        start_time = time.time()
        await db.execute(text("SELECT 1"))
        connection_time = time.time() - start_time
        
        # Get database size
        size_result = await db.execute(text("""
            SELECT pg_size_pretty(pg_database_size(current_database())) as size
        """))
        db_size = size_result.scalar()
        
        # Get active connections
        connections_result = await db.execute(text("""
            SELECT count(*) as active_connections 
            FROM pg_stat_activity 
            WHERE state = 'active'
        """))
        active_connections = connections_result.scalar()
        
        # Get slow queries (queries running for more than 1 second)
        slow_queries_result = await db.execute(text("""
            SELECT count(*) as slow_queries
            FROM pg_stat_activity 
            WHERE state = 'active' 
            AND now() - query_start > interval '1 second'
        """))
        slow_queries = slow_queries_result.scalar()
        
        return {
            "status": "healthy",
            "connection_time_ms": round(connection_time * 1000, 2),
            "database_size": db_size,
            "active_connections": active_connections,
            "slow_queries": slow_queries,
            "max_connections": "100",  # Default PostgreSQL setting
        }
        
    except Exception as e:
        logging.exception("Error in get_database_performance")
        return {
            "status": "error",
            "error": "An internal error has occurred.",
        }

@router.get("/slow-queries")
async def get_slow_queries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
    limit: int = Query(10, le=50),
):
    """Get current slow running queries"""
    
    try:
        result = await db.execute(text("""
            SELECT 
                pid,
                now() - query_start as duration,
                query,
                state,
                application_name
            FROM pg_stat_activity 
            WHERE state = 'active' 
            AND now() - query_start > interval '1 second'
            ORDER BY duration DESC
            LIMIT :limit
        """), {"limit": limit})
        
        slow_queries = []
        for row in result:
            slow_queries.append({
                "pid": row.pid,
                "duration_seconds": str(row.duration),
                "query": row.query[:200] + "..." if len(row.query) > 200 else row.query,
                "state": row.state,
                "application_name": row.application_name,
            })
        
        return {
            "slow_queries": slow_queries,
            "count": len(slow_queries),
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "slow_queries": [],
            "count": 0,
        }

@router.get("/cache-stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_admin_user),
):
    """Get detailed cache statistics"""
    
    cache_health = await get_cache_health()
    
    return {
        "cache_health": cache_health,
        "application_stats": cache_stats.get_stats(),
        "recommendations": _get_cache_recommendations(cache_stats),
    }

@router.post("/cache/clear")
async def clear_cache(
    pattern: str = Query("*", description="Cache key pattern to clear"),
    current_user: User = Depends(get_current_admin_user),
):
    """Clear cache by pattern (admin only)"""
    
    from app.core.cache import cache_manager
    
    try:
        success = await cache_manager.delete(pattern)
        return {
            "success": success,
            "pattern": pattern,
            "message": f"Cache cleared for pattern: {pattern}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {e}")

@router.get("/metrics/summary")
async def get_metrics_summary(
    current_user: User = Depends(get_current_admin_user),
):
    """Get performance metrics summary"""
    
    # Get various metrics
    cache_health = await get_cache_health()
    
    # Calculate performance scores
    cache_score = _calculate_cache_score(cache_stats)
    
    return {
        "performance_score": _calculate_overall_score(cache_score),
        "cache_score": cache_score,
        "recommendations": _get_performance_recommendations(cache_stats),
        "alerts": _get_performance_alerts(),
    }

def _calculate_cache_score(stats) -> int:
    """Calculate cache performance score (0-100)"""
    hit_rate = stats.hit_rate
    if hit_rate >= 90:
        return 100
    elif hit_rate >= 80:
        return 90
    elif hit_rate >= 70:
        return 80
    elif hit_rate >= 60:
        return 70
    else:
        return 50

def _calculate_overall_score(cache_score: int) -> int:
    """Calculate overall performance score"""
    # For now, just use cache score
    # In production, you'd combine multiple metrics
    return cache_score

def _get_cache_recommendations(stats) -> List[str]:
    """Get cache optimization recommendations"""
    recommendations = []
    
    if stats.hit_rate < 80:
        recommendations.append("Consider increasing cache TTL for frequently accessed data")
    
    if stats.errors > 0:
        recommendations.append("Check Redis connection and error logs")
    
    if stats.hits == 0 and stats.misses == 0:
        recommendations.append("Cache appears to be unused - verify cache integration")
    
    return recommendations

def _get_performance_recommendations(stats) -> List[str]:
    """Get general performance recommendations"""
    recommendations = []
    
    # Add cache recommendations
    recommendations.extend(_get_cache_recommendations(stats))
    
    # Add other performance recommendations
    recommendations.append("Monitor database query performance regularly")
    recommendations.append("Consider implementing CDN for static assets")
    
    return recommendations

def _get_performance_alerts() -> List[Dict[str, Any]]:
    """Get current performance alerts"""
    alerts = []
    
    # Check system resources
    memory = psutil.virtual_memory()
    if memory.percent > 85:
        alerts.append({
            "type": "warning",
            "message": f"High memory usage: {memory.percent}%",
            "metric": "memory",
            "value": memory.percent,
            "threshold": 85,
        })
    
    cpu_percent = psutil.cpu_percent()
    if cpu_percent > 80:
        alerts.append({
            "type": "warning",
            "message": f"High CPU usage: {cpu_percent}%",
            "metric": "cpu",
            "value": cpu_percent,
            "threshold": 80,
        })
    
    return alerts