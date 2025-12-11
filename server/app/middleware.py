"""
Middleware for Deep-Shiva API
Handles request/response logging, performance monitoring, and error tracking
"""

import time
import uuid
import json
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

from .logging_config import get_access_logger, get_logger, PerformanceLogger, ErrorTracker

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive request/response logging"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.access_logger = get_access_logger()
        self.app_logger = get_logger("middleware")
        self.performance_logger = PerformanceLogger(self.app_logger)
        self.error_tracker = ErrorTracker(self.app_logger)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Start timing
        start_time = time.time()
        
        # Extract request information
        method = request.method
        url = str(request.url)
        path = request.url.path
        query_params = dict(request.query_params)
        headers = dict(request.headers)
        
        # Get client IP (handle proxy headers)
        client_ip = self._get_client_ip(request)
        
        # Get user agent
        user_agent = headers.get("user-agent", "Unknown")
        
        # Log request start
        self.access_logger.info(
            f"Request started: {method} {path}",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "query_params": query_params,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "event_type": "request_start"
            }
        )
        
        # Add request ID to request state for use in route handlers
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Log successful response
            self.access_logger.info(
                f"Request completed: {method} {path}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "response_time": round(process_time, 2),
                    "client_ip": client_ip,
                    "event_type": "request_complete"
                }
            )
            
            # Log performance metrics
            self.performance_logger.log_api_performance(
                endpoint=path,
                method=method,
                duration_ms=process_time,
                status_code=response.status_code
            )
            
            # Add response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{process_time:.2f}ms"
            
            return response
            
        except Exception as exc:
            # Calculate response time for error case
            process_time = (time.time() - start_time) * 1000
            
            # Log error
            self.access_logger.error(
                f"Request failed: {method} {path}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "error": str(exc),
                    "response_time": round(process_time, 2),
                    "client_ip": client_ip,
                    "event_type": "request_error"
                },
                exc_info=True
            )
            
            # Track error
            self.error_tracker.log_validation_error(exc, {
                "method": method,
                "path": path,
                "query_params": query_params
            })
            
            # Return error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "request_id": request_id,
                    "message": "An unexpected error occurred. Please try again later."
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-Response-Time": f"{process_time:.2f}ms"
                }
            )
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address, handling proxy headers"""
        # Check for forwarded headers (common in production behind load balancers)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        return request.client.host if request.client else "unknown"

class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security monitoring and rate limiting"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("security")
        self.request_counts = {}  # Simple in-memory rate limiting (use Redis in production)
        self.max_requests_per_minute = 60
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = self._get_client_ip(request)
        
        # Simple rate limiting check
        if self._is_rate_limited(client_ip):
            self.logger.warning(
                "Rate limit exceeded",
                extra={
                    "client_ip": client_ip,
                    "path": request.url.path,
                    "method": request.method,
                    "security_event": True
                }
            )
            
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": "Too many requests. Please try again later.",
                    "retry_after": 60
                }
            )
        
        # Check for suspicious patterns
        self._check_suspicious_activity(request, client_ip)
        
        # Process request
        response = await call_next(request)
        
        # Update request count
        self._update_request_count(client_ip)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _is_rate_limited(self, client_ip: str) -> bool:
        """Check if client IP is rate limited"""
        current_time = time.time()
        minute_window = int(current_time // 60)
        
        key = f"{client_ip}:{minute_window}"
        count = self.request_counts.get(key, 0)
        
        return count >= self.max_requests_per_minute
    
    def _update_request_count(self, client_ip: str):
        """Update request count for rate limiting"""
        current_time = time.time()
        minute_window = int(current_time // 60)
        
        key = f"{client_ip}:{minute_window}"
        self.request_counts[key] = self.request_counts.get(key, 0) + 1
        
        # Clean up old entries (keep only last 2 minutes)
        keys_to_remove = [
            k for k in self.request_counts.keys()
            if int(k.split(":")[1]) < minute_window - 1
        ]
        for key in keys_to_remove:
            del self.request_counts[key]
    
    def _check_suspicious_activity(self, request: Request, client_ip: str):
        """Check for suspicious request patterns"""
        path = request.url.path.lower()
        query = str(request.query_params).lower()
        
        # Check for common attack patterns
        suspicious_patterns = [
            "script", "alert", "onload", "onerror",  # XSS attempts
            "union", "select", "drop", "insert",     # SQL injection attempts
            "../", "..\\", "etc/passwd",             # Path traversal attempts
            "eval(", "exec(", "system(",             # Code injection attempts
        ]
        
        for pattern in suspicious_patterns:
            if pattern in path or pattern in query:
                self.logger.warning(
                    "Suspicious request pattern detected",
                    extra={
                        "client_ip": client_ip,
                        "path": request.url.path,
                        "method": request.method,
                        "pattern": pattern,
                        "query_params": dict(request.query_params),
                        "security_event": True
                    }
                )
                break

class HealthCheckMiddleware(BaseHTTPMiddleware):
    """Middleware for health check monitoring"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.logger = get_logger("health")
        self.health_check_paths = ["/health", "/", "/docs", "/redoc"]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip detailed logging for health check endpoints
        if request.url.path in self.health_check_paths:
            return await call_next(request)
        
        # Process normal requests
        response = await call_next(request)
        
        # Log health-related metrics
        if response.status_code >= 500:
            self.logger.error(
                "Server error detected",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                    "health_event": True
                }
            )
        
        return response