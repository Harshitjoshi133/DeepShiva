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
    """Enhanced middleware for comprehensive request/response logging with detailed status codes and response information"""
    
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
        
        # Extract comprehensive request information
        method = request.method
        url = str(request.url)
        path = request.url.path
        query_params = dict(request.query_params)
        headers = dict(request.headers)
        
        # Get client IP (handle proxy headers)
        client_ip = self._get_client_ip(request)
        
        # Get user agent and other useful headers
        user_agent = headers.get("user-agent", "Unknown")
        content_type = headers.get("content-type", "")
        content_length = headers.get("content-length", "0")
        
        # Read request body for POST/PUT requests (for logging purposes)
        request_body_size = 0
        request_body_preview = ""
        
        if method in ["POST", "PUT", "PATCH"] and content_type.startswith("application/json"):
            try:
                body = await request.body()
                request_body_size = len(body)
                if body:
                    # Preview first 200 chars of request body
                    body_str = body.decode('utf-8')
                    request_body_preview = body_str[:200] + "..." if len(body_str) > 200 else body_str
            except Exception:
                request_body_preview = "[Unable to read body]"
        
        # Enhanced request logging
        self.access_logger.info(
            f"🚀 REQUEST START: {method} {path}",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "full_url": url,
                "query_params": query_params,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "content_type": content_type,
                "content_length": content_length,
                "request_body_size": request_body_size,
                "request_body_preview": request_body_preview,
                "headers_count": len(headers),
                "event_type": "request_start",
                "timestamp": time.time()
            }
        )
        
        # Add request ID to request state for use in route handlers
        request.state.request_id = request_id
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate response time
            process_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            # Get response information
            response_size = 0
            response_content_type = ""
            
            # Try to get response size and content type
            if hasattr(response, 'headers'):
                response_content_type = response.headers.get("content-type", "")
                content_length_header = response.headers.get("content-length")
                if content_length_header:
                    try:
                        response_size = int(content_length_header)
                    except ValueError:
                        pass
            
            # Determine log level based on status code
            if response.status_code >= 500:
                log_level = logging.ERROR
                status_emoji = "❌"
            elif response.status_code >= 400:
                log_level = logging.WARNING
                status_emoji = "⚠️"
            elif response.status_code >= 300:
                log_level = logging.INFO
                status_emoji = "🔄"
            else:
                log_level = logging.INFO
                status_emoji = "✅"
            
            # Enhanced response logging
            self.access_logger.log(
                log_level,
                f"{status_emoji} RESPONSE: {method} {path} → {response.status_code} ({process_time:.1f}ms)",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": response.status_code,
                    "status_text": self._get_status_text(response.status_code),
                    "response_time_ms": round(process_time, 2),
                    "response_time_category": self._categorize_response_time(process_time),
                    "client_ip": client_ip,
                    "response_size_bytes": response_size,
                    "response_content_type": response_content_type,
                    "request_body_size": request_body_size,
                    "performance_rating": self._rate_performance(process_time, response.status_code),
                    "event_type": "request_complete",
                    "success": response.status_code < 400
                }
            )
            
            # Log performance metrics with more detail
            self.performance_logger.log_api_performance(
                endpoint=path,
                method=method,
                duration_ms=process_time,
                status_code=response.status_code
            )
            
            # Log slow requests with more context
            if process_time > 1000:  # Slower than 1 second
                self.app_logger.warning(
                    f"🐌 SLOW REQUEST DETECTED: {method} {path}",
                    extra={
                        "request_id": request_id,
                        "method": method,
                        "path": path,
                        "response_time_ms": round(process_time, 2),
                        "status_code": response.status_code,
                        "query_params": query_params,
                        "request_body_size": request_body_size,
                        "response_size_bytes": response_size,
                        "performance_issue": True
                    }
                )
            
            # Add comprehensive response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{process_time:.2f}ms"
            response.headers["X-Status-Category"] = self._categorize_response_time(process_time)
            
            return response
            
        except Exception as exc:
            # Calculate response time for error case
            process_time = (time.time() - start_time) * 1000
            
            # Enhanced error logging
            self.access_logger.error(
                f"💥 REQUEST FAILED: {method} {path} → {type(exc).__name__}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "error_type": type(exc).__name__,
                    "error_message": str(exc),
                    "response_time_ms": round(process_time, 2),
                    "client_ip": client_ip,
                    "query_params": query_params,
                    "request_body_size": request_body_size,
                    "request_body_preview": request_body_preview,
                    "event_type": "request_error",
                    "success": False
                },
                exc_info=True
            )
            
            # Track error with more context
            self.error_tracker.log_validation_error(exc, {
                "request_id": request_id,
                "method": method,
                "path": path,
                "query_params": query_params,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "request_body_size": request_body_size
            })
            
            # Return enhanced error response
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "error_type": type(exc).__name__,
                    "request_id": request_id,
                    "message": "An unexpected error occurred. Please try again later.",
                    "timestamp": time.time(),
                    "path": path,
                    "method": method
                },
                headers={
                    "X-Request-ID": request_id,
                    "X-Response-Time": f"{process_time:.2f}ms",
                    "X-Error-Type": type(exc).__name__
                }
            )
    
    def _get_status_text(self, status_code: int) -> str:
        """Get human-readable status text for status codes"""
        status_texts = {
            200: "OK", 201: "Created", 202: "Accepted", 204: "No Content",
            300: "Multiple Choices", 301: "Moved Permanently", 302: "Found", 304: "Not Modified",
            400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found", 
            405: "Method Not Allowed", 409: "Conflict", 422: "Unprocessable Entity", 429: "Too Many Requests",
            500: "Internal Server Error", 502: "Bad Gateway", 503: "Service Unavailable", 504: "Gateway Timeout"
        }
        return status_texts.get(status_code, f"Status {status_code}")
    
    def _categorize_response_time(self, response_time_ms: float) -> str:
        """Categorize response time for better monitoring"""
        if response_time_ms < 100:
            return "excellent"
        elif response_time_ms < 300:
            return "good"
        elif response_time_ms < 1000:
            return "acceptable"
        elif response_time_ms < 3000:
            return "slow"
        else:
            return "very_slow"
    
    def _rate_performance(self, response_time_ms: float, status_code: int) -> str:
        """Rate overall performance of the request"""
        if status_code >= 500:
            return "error"
        elif status_code >= 400:
            return "client_error"
        elif response_time_ms > 3000:
            return "poor"
        elif response_time_ms > 1000:
            return "fair"
        elif response_time_ms > 300:
            return "good"
        else:
            return "excellent"
    
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