from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, vision, tourism, culture

app = FastAPI(
    title="Deep-Shiva API",
    description="Backend API for Uttarakhand Tourism Chatbot",
    version="1.0.0"
)

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

@app.get("/")
async def root():
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
            "Multi-language Support"
        ],
        "endpoints": {
            "chat": "/api/v1/chat/",
            "vision": "/api/v1/vision/",
            "tourism": "/api/v1/tourism/",
            "culture": "/api/v1/culture/",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2024-12-10T10:30:00Z",
        "services": {
            "chat": "operational",
            "vision": "operational", 
            "tourism": "operational",
            "culture": "operational"
        }
    }

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
