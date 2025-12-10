from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import random
from datetime import datetime
router = APIRouter()

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    user_id: str = Field(..., description="Unique user identifier")
    context: Optional[str] = Field(None, description="Additional context for the query")
    language: Optional[str] = Field("en", description="Preferred response language")

class ChatResponse(BaseModel):
    response: str
    user_id: str
    message_id: str
    timestamp: str
    context_used: List[str]
    suggested_actions: List[str]
    related_topics: List[str]

class ConversationHistory(BaseModel):
    user_id: str
    messages: List[Dict]
    total_messages: int
    last_activity: str

@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest):
    """
    Enhanced chat endpoint with context-aware responses.
    
    TODO: Connect to Ollama LLM here for actual AI responses.
    TODO: Integrate VectorDB for RAG-based context retrieval.
    TODO: Add conversation memory and personalization.
    """
    
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    # Analyze message for intent and keywords
    message_lower = request.message.lower()
    
    # Knowledge base for different topics
    knowledge_base = {
        "char_dham": {
            "keywords": ["char dham", "kedarnath", "badrinath", "gangotri", "yamunotri", "four dhams"],
            "responses": [
                "The Char Dham Yatra is one of the most sacred pilgrimages in Hinduism. It includes Kedarnath (3,583m), Badrinath (3,133m), Gangotri (3,100m), and Yamunotri (3,293m). Each shrine has its own significance and the best time to visit is from May to October.",
                "Char Dham represents the four sacred abodes in Uttarakhand. Kedarnath is dedicated to Lord Shiva, Badrinath to Lord Vishnu, while Gangotri and Yamunotri are the sources of rivers Ganga and Yamuna respectively.",
            ],
            "context": ["pilgrimage", "temples", "spirituality"],
            "actions": ["Check crowd status", "Plan route", "Book accommodation"],
            "related": ["Weather conditions", "Travel routes", "Accommodation options"]
        },
        "weather": {
            "keywords": ["weather", "temperature", "rain", "snow", "climate", "season"],
            "responses": [
                "Uttarakhand's weather varies greatly with altitude. The Char Dham shrines experience cold temperatures year-round. Summer (May-June) is ideal for pilgrimage with temperatures 5-15°C. Monsoon (July-August) brings heavy rainfall and landslides. Winter (November-April) sees heavy snowfall and shrine closures.",
                "The weather in Uttarakhand's high-altitude regions can change rapidly. Always carry warm clothing, rain gear, and check weather forecasts before traveling. The shrines are typically closed from November to April due to heavy snowfall.",
            ],
            "context": ["travel planning", "safety"],
            "actions": ["Check current weather", "View forecast", "Pack accordingly"],
            "related": ["Best travel time", "What to pack", "Safety precautions"]
        },
        "travel": {
            "keywords": ["travel", "route", "road", "transport", "bus", "car", "helicopter"],
            "responses": [
                "Travel to Char Dham involves well-connected road networks from Rishikesh and Haridwar. Kedarnath requires a 16km trek from Gaurikund, while others are accessible by road. Helicopter services are available for Kedarnath and Badrinath during peak season.",
                "The main routes start from Rishikesh: Rishikesh-Kedarnath (223km + 16km trek), Rishikesh-Badrinath (301km), Rishikesh-Gangotri (249km), and Rishikesh-Yamunotri (209km). Roads can be challenging with narrow mountain paths.",
            ],
            "context": ["logistics", "planning"],
            "actions": ["Calculate carbon footprint", "Find routes", "Book transport"],
            "related": ["Road conditions", "Fuel stops", "Emergency contacts"]
        },
        "accommodation": {
            "keywords": ["stay", "hotel", "accommodation", "lodge", "dharamshala", "booking"],
            "responses": [
                "Accommodation options range from government guesthouses and dharamshalas to private hotels. Book in advance during peak season (May-October). Basic facilities are available near all shrines, with better options in base towns like Guptkashi, Joshimath, and Uttarkashi.",
                "Stay options include GMVN (Garhwal Mandal Vikas Nigam) guesthouses, private hotels, and ashrams. Prices range from ₹500-5000 per night. Basic amenities like hot water and heating may be limited at high altitudes.",
            ],
            "context": ["comfort", "planning"],
            "actions": ["Find hotels", "Check availability", "Read reviews"],
            "related": ["Booking platforms", "Cancellation policies", "Amenities available"]
        },
        "culture": {
            "keywords": ["culture", "tradition", "art", "handicraft", "local", "artisan", "shopping"],
            "responses": [
                "Uttarakhand has rich cultural heritage with traditional arts like Aipan (floor art), Ringal bamboo crafts, and handwoven textiles. Local artisans create beautiful woolen shawls, copper utensils, and wooden carvings. Support local communities by purchasing authentic handicrafts.",
                "The region's culture reflects its spiritual significance and mountain lifestyle. Traditional music, dance forms like Langvir Nritya, and festivals like Nanda Devi Raj Jat showcase the local heritage. Local markets offer organic honey, herbal products, and traditional crafts.",
            ],
            "context": ["shopping", "heritage"],
            "actions": ["Browse products", "Find artisans", "Learn about crafts"],
            "related": ["Local markets", "Authentic products", "Cultural festivals"]
        },
        "yoga": {
            "keywords": ["yoga", "meditation", "asana", "pose", "spiritual", "practice"],
            "responses": [
                "Uttarakhand, especially Rishikesh, is known as the 'Yoga Capital of the World'. The serene mountain environment is perfect for yoga practice and meditation. Many ashrams offer yoga courses, and the spiritual energy of the region enhances the practice.",
                "Practicing yoga in the Himalayas connects you with nature's energy. Mountain poses like Warrior and Tree pose feel more meaningful here. The clean air and peaceful environment help deepen your practice and meditation.",
            ],
            "context": ["wellness", "spirituality"],
            "actions": ["Try yoga poses", "Find classes", "Learn meditation"],
            "related": ["Yoga centers", "Meditation techniques", "Spiritual practices"]
        }
    }
    
    # Find matching topic
    matched_topic = None
    for topic, data in knowledge_base.items():
        if any(keyword in message_lower for keyword in data["keywords"]):
            matched_topic = topic
            break
    
    # Generate response
    if matched_topic:
        topic_data = knowledge_base[matched_topic]
        response = random.choice(topic_data["responses"])
        context_used = topic_data["context"]
        suggested_actions = topic_data["actions"]
        related_topics = topic_data["related"]
    else:
        # Generic response for unmatched queries
        response = f"I am Deep-Shiva, your spiritual guide for Uttarakhand tourism. I understand you're asking about '{request.message}'. While I'm being enhanced with advanced AI capabilities, I can help you with information about the Char Dham pilgrimage, weather conditions, travel routes, local culture, and yoga practices. What specific aspect would you like to know more about?"
        context_used = ["general"]
        suggested_actions = ["Ask about Char Dham", "Check weather", "Plan travel"]
        related_topics = ["Pilgrimage sites", "Travel planning", "Local culture"]
    
    # Add personalization based on language
    if request.language == "hi":
        response = f"नमस्ते! {response}"
    elif request.language == "ga":  # Garhwali
        response = f"जय भोले की! {response}"
    
    # Generate unique message ID
    message_id = f"msg_{random.randint(100000, 999999)}"
    
    return ChatResponse(
        response=response,
        user_id=request.user_id,
        message_id=message_id,
        timestamp=datetime.now().isoformat(),
        context_used=context_used,
        suggested_actions=suggested_actions[:3],  # Limit to 3 suggestions
        related_topics=related_topics[:3]  # Limit to 3 related topics
    )
