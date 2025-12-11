# Deep-Shiva API Logging System

## Overview

The Deep-Shiva API now includes a comprehensive logging system that provides:

- **Structured Logging**: JSON-formatted logs for production, colored console logs for development
- **Request/Response Tracking**: Complete request lifecycle monitoring with unique request IDs
- **Performance Monitoring**: Response time tracking and slow query detection
- **Error Tracking**: Detailed error logging with context and stack traces
- **Security Monitoring**: Rate limiting and suspicious activity detection
- **Log Management**: Automatic log rotation and cleanup utilities

## Log Files

The logging system creates the following log files in the `logs/` directory:

- `app.log` - General application logs (INFO level and above)
- `error.log` - Error logs only (ERROR and CRITICAL levels)
- `access.log` - HTTP request/response logs

## Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational messages
- **WARNING**: Warning messages for potential issues
- **ERROR**: Error messages for handled exceptions
- **CRITICAL**: Critical errors that may cause system failure

## Configuration

### Environment Variables

You can configure logging behavior using environment variables with the `DEEP_SHIVA_` prefix:

```bash
# Logging configuration
DEEP_SHIVA_LOG_LEVEL=INFO
DEEP_SHIVA_LOG_FORMAT=json
DEEP_SHIVA_ENVIRONMENT=production

# Performance thresholds
DEEP_SHIVA_SLOW_QUERY_THRESHOLD=1000.0
DEEP_SHIVA_SLOW_API_THRESHOLD=2000.0

# Security settings
DEEP_SHIVA_RATE_LIMIT_REQUESTS=60
DEEP_SHIVA_RATE_LIMIT_WINDOW=60
```

### Development vs Production

**Development Mode:**
- Colored console output
- DEBUG level logging
- Detailed error messages
- Pretty-printed JSON responses

**Production Mode:**
- JSON-formatted logs
- INFO level logging
- Structured error responses
- Performance optimizations

## Monitoring Endpoints

The API provides several monitoring endpoints:

### GET /api/v1/monitoring/logs
Get recent log entries with filtering options:
```bash
# Get last 100 logs
curl "http://localhost:8000/api/v1/monitoring/logs"

# Filter by log level
curl "http://localhost:8000/api/v1/monitoring/logs?level=ERROR"

# Filter by endpoint
curl "http://localhost:8000/api/v1/monitoring/logs?endpoint=/api/v1/chat"
```

### GET /api/v1/monitoring/stats
Get API usage statistics:
```bash
curl "http://localhost:8000/api/v1/monitoring/stats"
```

### GET /api/v1/monitoring/health-detailed
Get detailed system health information:
```bash
curl "http://localhost:8000/api/v1/monitoring/health-detailed"
```

### GET /api/v1/monitoring/performance-metrics
Get performance metrics for API endpoints:
```bash
curl "http://localhost:8000/api/v1/monitoring/performance-metrics"
```

## Log Format

### JSON Log Format (Production)
```json
{
  "timestamp": "2024-12-11T10:30:00.123Z",
  "level": "INFO",
  "logger": "deep_shiva.chat",
  "message": "Chat query processed successfully",
  "module": "chat",
  "function": "chat_query",
  "line": 45,
  "request_id": "abc12345",
  "user_id": "user_123",
  "endpoint": "/api/v1/chat/query",
  "response_time_ms": 234.5
}
```

### Console Log Format (Development)
```
[INFO] 10:30:00 | deep_shiva.chat | Chat query processed successfully [req_id=abc12345, user=user_123, time=234.5ms]
```

## Request Tracking

Every HTTP request gets a unique request ID that's:
- Generated automatically by the logging middleware
- Included in all log entries for that request
- Returned in the `X-Request-ID` response header
- Used to trace the complete request lifecycle

## Performance Monitoring

The system automatically tracks:
- **Response Times**: All API endpoints are timed
- **Slow Queries**: Database queries exceeding thresholds
- **Error Rates**: Percentage of failed requests
- **Endpoint Usage**: Most frequently used endpoints

### Performance Alerts

Automatic alerts are generated for:
- API responses slower than 2 seconds
- Database queries slower than 1 second
- Error rates above 5%
- High memory usage from log files

## Security Monitoring

The security middleware monitors for:
- **Rate Limiting**: Prevents abuse with configurable limits
- **Suspicious Patterns**: Detects common attack patterns
- **Authentication Failures**: Tracks failed login attempts
- **Unusual Activity**: Flags abnormal usage patterns

## Error Tracking

Comprehensive error tracking includes:
- **Validation Errors**: Input validation failures
- **Database Errors**: Database connection and query issues
- **External API Errors**: Third-party service failures
- **System Errors**: Unexpected application errors

Each error log includes:
- Full stack trace
- Request context
- User information
- Error categorization

## Log Management

### Automatic Log Rotation

Logs are automatically rotated when they reach 10MB:
- Up to 5 backup files are kept
- Old files are compressed
- Automatic cleanup prevents disk space issues

### Manual Log Cleanup

Use the monitoring API to clean up old logs:
```bash
# Keep logs from last 7 days
curl -X POST "http://localhost:8000/api/v1/monitoring/clear-logs?days_to_keep=7"
```

## Best Practices

### For Developers

1. **Use Structured Logging**: Include relevant context in log messages
2. **Log at Appropriate Levels**: Don't overuse DEBUG or ERROR levels
3. **Include Request IDs**: Always include request context when available
4. **Avoid Sensitive Data**: Never log passwords, tokens, or personal data

### For Operations

1. **Monitor Log Files**: Set up alerts for log file size and error rates
2. **Regular Cleanup**: Implement automated log cleanup policies
3. **Performance Monitoring**: Watch for slow endpoints and optimize
4. **Security Alerts**: Monitor for suspicious activity patterns

## Integration Examples

### Adding Logging to New Endpoints

```python
from app.logging_config import get_logger, PerformanceLogger
import time

router = APIRouter()
logger = get_logger("my_module")
performance_logger = PerformanceLogger(logger)

@router.post("/my-endpoint")
async def my_endpoint(request: MyRequest, http_request: Request):
    start_time = time.time()
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    
    logger.info("Processing request", extra={
        "request_id": request_id,
        "user_id": request.user_id
    })
    
    try:
        # Your business logic here
        result = process_request(request)
        
        processing_time = (time.time() - start_time) * 1000
        logger.info("Request processed successfully", extra={
            "request_id": request_id,
            "processing_time_ms": processing_time
        })
        
        return result
        
    except Exception as e:
        logger.error("Request processing failed", extra={
            "request_id": request_id,
            "error": str(e)
        }, exc_info=True)
        raise
```

### Custom Performance Monitoring

```python
# Log slow operations
if processing_time > 1000:
    performance_logger.log_api_performance(
        endpoint="/my-endpoint",
        method="POST", 
        duration_ms=processing_time,
        status_code=200
    )
```

## Troubleshooting

### Common Issues

1. **Log Files Not Created**: Check directory permissions for `logs/` folder
2. **High Disk Usage**: Implement log rotation and cleanup policies
3. **Performance Impact**: Adjust log levels in production
4. **Missing Request IDs**: Ensure middleware is properly configured

### Debug Mode

Enable debug logging for troubleshooting:
```bash
export DEEP_SHIVA_LOG_LEVEL=DEBUG
export DEEP_SHIVA_DEBUG=true
```

This comprehensive logging system provides full visibility into your API's operation, performance, and security, making it easier to maintain and troubleshoot in production environments.