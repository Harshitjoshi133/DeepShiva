"""
Simplified logging configuration for Deep-Shiva API
Provides structured logging with different levels, request tracking, and performance monitoring
"""

import logging
import logging.config
import sys
import os
import json
from datetime import datetime
from typing import Any, Dict
from pathlib import Path

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        if hasattr(record, 'method'):
            log_entry['method'] = record.method
        if hasattr(record, 'status_code'):
            log_entry['status_code'] = record.status_code
        if hasattr(record, 'response_time'):
            log_entry['response_time_ms'] = record.response_time
        if hasattr(record, 'error_type'):
            log_entry['error_type'] = record.error_type
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)

class SimpleConsoleFormatter(logging.Formatter):
    """Simple console formatter for development"""
    
    def format(self, record: logging.LogRecord) -> str:
        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Build log message
        log_parts = [
            f"[{record.levelname}]",
            f"{timestamp}",
            f"{record.name}",
            f"{record.getMessage()}"
        ]
        
        # Add extra context if available
        extras = []
        if hasattr(record, 'request_id'):
            extras.append(f"req_id={record.request_id}")
        if hasattr(record, 'user_id'):
            extras.append(f"user={record.user_id}")
        if hasattr(record, 'response_time'):
            extras.append(f"time={record.response_time}ms")
        
        if extras:
            log_parts.append(f"[{', '.join(extras)}]")
        
        return " | ".join(log_parts)

def setup_logging(environment: str = "development") -> None:
    """
    Setup logging configuration based on environment
    
    Args:
        environment: "development", "production", or "testing"
    """
    
    # Logging configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
            },
            "console": {
                "()": SimpleConsoleFormatter,
            },
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO" if environment == "production" else "DEBUG",
                "formatter": "simple" if environment == "development" else "json",
                "stream": sys.stdout,
            },
            "file_info": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
            "file_error": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "json",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf8",
            },
            "file_access": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "json",
                "filename": "logs/access.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 10,
                "encoding": "utf8",
            }
        },
        "loggers": {
            "deep_shiva": {
                "level": "DEBUG" if environment == "development" else "INFO",
                "handlers": ["console", "file_info", "file_error"],
                "propagate": False,
            },
            "deep_shiva.access": {
                "level": "INFO",
                "handlers": ["file_access"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["file_access"],
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "level": "INFO" if os.getenv("SQLALCHEMY_VERBOSE", "false").lower() == "true" else "WARNING",
                "handlers": ["file_info"] if os.getenv("SQLALCHEMY_VERBOSE", "false").lower() != "true" else ["console", "file_info"],
                "propagate": False,
            },
            "sqlalchemy.pool": {
                "level": "WARNING",  # Quiet connection pool logs
                "handlers": ["file_info"],
                "propagate": False,
            },
            "sqlalchemy.dialects": {
                "level": "WARNING",  # Quiet dialect logs
                "handlers": ["file_info"],
                "propagate": False,
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"],
        }
    }
    
    logging.config.dictConfig(config)

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name"""
    return logging.getLogger(f"deep_shiva.{name}")

def get_access_logger() -> logging.Logger:
    """Get the access logger for request/response logging"""
    return logging.getLogger("deep_shiva.access")

# Performance monitoring utilities
class PerformanceLogger:
    """Utility class for performance monitoring"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_slow_query(self, query: str, duration_ms: float, threshold_ms: float = 1000):
        """Log slow database queries"""
        if duration_ms > threshold_ms:
            self.logger.warning(
                "Slow database query detected",
                extra={
                    "query": query[:200] + "..." if len(query) > 200 else query,
                    "duration_ms": duration_ms,
                    "threshold_ms": threshold_ms
                }
            )
    
    def log_api_performance(self, endpoint: str, method: str, duration_ms: float, status_code: int):
        """Log API endpoint performance"""
        level = logging.WARNING if duration_ms > 2000 else logging.INFO
        self.logger.log(
            level,
            f"API call completed: {method} {endpoint}",
            extra={
                "endpoint": endpoint,
                "method": method,
                "response_time": duration_ms,
                "status_code": status_code
            }
        )

# Error tracking utilities
class ErrorTracker:
    """Utility class for error tracking and monitoring"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_validation_error(self, error: Exception, request_data: Dict[str, Any]):
        """Log validation errors with request context"""
        self.logger.error(
            "Validation error occurred",
            extra={
                "error_type": "ValidationError",
                "error_message": str(error),
                "request_data": request_data
            },
            exc_info=True
        )
    
    def log_database_error(self, error: Exception, operation: str):
        """Log database errors"""
        self.logger.error(
            f"Database error during {operation}",
            extra={
                "error_type": "DatabaseError",
                "operation": operation,
                "error_message": str(error)
            },
            exc_info=True
        )
    
    def log_external_api_error(self, error: Exception, service: str, endpoint: str):
        """Log external API errors"""
        self.logger.error(
            f"External API error: {service}",
            extra={
                "error_type": "ExternalAPIError",
                "service": service,
                "endpoint": endpoint,
                "error_message": str(error)
            },
            exc_info=True
        )

# Security logging utilities
class SecurityLogger:
    """Utility class for security-related logging"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
    
    def log_suspicious_activity(self, user_id: str, activity: str, details: Dict[str, Any]):
        """Log suspicious user activity"""
        self.logger.warning(
            f"Suspicious activity detected: {activity}",
            extra={
                "user_id": user_id,
                "activity": activity,
                "details": details,
                "security_event": True
            }
        )
    
    def log_rate_limit_exceeded(self, user_id: str, endpoint: str, attempts: int):
        """Log rate limit violations"""
        self.logger.warning(
            "Rate limit exceeded",
            extra={
                "user_id": user_id,
                "endpoint": endpoint,
                "attempts": attempts,
                "security_event": True
            }
        )
    
    def log_authentication_failure(self, user_id: str, reason: str):
        """Log authentication failures"""
        self.logger.warning(
            "Authentication failure",
            extra={
                "user_id": user_id,
                "reason": reason,
                "security_event": True
            }
        )