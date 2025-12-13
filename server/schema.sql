-- Deep-Shiva Database Schema for Neon PostgreSQL
-- This file contains the complete database schema for the Uttarakhand Tourism Chatbot

-- Enable UUID extension for better ID generation (optional)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table - Store user information and preferences
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    full_name VARCHAR(100),
    preferred_language VARCHAR(10) DEFAULT 'en',
    location VARCHAR(100),
    interests JSONB, -- Store user interests as JSON array
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Chats table - Store chat sessions with enhanced metadata
CREATE TABLE IF NOT EXISTS chats (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200),
    chat_type VARCHAR(50) DEFAULT 'general', -- general, tourism, culture, yoga, emergency, vision
    session_id UUID DEFAULT uuid_generate_v4(), -- Unique session identifier
    chat_metadata JSONB, -- Store additional chat metadata (location, preferences, context)
    message_count INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0, -- Track AI token usage
    avg_response_time DECIMAL(5,2), -- Average response time in seconds
    user_rating INTEGER CHECK (user_rating >= 1 AND user_rating <= 5), -- User satisfaction rating
    tags JSONB, -- Array of tags for categorization
    is_favorite BOOLEAN DEFAULT FALSE,
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Chat messages table - Store individual messages and responses with enhanced metadata
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER REFERENCES chats(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    response TEXT,
    message_type VARCHAR(20) DEFAULT 'text', -- text, image, voice, vision
    language VARCHAR(10) DEFAULT 'en',
    ai_model VARCHAR(50), -- Track which AI model was used
    tokens_used INTEGER DEFAULT 0, -- Tokens consumed for this message
    response_time DECIMAL(5,2), -- Response time in seconds
    confidence_score DECIMAL(3,2), -- AI confidence in response (0.00-1.00)
    context_data JSONB, -- Store context like location, image analysis results, etc.
    feedback_rating INTEGER CHECK (feedback_rating >= 1 AND feedback_rating <= 5), -- Message-level feedback
    is_helpful BOOLEAN, -- User feedback on helpfulness
    attachments JSONB, -- Store file/image attachments metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Cultural sites table - Store information about cultural heritage sites
CREATE TABLE IF NOT EXISTS cultural_sites (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    location VARCHAR(200) NOT NULL,
    district VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    category VARCHAR(50) NOT NULL, -- temple, heritage, monument, etc.
    historical_significance TEXT,
    visiting_hours VARCHAR(100),
    entry_fee VARCHAR(50),
    best_time_to_visit VARCHAR(100),
    images JSONB, -- Array of image URLs
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Cultural traditions table - Store traditional practices, arts, and customs
CREATE TABLE IF NOT EXISTS cultural_traditions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    district VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL, -- dance, music, ritual, festival, cuisine, craft, etc.
    origin_story TEXT,
    significance TEXT,
    when_practiced VARCHAR(200), -- When this tradition is practiced
    participants VARCHAR(200), -- Who participates
    materials_required JSONB, -- Array of materials/items needed
    steps_or_process JSONB, -- Array of steps or process description
    cultural_values JSONB, -- Array of cultural values represented
    modern_relevance TEXT,
    preservation_status VARCHAR(50) DEFAULT 'active', -- active, declining, revived, extinct
    images JSONB, -- Array of image URLs
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Cultural practitioners table - Store information about people who practice/teach traditions
CREATE TABLE IF NOT EXISTS cultural_practitioners (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    location VARCHAR(200) NOT NULL,
    district VARCHAR(100) NOT NULL,
    specialization JSONB NOT NULL, -- Array of traditions/skills they practice
    experience_years INTEGER,
    description TEXT,
    teaching_available BOOLEAN DEFAULT FALSE,
    languages_spoken JSONB, -- Array of languages they speak
    achievements JSONB, -- Array of achievements/awards
    availability_schedule JSONB, -- Schedule information
    contact_preference VARCHAR(20) DEFAULT 'phone', -- phone, email, whatsapp
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Cultural events table - Store upcoming cultural events, workshops, festivals
CREATE TABLE IF NOT EXISTS cultural_events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    event_type VARCHAR(50) NOT NULL, -- workshop, festival, performance, exhibition, etc.
    tradition_id INTEGER REFERENCES cultural_traditions(id) ON DELETE SET NULL,
    organizer VARCHAR(200),
    location VARCHAR(200) NOT NULL,
    district VARCHAR(100) NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE,
    registration_required BOOLEAN DEFAULT FALSE,
    registration_fee DECIMAL(10, 2) DEFAULT 0.00,
    max_participants INTEGER,
    age_group VARCHAR(50), -- Age restrictions or recommendations
    skill_level VARCHAR(20) DEFAULT 'all', -- beginner, intermediate, advanced, all
    contact_info JSONB, -- Contact information for registration
    requirements JSONB, -- Array of requirements or things to bring
    learning_outcomes JSONB, -- Array of what participants will learn
    images JSONB, -- Array of image URLs
    status VARCHAR(20) DEFAULT 'upcoming', -- upcoming, ongoing, completed, cancelled
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Artisans table - Store artisan profiles
CREATE TABLE IF NOT EXISTS artisans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(20),
    location VARCHAR(200) NOT NULL,
    district VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL, -- woodwork, textiles, pottery, etc.
    experience_years INTEGER,
    description TEXT,
    profile_image VARCHAR(500),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Artisan products table - Store products created by artisans
CREATE TABLE IF NOT EXISTS artisan_products (
    id SERIAL PRIMARY KEY,
    artisan_id INTEGER REFERENCES artisans(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2),
    currency VARCHAR(10) DEFAULT 'INR',
    materials_used TEXT,
    dimensions VARCHAR(100),
    weight VARCHAR(50),
    images JSONB, -- Array of image URLs
    availability_status VARCHAR(20) DEFAULT 'available', -- available, sold, custom_order
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Tourism places table - Store tourist destinations
CREATE TABLE IF NOT EXISTS tourism_places (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    location VARCHAR(200) NOT NULL,
    district VARCHAR(100) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    category VARCHAR(50) NOT NULL, -- hill_station, temple, adventure, wildlife, etc.
    altitude INTEGER, -- in meters
    best_time_to_visit VARCHAR(100),
    activities JSONB, -- Array of activities
    accommodation_options JSONB,
    transportation TEXT,
    entry_fee VARCHAR(50),
    images JSONB, -- Array of image URLs
    weather_info JSONB,
    crowd_level VARCHAR(20) DEFAULT 'moderate', -- low, moderate, high
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Yoga poses table - Store yoga pose information
CREATE TABLE IF NOT EXISTS yoga_poses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sanskrit_name VARCHAR(100),
    description TEXT,
    difficulty_level VARCHAR(20) NOT NULL, -- beginner, intermediate, advanced
    category VARCHAR(50) NOT NULL, -- standing, sitting, lying, balancing, etc.
    benefits JSONB, -- Array of benefits
    instructions JSONB, -- Step-by-step instructions
    precautions TEXT,
    duration VARCHAR(50),
    image_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Emergency contacts table - Store emergency service contacts
CREATE TABLE IF NOT EXISTS emergency_contacts (
    id SERIAL PRIMARY KEY,
    district VARCHAR(100) NOT NULL,
    service_type VARCHAR(50) NOT NULL, -- police, hospital, fire, tourist_helpline
    name VARCHAR(200) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    is_24x7 BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Dashboard metrics table - Store analytics and metrics data
CREATE TABLE IF NOT EXISTS dashboard_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15, 2) NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- count, percentage, rating, etc.
    category VARCHAR(50) NOT NULL, -- users, chats, tourism, culture, etc.
    date_recorded TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    additional_data JSONB
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_chats_user_id ON chats(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_chat_id ON chat_messages(chat_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_cultural_sites_district ON cultural_sites(district);
CREATE INDEX IF NOT EXISTS idx_cultural_sites_category ON cultural_sites(category);
CREATE INDEX IF NOT EXISTS idx_cultural_traditions_district ON cultural_traditions(district);
CREATE INDEX IF NOT EXISTS idx_cultural_traditions_category ON cultural_traditions(category);
CREATE INDEX IF NOT EXISTS idx_cultural_practitioners_district ON cultural_practitioners(district);
CREATE INDEX IF NOT EXISTS idx_cultural_events_district ON cultural_events(district);
CREATE INDEX IF NOT EXISTS idx_cultural_events_start_date ON cultural_events(start_date);
CREATE INDEX IF NOT EXISTS idx_cultural_events_status ON cultural_events(status);
CREATE INDEX IF NOT EXISTS idx_artisans_district ON artisans(district);
CREATE INDEX IF NOT EXISTS idx_artisans_specialization ON artisans(specialization);
CREATE INDEX IF NOT EXISTS idx_artisan_products_artisan_id ON artisan_products(artisan_id);
CREATE INDEX IF NOT EXISTS idx_tourism_places_district ON tourism_places(district);
CREATE INDEX IF NOT EXISTS idx_tourism_places_category ON tourism_places(category);
CREATE INDEX IF NOT EXISTS idx_yoga_poses_difficulty ON yoga_poses(difficulty_level);
CREATE INDEX IF NOT EXISTS idx_emergency_contacts_district ON emergency_contacts(district);
CREATE INDEX IF NOT EXISTS idx_emergency_contacts_service_type ON emergency_contacts(service_type);
CREATE INDEX IF NOT EXISTS idx_dashboard_metrics_category ON dashboard_metrics(category);
CREATE INDEX IF NOT EXISTS idx_dashboard_metrics_date ON dashboard_metrics(date_recorded);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_chats_updated_at BEFORE UPDATE ON chats FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cultural_sites_updated_at BEFORE UPDATE ON cultural_sites FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cultural_traditions_updated_at BEFORE UPDATE ON cultural_traditions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cultural_practitioners_updated_at BEFORE UPDATE ON cultural_practitioners FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_cultural_events_updated_at BEFORE UPDATE ON cultural_events FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_artisans_updated_at BEFORE UPDATE ON artisans FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_artisan_products_updated_at BEFORE UPDATE ON artisan_products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_tourism_places_updated_at BEFORE UPDATE ON tourism_places FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_emergency_contacts_updated_at BEFORE UPDATE ON emergency_contacts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();