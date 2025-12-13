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
    chat_type = Column(String(50), default="general")  # general, tourism, culture, yoga, emergency, vision
    session_id = Column(String(36), nullable=True)  # UUID for session tracking
    chat_metadata = Column(JSON, nullable=True)  # Store additional chat metadata
    message_count = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)  # Track AI token usage
    avg_response_time = Column(Float, nullable=True)  # Average response time in seconds
    user_rating = Column(Integer, nullable=True)  # User satisfaction rating 1-5
    tags = Column(JSON, nullable=True)  # Array of tags for categorization
    is_favorite = Column(Boolean, default=False)
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
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
    message_type = Column(String(20), default="text")  # text, image, voice, vision
    language = Column(String(10), default="en")
    ai_model = Column(String(50), nullable=True)  # Track which AI model was used
    tokens_used = Column(Integer, default=0)  # Tokens consumed for this message
    response_time = Column(Float, nullable=True)  # Response time in seconds
    confidence_score = Column(Float, nullable=True)  # AI confidence in response (0.00-1.00)
    context_data = Column(JSON, nullable=True)  # Store context like location, image analysis results, etc.
    feedback_rating = Column(Integer, nullable=True)  # Message-level feedback 1-5
    is_helpful = Column(Boolean, nullable=True)  # User feedback on helpfulness
    attachments = Column(JSON, nullable=True)  # Store file/image attachments metadata
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

class CulturalTradition(Base):
    __tablename__ = "cultural_traditions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    district = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)  # dance, music, ritual, festival, cuisine, craft, etc.
    origin_story = Column(Text, nullable=True)
    significance = Column(Text, nullable=True)
    when_practiced = Column(String(200), nullable=True)  # When this tradition is practiced
    participants = Column(String(200), nullable=True)  # Who participates
    materials_required = Column(JSON, nullable=True)  # Array of materials/items needed
    steps_or_process = Column(JSON, nullable=True)  # Array of steps or process description
    cultural_values = Column(JSON, nullable=True)  # Array of cultural values represented
    modern_relevance = Column(Text, nullable=True)
    preservation_status = Column(String(50), default="active")  # active, declining, revived, extinct
    images = Column(JSON, nullable=True)  # Array of image URLs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class CulturalPractitioner(Base):
    __tablename__ = "cultural_practitioners"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    phone = Column(String(20), nullable=True)
    location = Column(String(200), nullable=False)
    district = Column(String(100), nullable=False)
    specialization = Column(JSON, nullable=False)  # Array of traditions/skills they practice
    experience_years = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    teaching_available = Column(Boolean, default=False)
    languages_spoken = Column(JSON, nullable=True)  # Array of languages they speak
    achievements = Column(JSON, nullable=True)  # Array of achievements/awards
    availability_schedule = Column(JSON, nullable=True)  # Schedule information
    contact_preference = Column(String(20), default="phone")  # phone, email, whatsapp
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class CulturalEvent(Base):
    __tablename__ = "cultural_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    event_type = Column(String(50), nullable=False)  # workshop, festival, performance, exhibition, etc.
    tradition_id = Column(Integer, ForeignKey("cultural_traditions.id"), nullable=True)
    organizer = Column(String(200), nullable=True)
    location = Column(String(200), nullable=False)
    district = Column(String(100), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    registration_required = Column(Boolean, default=False)
    registration_fee = Column(Float, default=0.00)
    max_participants = Column(Integer, nullable=True)
    age_group = Column(String(50), nullable=True)  # Age restrictions or recommendations
    skill_level = Column(String(20), default="all")  # beginner, intermediate, advanced, all
    contact_info = Column(JSON, nullable=True)  # Contact information for registration
    requirements = Column(JSON, nullable=True)  # Array of requirements or things to bring
    learning_outcomes = Column(JSON, nullable=True)  # Array of what participants will learn
    images = Column(JSON, nullable=True)  # Array of image URLs
    status = Column(String(20), default="upcoming")  # upcoming, ongoing, completed, cancelled
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    tradition = relationship("CulturalTradition")

class DashboardMetrics(Base):
    __tablename__ = "dashboard_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50), nullable=False)  # count, percentage, rating, etc.
    category = Column(String(50), nullable=False)  # users, chats, tourism, culture, etc.
    date_recorded = Column(DateTime(timezone=True), server_default=func.now())
    additional_data = Column(JSON, nullable=True)