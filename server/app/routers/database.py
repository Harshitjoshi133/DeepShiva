from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.database import get_db
from app.models import *
from typing import List, Dict, Any
import json

router = APIRouter()

@router.get("/stats/overview")
async def get_database_overview(db: Session = Depends(get_db)):
    """Get comprehensive database statistics for dashboard."""
    try:
        # User statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        
        # Chat statistics
        total_chats = db.query(Chat).count()
        active_chats = db.query(Chat).filter(Chat.is_active == True).count()
        total_messages = db.query(ChatMessage).count()
        
        # Chat types distribution
        chat_types = db.query(Chat.chat_type, func.count(Chat.id)).group_by(Chat.chat_type).all()
        chat_types_dict = dict(chat_types) if chat_types else {}
        
        # Cultural statistics
        cultural_sites = db.query(CulturalSite).filter(CulturalSite.is_active == True).count()
        total_artisans = db.query(Artisan).filter(Artisan.is_active == True).count()
        verified_artisans = db.query(Artisan).filter(
            Artisan.is_active == True, 
            Artisan.is_verified == True
        ).count()
        artisan_products = db.query(ArtisanProduct).filter(ArtisanProduct.is_active == True).count()
        
        # Tourism statistics
        tourism_places = db.query(TourismPlace).filter(TourismPlace.is_active == True).count()
        tourism_categories = db.query(
            TourismPlace.category, 
            func.count(TourismPlace.id)
        ).filter(TourismPlace.is_active == True).group_by(TourismPlace.category).all()
        tourism_categories_dict = dict(tourism_categories) if tourism_categories else {}
        
        # Yoga poses
        yoga_poses = db.query(YogaPose).filter(YogaPose.is_active == True).count()
        
        # Emergency contacts
        emergency_contacts = db.query(EmergencyContact).filter(EmergencyContact.is_active == True).count()
        
        return {
            "users": {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users
            },
            "chats": {
                "total": total_chats,
                "active": active_chats,
                "messages": total_messages,
                "types": chat_types_dict
            },
            "culture": {
                "sites": cultural_sites,
                "artisans": {
                    "total": total_artisans,
                    "verified": verified_artisans,
                    "pending": total_artisans - verified_artisans
                },
                "products": artisan_products
            },
            "tourism": {
                "places": tourism_places,
                "categories": tourism_categories_dict
            },
            "yoga": {
                "poses": yoga_poses
            },
            "emergency": {
                "contacts": emergency_contacts
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/stats/recent-activity")
async def get_recent_activity(limit: int = 10, db: Session = Depends(get_db)):
    """Get recent chat activity for dashboard."""
    try:
        recent_messages = db.query(ChatMessage).order_by(
            ChatMessage.created_at.desc()
        ).limit(limit).all()
        
        activity = []
        for msg in recent_messages:
            activity.append({
                "id": msg.id,
                "user_id": msg.user_id,
                "chat_id": msg.chat_id,
                "message": msg.message[:100] + "..." if len(msg.message) > 100 else msg.message,
                "message_type": msg.message_type,
                "language": msg.language,
                "created_at": msg.created_at.isoformat()
            })
        
        return {"recent_activity": activity}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/users")
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of users."""
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        return {"users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/cultural-sites")
async def get_cultural_sites(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of cultural sites."""
    try:
        sites = db.query(CulturalSite).filter(CulturalSite.is_active == True).offset(skip).limit(limit).all()
        return {"cultural_sites": sites}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/artisans")
async def get_artisans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of artisans."""
    try:
        artisans = db.query(Artisan).filter(Artisan.is_active == True).offset(skip).limit(limit).all()
        return {"artisans": artisans}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/artisan-products")
async def get_artisan_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of artisan products."""
    try:
        products = db.query(ArtisanProduct).filter(ArtisanProduct.is_active == True).offset(skip).limit(limit).all()
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/tourism-places")
async def get_tourism_places(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of tourism places."""
    try:
        places = db.query(TourismPlace).filter(TourismPlace.is_active == True).offset(skip).limit(limit).all()
        return {"tourism_places": places}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/health")
async def database_health_check():
    """
    Comprehensive database health check with connection retry logic.
    Does not depend on get_db to avoid dependency injection issues.
    """
    from app.database import test_database_connection, get_db_with_retry
    from sqlalchemy.exc import DisconnectionError, OperationalError
    import time
    
    start_time = time.time()
    
    try:
        # Test basic connectivity
        connection_status = test_database_connection()
        
        if connection_status["status"] == "failed":
            return {
                "status": "unhealthy",
                "connection": "failed",
                "error": connection_status["error"],
                "response_time_ms": round((time.time() - start_time) * 1000, 2),
                "timestamp": time.time()
            }
        
        # Test database operations
        db = get_db_with_retry()
        
        # Test basic queries
        user_count = db.query(User).count()
        chat_count = db.query(Chat).count()
        
        # Test write operation (safe)
        db.execute(text("SELECT 1 as test_query"))
        
        db.close()
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            "status": "healthy",
            "connection": "active",
            "database_version": connection_status.get("version", "unknown"),
            "stats": {
                "users": user_count,
                "chats": chat_count
            },
            "response_time_ms": response_time,
            "timestamp": time.time(),
            "message": "Database is fully operational"
        }
        
    except (DisconnectionError, OperationalError) as db_error:
        return {
            "status": "unhealthy",
            "connection": "failed",
            "error_type": "connection_error",
            "error": str(db_error),
            "response_time_ms": round((time.time() - start_time) * 1000, 2),
            "timestamp": time.time(),
            "message": "Database connection failed"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy", 
            "connection": "unknown",
            "error_type": "general_error",
            "error": str(e),
            "response_time_ms": round((time.time() - start_time) * 1000, 2),
            "timestamp": time.time(),
            "message": "Database health check failed"
        }

@router.get("/connection-test")
async def test_database_connection_endpoint():
    """
    Simple connection test endpoint for monitoring.
    """
    from app.database import test_database_connection
    
    result = test_database_connection()
    
    if result["status"] == "connected":
        return {
            "status": "success",
            "connected": True,
            "version": result["version"],
            "timestamp": result["timestamp"]
        }
    else:
        return {
            "status": "failed",
            "connected": False,
            "error": result["error"],
            "timestamp": result["timestamp"]
        }