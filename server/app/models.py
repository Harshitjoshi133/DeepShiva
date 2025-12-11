from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=True)
    preferred_language = Column(String(10), default="en")
    location = Column(String(100), nullable=True)
    interests = Column(JSON, nullable=True)  # Store as JSON array
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    chats = relationship("Chat", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")

class Chat(Base):
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=True)
    chat_type = Column(String(50), default="general")  # general, tourism, culture, yoga, emergency
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="chats")
    messages = relationship("ChatMessage", back_populates="chat")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    message_type = Column(String(20), default="text")  # text, image, voice
    language = Column(String(10), default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chat = relationship("Chat", back_populates="messages")
    user = relationship("User", back_populates="chat_messages")

class CulturalSite(Base):
    __tablename__ = "cultural_sites"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(200), nullable=False)
    district = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    category = Column(String(50), nullable=False)  # temple, heritage, monument, etc.
    historical_significance = Column(Text, nullable=True)
    visiting_hours = Column(String(100), nullable=True)
    entry_fee = Column(String(50), nullable=True)
    best_time_to_visit = Column(String(100), nullable=True)
    images = Column(JSON, nullable=True)  # Array of image URLs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class Artisan(Base):
    __tablename__ = "artisans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    location = Column(String(200), nullable=False)
    district = Column(String(100), nullable=False)
    specialization = Column(String(100), nullable=False)  # woodwork, textiles, pottery, etc.
    experience_years = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    profile_image = Column(String(500), nullable=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    products = relationship("ArtisanProduct", back_populates="artisan")

class ArtisanProduct(Base):
    __tablename__ = "artisan_products"
    
    id = Column(Integer, primary_key=True, index=True)
    artisan_id = Column(Integer, ForeignKey("artisans.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False)
    price = Column(Float, nullable=True)
    currency = Column(String(10), default="INR")
    materials_used = Column(Text, nullable=True)
    dimensions = Column(String(100), nullable=True)
    weight = Column(String(50), nullable=True)
    images = Column(JSON, nullable=True)  # Array of image URLs
    availability_status = Column(String(20), default="available")  # available, sold, custom_order
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    artisan = relationship("Artisan", back_populates="products")

class TourismPlace(Base):
    __tablename__ = "tourism_places"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    location = Column(String(200), nullable=False)
    district = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    category = Column(String(50), nullable=False)  # hill_station, temple, adventure, wildlife, etc.
    altitude = Column(Integer, nullable=True)  # in meters
    best_time_to_visit = Column(String(100), nullable=True)
    activities = Column(JSON, nullable=True)  # Array of activities
    accommodation_options = Column(JSON, nullable=True)
    transportation = Column(Text, nullable=True)
    entry_fee = Column(String(50), nullable=True)
    images = Column(JSON, nullable=True)  # Array of image URLs
    weather_info = Column(JSON, nullable=True)
    crowd_level = Column(String(20), default="moderate")  # low, moderate, high
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class YogaPose(Base):
    __tablename__ = "yoga_poses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    sanskrit_name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    difficulty_level = Column(String(20), nullable=False)  # beginner, intermediate, advanced
    category = Column(String(50), nullable=False)  # standing, sitting, lying, balancing, etc.
    benefits = Column(JSON, nullable=True)  # Array of benefits
    instructions = Column(JSON, nullable=True)  # Step-by-step instructions
    precautions = Column(Text, nullable=True)
    duration = Column(String(50), nullable=True)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

class EmergencyContact(Base):
    __tablename__ = "emergency_contacts"
    
    id = Column(Integer, primary_key=True, index=True)
    district = Column(String(100), nullable=False)
    service_type = Column(String(50), nullable=False)  # police, hospital, fire, tourist_helpline
    name = Column(String(200), nullable=False)
    phone_number = Column(String(20), nullable=False)
    address = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_24x7 = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class DashboardMetrics(Base):
    __tablename__ = "dashboard_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50), nullable=False)  # count, percentage, rating, etc.
    category = Column(String(50), nullable=False)  # users, chats, tourism, culture, etc.
    date_recorded = Column(DateTime(timezone=True), server_default=func.now())
    additional_data = Column(JSON, nullable=True)