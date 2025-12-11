#!/usr/bin/env python3
"""
Database utility functions for Deep-Shiva project.
Provides common database operations and queries.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import SessionLocal, get_db
from app.models import *
import json
from datetime import datetime

class DatabaseUtils:
    """Utility class for database operations."""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()
    
    def get_user_stats(self):
        """Get user statistics."""
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users
        }
    
    def get_chat_stats(self):
        """Get chat statistics."""
        total_chats = self.db.query(Chat).count()
        active_chats = self.db.query(Chat).filter(Chat.is_active == True).count()
        total_messages = self.db.query(ChatMessage).count()
        
        # Chat types distribution
        chat_types = self.db.query(Chat.chat_type, func.count(Chat.id)).group_by(Chat.chat_type).all()
        
        return {
            "total_chats": total_chats,
            "active_chats": active_chats,
            "total_messages": total_messages,
            "chat_types": dict(chat_types)
        }
    
    def get_culture_stats(self):
        """Get cultural sites and artisan statistics."""
        cultural_sites = self.db.query(CulturalSite).filter(CulturalSite.is_active == True).count()
        artisans = self.db.query(Artisan).filter(Artisan.is_active == True).count()
        verified_artisans = self.db.query(Artisan).filter(
            Artisan.is_active == True, 
            Artisan.is_verified == True
        ).count()
        products = self.db.query(ArtisanProduct).filter(ArtisanProduct.is_active == True).count()
        
        return {
            "cultural_sites": cultural_sites,
            "total_artisans": artisans,
            "verified_artisans": verified_artisans,
            "artisan_products": products
        }
    
    def get_tourism_stats(self):
        """Get tourism statistics."""
        tourism_places = self.db.query(TourismPlace).filter(TourismPlace.is_active == True).count()
        
        # Places by category
        categories = self.db.query(
            TourismPlace.category, 
            func.count(TourismPlace.id)
        ).filter(TourismPlace.is_active == True).group_by(TourismPlace.category).all()
        
        return {
            "total_places": tourism_places,
            "categories": dict(categories)
        }
    
    def get_recent_activity(self, limit=10):
        """Get recent chat messages."""
        recent_messages = self.db.query(ChatMessage).order_by(
            ChatMessage.created_at.desc()
        ).limit(limit).all()
        
        return [{
            "id": msg.id,
            "user_id": msg.user_id,
            "message": msg.message[:100] + "..." if len(msg.message) > 100 else msg.message,
            "created_at": msg.created_at.isoformat(),
            "language": msg.language
        } for msg in recent_messages]
    
    def create_sample_user(self, username, email, full_name):
        """Create a sample user for testing."""
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            preferred_language="en",
            interests=["tourism", "culture"]
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_dashboard_metrics(self):
        """Update dashboard metrics with current data."""
        # Clear existing metrics for today
        today = datetime.now().date()
        self.db.query(DashboardMetrics).filter(
            func.date(DashboardMetrics.date_recorded) == today
        ).delete()
        
        # Add updated metrics
        metrics = [
            DashboardMetrics(
                metric_name="Total Users",
                metric_value=self.db.query(User).count(),
                metric_type="count",
                category="users"
            ),
            DashboardMetrics(
                metric_name="Active Chats",
                metric_value=self.db.query(Chat).filter(Chat.is_active == True).count(),
                metric_type="count",
                category="chats"
            ),
            DashboardMetrics(
                metric_name="Cultural Sites",
                metric_value=self.db.query(CulturalSite).filter(CulturalSite.is_active == True).count(),
                metric_type="count",
                category="culture"
            ),
            DashboardMetrics(
                metric_name="Tourism Places",
                metric_value=self.db.query(TourismPlace).filter(TourismPlace.is_active == True).count(),
                metric_type="count",
                category="tourism"
            ),
            DashboardMetrics(
                metric_name="Registered Artisans",
                metric_value=self.db.query(Artisan).filter(Artisan.is_active == True).count(),
                metric_type="count",
                category="culture"
            )
        ]
        
        for metric in metrics:
            self.db.add(metric)
        
        self.db.commit()
        return len(metrics)

def print_database_overview():
    """Print a comprehensive database overview."""
    with DatabaseUtils() as db_utils:
        print("=== Deep-Shiva Database Overview ===\n")
        
        # User stats
        user_stats = db_utils.get_user_stats()
        print(f"👥 Users: {user_stats['total_users']} total, {user_stats['active_users']} active")
        
        # Chat stats
        chat_stats = db_utils.get_chat_stats()
        print(f"💬 Chats: {chat_stats['total_chats']} total, {chat_stats['total_messages']} messages")
        print(f"   Types: {chat_stats.get('chat_types', {})}")
        
        # Culture stats
        culture_stats = db_utils.get_culture_stats()
        print(f"🏛️  Culture: {culture_stats['cultural_sites']} sites, {culture_stats['total_artisans']} artisans")
        print(f"   Verified artisans: {culture_stats['verified_artisans']}")
        print(f"   Products: {culture_stats['artisan_products']}")
        
        # Tourism stats
        tourism_stats = db_utils.get_tourism_stats()
        print(f"🏔️  Tourism: {tourism_stats['total_places']} places")
        print(f"   Categories: {tourism_stats.get('categories', {})}")
        
        print(f"\n📊 Dashboard metrics updated: {db_utils.update_dashboard_metrics()} entries")

if __name__ == "__main__":
    print_database_overview()