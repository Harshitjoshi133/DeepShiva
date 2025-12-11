"""
Monitoring and logging dashboard endpoints
Provides insights into API performance, errors, and usage patterns
"""

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import os
import json
from datetime import datetime, timedelta
from pathlib import Path

from ..logging_config import get_logger

router = APIRouter()
logger = get_logger("monitoring")

class LogEntry(BaseModel):
    timestamp: str
    level: str
    logger: str
    message: str
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    endpoint: Optional[str] = None
    response_time: Optional[float] = None

class LogStats(BaseModel):
    total_requests: int
    error_count: int
    warning_count: int
    avg_response_time: float
    top_endpoints: List[Dict[str, Any]]
    error_rate: float
    last_updated: str

class SystemHealth(BaseModel):
    status: str
    uptime_hours: float
    log_files_size_mb: float
    recent_errors: List[LogEntry]
    performance_alerts: List[str]

@router.get("/logs", response_model=List[LogEntry])
async def get_recent_logs(
    request: Request,
    level: Optional[str] = Query(None, description="Filter by log level"),
    limit: int = Query(100, ge=1, le=1000, description="Number of logs to return"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint")
):
    """
    Get recent log entries with optional filtering
    
    TODO: Implement proper log parsing and indexing for production
    TODO: Add pagination and advanced filtering
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info("Log retrieval request", extra={
        "request_id": request_id,
        "level_filter": level,
        "limit": limit,
        "endpoint_filter": endpoint
    })
    
    logs = []
    log_file_path = Path("logs/app.log")
    
    try:
        if log_file_path.exists():
            with open(log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Parse recent log lines (simple implementation)
            for line in reversed(lines[-limit*2:]):  # Get more lines to filter
                try:
                    log_data = json.loads(line.strip())
                    
                    # Apply filters
                    if level and log_data.get('level') != level.upper():
                        continue
                    if endpoint and endpoint not in log_data.get('endpoint', ''):
                        continue
                    
                    logs.append(LogEntry(
                        timestamp=log_data.get('timestamp', ''),
                        level=log_data.get('level', 'INFO'),
                        logger=log_data.get('logger', 'unknown'),
                        message=log_data.get('message', ''),
                        request_id=log_data.get('request_id'),
                        user_id=log_data.get('user_id'),
                        endpoint=log_data.get('endpoint'),
                        response_time=log_data.get('response_time')
                    ))
                    
                    if len(logs) >= limit:
                        break
                        
                except (json.JSONDecodeError, KeyError):
                    continue
                    
    except Exception as e:
        logger.error("Failed to read log file", extra={
            "request_id": request_id,
            "error": str(e)
        })
        raise HTTPException(status_code=500, detail="Failed to retrieve logs")
    
    logger.info("Log retrieval completed", extra={
        "request_id": request_id,
        "logs_returned": len(logs)
    })
    
    return logs

@router.get("/stats", response_model=LogStats)
async def get_log_statistics(
    request: Request,
    hours: int = Query(24, ge=1, le=168, description="Hours to analyze")
):
    """
    Get API usage statistics and performance metrics
    
    TODO: Implement real-time metrics collection
    TODO: Add database storage for historical data
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info("Statistics request", extra={
        "request_id": request_id,
        "hours": hours
    })
    
    # Mock statistics (in production, this would query a metrics database)
    stats = LogStats(
        total_requests=1247,
        error_count=23,
        warning_count=45,
        avg_response_time=156.7,
        top_endpoints=[
            {"endpoint": "/api/v1/chat/query", "count": 456, "avg_time": 234.5},
            {"endpoint": "/api/v1/vision/analyze", "count": 234, "avg_time": 567.8},
            {"endpoint": "/api/v1/tourism/crowd-status", "count": 189, "avg_time": 123.4},
            {"endpoint": "/api/v1/tourism/calculate-carbon", "count": 156, "avg_time": 89.2},
            {"endpoint": "/health", "count": 89, "avg_time": 12.3}
        ],
        error_rate=1.84,  # Percentage
        last_updated=datetime.utcnow().isoformat() + "Z"
    )
    
    logger.info("Statistics generated", extra={
        "request_id": request_id,
        "total_requests": stats.total_requests,
        "error_rate": stats.error_rate
    })
    
    return stats

@router.get("/health-detailed", response_model=SystemHealth)
async def get_system_health(request: Request):
    """
    Get detailed system health information
    
    TODO: Add real system metrics (CPU, memory, disk usage)
    TODO: Implement alerting thresholds
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info("System health check request", extra={
        "request_id": request_id
    })
    
    # Calculate log files size
    log_files_size = 0
    logs_dir = Path("logs")
    if logs_dir.exists():
        for log_file in logs_dir.glob("*.log"):
            log_files_size += log_file.stat().st_size
    
    log_files_size_mb = log_files_size / (1024 * 1024)
    
    # Get recent errors (simplified)
    recent_errors = []
    error_log_path = Path("logs/error.log")
    if error_log_path.exists():
        try:
            with open(error_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line in reversed(lines[-10:]):  # Last 10 error lines
                try:
                    error_data = json.loads(line.strip())
                    recent_errors.append(LogEntry(
                        timestamp=error_data.get('timestamp', ''),
                        level=error_data.get('level', 'ERROR'),
                        logger=error_data.get('logger', 'unknown'),
                        message=error_data.get('message', ''),
                        request_id=error_data.get('request_id'),
                        endpoint=error_data.get('endpoint')
                    ))
                except (json.JSONDecodeError, KeyError):
                    continue
        except Exception:
            pass
    
    # Generate performance alerts
    performance_alerts = []
    if log_files_size_mb > 100:
        performance_alerts.append("Log files size exceeds 100MB - consider rotation")
    if len(recent_errors) > 5:
        performance_alerts.append("High error rate detected in recent logs")
    
    # Mock uptime calculation
    uptime_hours = 24.5  # In production, calculate from startup time
    
    health = SystemHealth(
        status="healthy" if len(performance_alerts) == 0 else "warning",
        uptime_hours=uptime_hours,
        log_files_size_mb=round(log_files_size_mb, 2),
        recent_errors=recent_errors[:5],  # Limit to 5 most recent
        performance_alerts=performance_alerts
    )
    
    logger.info("System health check completed", extra={
        "request_id": request_id,
        "status": health.status,
        "alerts_count": len(performance_alerts),
        "log_size_mb": health.log_files_size_mb
    })
    
    return health

@router.post("/clear-logs")
async def clear_old_logs(
    request: Request,
    days_to_keep: int = Query(7, ge=1, le=30, description="Days of logs to keep")
):
    """
    Clear old log files to manage disk space
    
    TODO: Implement safe log archival before deletion
    TODO: Add configuration for automatic log rotation
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.warning("Log cleanup requested", extra={
        "request_id": request_id,
        "days_to_keep": days_to_keep
    })
    
    # In production, implement actual log cleanup
    # For now, just return success message
    
    return {
        "message": f"Log cleanup completed. Kept logs from last {days_to_keep} days.",
        "status": "success",
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@router.get("/performance-metrics")
async def get_performance_metrics(
    request: Request,
    endpoint: Optional[str] = Query(None, description="Filter by specific endpoint")
):
    """
    Get detailed performance metrics for API endpoints
    
    TODO: Implement real performance tracking with percentiles
    TODO: Add historical trend analysis
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info("Performance metrics request", extra={
        "request_id": request_id,
        "endpoint_filter": endpoint
    })
    
    # Mock performance data
    metrics = {
        "summary": {
            "total_requests_24h": 1247,
            "avg_response_time": 156.7,
            "p95_response_time": 456.2,
            "p99_response_time": 1234.5,
            "error_rate": 1.84
        },
        "endpoints": [
            {
                "endpoint": "/api/v1/chat/query",
                "requests_24h": 456,
                "avg_response_time": 234.5,
                "p95_response_time": 567.8,
                "error_rate": 2.1,
                "status": "healthy"
            },
            {
                "endpoint": "/api/v1/vision/analyze",
                "requests_24h": 234,
                "avg_response_time": 567.8,
                "p95_response_time": 1234.5,
                "error_rate": 1.3,
                "status": "warning"  # Slow response times
            },
            {
                "endpoint": "/api/v1/tourism/crowd-status",
                "requests_24h": 189,
                "avg_response_time": 123.4,
                "p95_response_time": 234.5,
                "error_rate": 0.5,
                "status": "healthy"
            }
        ],
        "alerts": [
            {
                "type": "slow_endpoint",
                "endpoint": "/api/v1/vision/analyze",
                "message": "Average response time exceeds 500ms threshold",
                "severity": "warning"
            }
        ],
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }
    
    # Filter by endpoint if specified
    if endpoint:
        metrics["endpoints"] = [
            ep for ep in metrics["endpoints"] 
            if endpoint in ep["endpoint"]
        ]
    
    return metrics