@router.get("/history/{user_id}", response_model=ConversationHistory)
async def get_conversation_history(
    user_id: str,
    limit: int = Query(20, ge=1, le=100, description="Number of recent messages to return")
):
    """
    Get conversation history for a user.
    
    TODO: Implement persistent storage for conversation history.
    TODO: Add conversation analytics and insights.
    """
    
    # Mock conversation history
    mock_messages = [
        {
            "message_id": "msg_123456",
            "user_message": "Tell me about Kedarnath temple",
            "bot_response": "Kedarnath is one of the most sacred temples dedicated to Lord Shiva...",
            "timestamp": "2024-12-10T09:15:00Z",
            "context_used": ["pilgrimage", "temples"]
        },
        {
            "message_id": "msg_123457", 
            "user_message": "What's the weather like there?",
            "bot_response": "The weather at Kedarnath varies greatly with altitude...",
            "timestamp": "2024-12-10T09:18:00Z",
            "context_used": ["weather", "travel planning"]
        },
        {
            "message_id": "msg_123458",
            "user_message": "How do I get there?",
            "bot_response": "Travel to Kedarnath involves a journey to Gaurikund followed by a 16km trek...",
            "timestamp": "2024-12-10T09:22:00Z",
            "context_used": ["travel", "logistics"]
        }
    ]
    
    # Limit messages
    limited_messages = mock_messages[:limit]
    
    return ConversationHistory(
        user_id=user_id,
        messages=limited_messages,
        total_messages=len(mock_messages),
        last_activity="2024-12-10T09:22:00Z"
    )

@router.delete("/history/{user_id}")
async def clear_conversation_history(user_id: str):
    """
    Clear conversation history for a user.
    
    TODO: Implement actual history deletion from database.
    """
    
    return {
        "message": f"Conversation history cleared for user {user_id}",
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }

class ChatFeedbackRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    message_id: str = Field(..., description="Message ID being rated")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5")
    feedback_type: str = Field(..., description="Type: helpful, accurate, relevant, clear")
    comments: Optional[str] = Field(None, max_length=500, description="Additional comments")

@router.post("/feedback")
async def submit_chat_feedback(request: ChatFeedbackRequest):
    """
    Submit feedback on chat responses to improve AI performance.
    
    TODO: Store feedback for model training and improvement.
    TODO: Implement feedback analytics dashboard.
    """
    
    valid_feedback_types = ["helpful", "accurate", "relevant", "clear"]
    if request.feedback_type not in valid_feedback_types:
        raise HTTPException(status_code=400, detail=f"Invalid feedback type. Must be one of: {valid_feedback_types}")
    
    feedback_data = {
        "feedback_id": random.randint(10000, 99999),
        "user_id": request.user_id,
        "message_id": request.message_id,
        "rating": request.rating,
        "feedback_type": request.feedback_type,
        "comments": request.comments,
        "timestamp": datetime.now().isoformat(),
        "status": "received"
    }
    
    return {
        "message": "Thank you for your feedback! This helps us improve Deep-Shiva.",
        "feedback_id": feedback_data["feedback_id"],
        "status": "success"
    }

@router.get("/suggestions")
async def get_chat_suggestions():
    """
    Get suggested questions/topics for users to ask about.
    
    TODO: Personalize suggestions based on user history and preferences.
    TODO: Add trending topics and seasonal suggestions.
    """
    
    suggestions = {
        "popular_questions": [
            "Tell me about the Char Dham yatra",
            "What's the best time to visit Kedarnath?",
            "How do I plan a trip to Badrinath?",
            "What should I pack for the pilgrimage?",
            "Are there helicopter services available?",
            "What are the accommodation options?",
            "Tell me about local culture and traditions",
            "What yoga practices are recommended?"
        ],
        "categories": [
            {
                "name": "Pilgrimage Planning",
                "questions": [
                    "How long does the Char Dham yatra take?",
                    "What are the registration requirements?",
                    "Can I visit all four dhams in one trip?"
                ]
            },
            {
                "name": "Travel & Transport",
                "questions": [
                    "What are the road conditions like?",
                    "Is public transport available?",
                    "How much does the trip cost?"
                ]
            },
            {
                "name": "Health & Safety",
                "questions": [
                    "What precautions should I take for high altitude?",
                    "Are there medical facilities available?",
                    "What emergency contacts should I have?"
                ]
            },
            {
                "name": "Culture & Spirituality",
                "questions": [
                    "What are the temple timings?",
                    "What rituals are performed at each shrine?",
                    "Can I buy local handicrafts?"
                ]
            }
        ],
        "quick_actions": [
            "Check current weather",
            "Calculate carbon footprint",
            "View crowd status",
            "Find accommodation",
            "Practice yoga poses"
        ]
    }
    
    return suggestions

class TranslateRequest(BaseModel):
    text: str = Field(..., description="Text to translate")
    target_language: str = Field(..., description="Target language: en, hi, ga")
    source_language: Optional[str] = Field("auto", description="Source language (auto-detect)")

@router.post("/translate")
async def translate_message(request: TranslateRequest):
    """
    Translate text between supported languages.
    
    TODO: Integrate with translation service (Google Translate API, etc.)
    TODO: Add support for more regional languages.
    """
    
    supported_languages = ["en", "hi", "ga"]  # English, Hindi, Garhwali
    
    if request.target_language not in supported_languages:
        raise HTTPException(status_code=400, detail=f"Unsupported target language. Supported: {supported_languages}")
    
    # Mock translation responses
    translations = {
        "en": {
            "नमस्ते": "Hello",
            "धन्यवाद": "Thank you", 
            "केदारनाथ": "Kedarnath",
            "यात्रा": "Journey/Pilgrimage"
        },
        "hi": {
            "hello": "नमस्ते",
            "thank you": "धन्यवाद",
            "kedarnath": "केदारनाथ", 
            "journey": "यात्रा"
        },
        "ga": {
            "hello": "जय भोले की",
            "thank you": "धन्यवाद",
            "mountain": "पहाड़",
            "temple": "मंदिर"
        }
    }
    
    # Simple mock translation
    text_lower = request.text.lower()
    translated_text = request.text  # Default to original text
    
    if request.target_language in translations:
        for original, translation in translations[request.target_language].items():
            if original in text_lower:
                translated_text = translation
                break
    
    return {
        "original_text": request.text,
        "translated_text": translated_text,
        "source_language": request.source_language,
        "target_language": request.target_language,
        "confidence": 0.95 if translated_text != request.text else 0.1
    }