import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import chat, vision, tourism, culture, database, monitoring, yoga, meditation
from app.database import engine
from app.models import Base
from app.logging_config import setup_logging, get_logger
from app.middleware import LoggingMiddleware, SecurityMiddleware, HealthCheckMiddleware

# Setup configuration and logging
from app.config import settings, get_log_config

log_config = get_log_config()
setup_logging(log_config["environment"])

# Get logger for main application
logger = get_logger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Deep-Shiva API - Event: startup")
    
    # Create database tables (suppress verbose SQLAlchemy logs during startup)
    try:
        # Temporarily set SQLAlchemy logging to ERROR level during table creation
        import logging
        sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
        original_level = sqlalchemy_logger.level
        sqlalchemy_logger.setLevel(logging.ERROR)
        
        Base.metadata.create_all(bind=engine)
        
        # Restore original logging level
        sqlalchemy_logger.setLevel(original_level)
        
        logger.info("Database initialized successfully - Event: database_init")
    except Exception as e:
        logger.error(f"Failed to initialize database - Error: {str(e)}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Deep-Shiva API - Event: shutdown")

app = FastAPI(
    title="Deep-Shiva API",
    description="Backend API for Uttarakhand Tourism Chatbot with comprehensive logging",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware (order matters - last added is executed first)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SecurityMiddleware)
app.add_middleware(HealthCheckMiddleware)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(vision.router, prefix="/api/v1/vision", tags=["Vision"])
app.include_router(yoga.router, prefix="/api/v1/yoga", tags=["Yoga"])
app.include_router(meditation.router, prefix="/api/v1", tags=["Meditation"])
app.include_router(tourism.router, prefix="/api/v1/tourism", tags=["Tourism"])
app.include_router(culture.router, prefix="/api/v1/culture", tags=["Culture"])
app.include_router(database.router, prefix="/api/v1/database", tags=["Database"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["Monitoring"])

@app.get("/")
async def root(request: Request):
    """Root endpoint with API information"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.info(f"Root endpoint accessed - Request ID: {request_id}, Endpoint: /")
    
    return {
        "message": "Welcome to Deep-Shiva API",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "Enhanced Chat with Context Awareness",
            "Advanced Yoga Pose Analysis", 
            "AI-Guided Meditation Sessions",
            "Comprehensive Tourism Information",
            "Cultural Heritage & Artisan Support",
            "Real-time Weather & Crowd Data",
            "Carbon Footprint Calculator",
            "Multi-language Support",
            "Comprehensive Logging & Monitoring"
        ],
        "endpoints": {
            "chat": "/api/v1/chat/",
            "vision": "/api/v1/vision/",
            "yoga": "/api/v1/yoga/",
            "meditation": "/api/v1/meditation/",
            "tourism": "/api/v1/tourism/",
            "culture": "/api/v1/culture/",
            "database": "/api/v1/database/",
            "monitoring": "/api/v1/monitoring/",
            "docs": "/docs"
        },
        "logging": {
            "environment": settings.environment,
            "log_level": settings.log_level,
            "log_format": settings.log_format,
            "log_levels": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            "log_files": ["logs/app.log", "logs/error.log", "logs/access.log"]
        }
    }

@app.get("/health")
async def health_check(request: Request):
    """Enhanced health check with robust database testing"""
    from datetime import datetime
    from app.database import test_database_connection
    
    request_id = getattr(request.state, 'request_id', 'unknown')
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Test database connection using robust method
    db_test_result = test_database_connection()
    db_status = "operational" if db_test_result["status"] == "connected" else "error"
    
    if db_status == "operational":
        logger.debug(f"Database health check passed - Request ID: {request_id}")
    else:
        error_msg = db_test_result.get("error", "Unknown database error")
        logger.error(f"Database health check failed - Request ID: {request_id}, Error: {error_msg}")
    
    health_status = {
        "status": "healthy" if db_status == "operational" else "degraded",
        "timestamp": timestamp,
        "request_id": request_id,
        "services": {
            "chat": "operational",
            "vision": "operational",
            "yoga": "operational",
            "meditation": "operational",
            "tourism": "operational",
            "culture": "operational",
            "database": db_status
        },
        "system": {
            "environment": settings.environment,
            "logging": "operational",
            "debug_mode": settings.debug
        },
        "database_info": {
            "status": db_test_result["status"],
            "version": db_test_result.get("version", "unknown"),
            "error": db_test_result.get("error") if db_status == "error" else None
        }
    }
    
    logger.info(f"Health check completed - Request ID: {request_id}, Status: {health_status['status']}, Database: {db_status}")
    
    return health_status

@app.get("/stats")
async def get_api_stats():
    """
    Get API usage statistics and system information.
    
    TODO: Implement real usage tracking and metrics.
    """
    return {
        "total_endpoints": 25,
        "active_users": 1247,
        "total_queries_today": 3456,
        "popular_features": [
            {"name": "Chat Queries", "usage": "45%"},
            {"name": "Pose Analysis", "usage": "25%"},
            {"name": "Tourism Info", "usage": "20%"},
            {"name": "Culture Hub", "usage": "10%"}
        ],
        "system_info": {
            "uptime": "99.9%",
            "response_time_avg": "120ms",
            "last_updated": "2024-12-10T10:30:00Z"
        }
    }
