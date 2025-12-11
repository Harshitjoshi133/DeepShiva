import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import chat, vision, tourism, culture, database, monitoring
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
    logger.info("Starting Deep-Shiva API", extra={"event": "startup"})
    
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
        
        logger.info("Database initialized successfully", extra={"event": "database_init"})
    except Exception as e:
        logger.error("Failed to initialize database", extra={"error": str(e)}, exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Deep-Shiva API", extra={"event": "shutdown"})

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
app.include_router(tourism.router, prefix="/api/v1/tourism", tags=["Tourism"])
app.include_router(culture.router, prefix="/api/v1/culture", tags=["Culture"])
app.include_router(database.router, prefix="/api/v1/database", tags=["Database"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["Monitoring"])

@app.get("/")
async def root(request: Request):
    """Root endpoint with API information"""
    logger.info("Root endpoint accessed", extra={
        "request_id": getattr(request.state, 'request_id', 'unknown'),
        "endpoint": "/"
    })
    
    return {
        "message": "Welcome to Deep-Shiva API",
        "version": "1.0.0",
        "status": "operational",
        "features": [
            "Enhanced Chat with Context Awareness",
            "Advanced Yoga Pose Analysis", 
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
    """Enhanced health check with logging"""
    from datetime import datetime
    
    request_id = getattr(request.state, 'request_id', 'unknown')
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    # Test database connection
    db_status = "operational"
    try:
        # Simple database connectivity test (modern SQLAlchemy approach)
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        logger.debug("Database health check passed", extra={"request_id": request_id})
    except Exception as e:
        db_status = "error"
        logger.error("Database health check failed", extra={
            "request_id": request_id,
            "error": str(e)
        })
    
    health_status = {
        "status": "healthy" if db_status == "operational" else "degraded",
        "timestamp": timestamp,
        "request_id": request_id,
        "services": {
            "chat": "operational",
            "vision": "operational",
            "tourism": "operational", 
            "culture": "operational",
            "database": db_status
        },
        "system": {
            "environment": settings.environment,
            "logging": "operational",
            "debug_mode": settings.debug
        }
    }
    
    logger.info("Health check completed", extra={
        "request_id": request_id,
        "status": health_status["status"],
        "db_status": db_status
    })
    
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
