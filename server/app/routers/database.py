from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
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
async def database_health_check(db: Session = Depends(get_db)):
    """Check database connectivity and basic stats."""
    try:
        # Simple query to test connection
        user_count = db.query(User).count()
        return {
            "status": "healthy",
            "connection": "active",
            "sample_count": user_count,
            "message": "Database is accessible and responding"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database health check failed: {str(e)}")