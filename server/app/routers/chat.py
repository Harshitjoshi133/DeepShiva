from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import time
from datetime import datetime
import uuid
import json
from pathlib import Path

from ..logging_config import get_logger, ErrorTracker, PerformanceLogger, get_ai_response_logger, AIResponseLogger
from ..services.ollama_service import ollama_service

router = APIRouter()
logger = get_logger("chat")
error_tracker = ErrorTracker(logger)
performance_logger = PerformanceLogger(logger)
ai_response_logger = AIResponseLogger(get_ai_response_logger())

# Helper functions for response analysis
def _extract_context_from_response(response: str) -> List[str]:
    """Extract context keywords from AI response"""
    context_keywords = {
        "pilgrimage": ["kedarnath", "badrinath", "gangotri", "yamunotri", "char dham", "temple", "shrine"],
        "travel": ["route", "road", "journey", "transport", "helicopter", "trek", "distance"],
        "weather": ["weather", "temperature", "season", "rain", "snow", "climate"],
        "accommodation": ["hotel", "stay", "lodge", "guesthouse", "booking", "accommodation"],
        "culture": ["culture", "tradition", "art", "handicraft", "local", "artisan"],
        "spirituality": ["spiritual", "meditation", "yoga", "prayer", "blessing", "sacred"],
        "safety": ["safety", "precaution", "emergency", "first aid", "rescue"]
    }
    
    response_lower = response.lower()
    found_contexts = []
    
    for context, keywords in context_keywords.items():
        if any(keyword in response_lower for keyword in keywords):
            found_contexts.append(context)
    
    return found_contexts[:3]  # Return top 3 contexts

def _generate_suggested_actions(message: str, response: str) -> List[str]:
    """Generate suggested actions based on message and response"""
    message_lower = message.lower()
    response_lower = response.lower()
    
    suggestions = []
    
    # Context-based suggestions
    if any(word in message_lower for word in ["weather", "temperature", "climate"]):
        suggestions.extend(["Check current weather", "View 7-day forecast", "Pack weather-appropriate gear"])
    
    if any(word in message_lower for word in ["route", "travel", "journey", "how to reach"]):
        suggestions.extend(["Calculate carbon footprint", "Find accommodation", "Check road conditions"])
    
    if any(word in message_lower for word in ["kedarnath", "badrinath", "gangotri", "yamunotri"]):
        suggestions.extend(["Check crowd status", "View shrine timings", "Book helicopter tickets"])
    
    if any(word in message_lower for word in ["stay", "hotel", "accommodation"]):
        suggestions.extend(["Find nearby hotels", "Check availability", "Read reviews"])
    
    if any(word in message_lower for word in ["yoga", "meditation", "spiritual"]):
        suggestions.extend(["Try yoga poses", "Find meditation centers", "Learn breathing techniques"])
    
    # Default suggestions if none match
    if not suggestions:
        suggestions = ["Ask about Char Dham", "Check weather conditions", "Plan your journey"]
    
    return suggestions[:3]  # Return top 3 suggestions

def _generate_related_topics(message: str, response: str) -> List[str]:
    """Generate related topics based on message and response"""
    message_lower = message.lower()
    
    topics = []
    
    # Topic mapping
    if any(word in message_lower for word in ["kedarnath", "badrinath", "gangotri", "yamunotri", "char dham"]):
        topics.extend(["Temple timings", "Accommodation options", "Travel routes"])
    
    if any(word in message_lower for word in ["weather", "temperature"]):
        topics.extend(["Best travel time", "What to pack", "Seasonal guidelines"])
    
    if any(word in message_lower for word in ["travel", "route", "journey"]):
        topics.extend(["Road conditions", "Fuel stops", "Emergency contacts"])
    
    if any(word in message_lower for word in ["culture", "tradition", "art"]):
        topics.extend(["Local festivals", "Handicrafts", "Traditional food"])
    
    if any(word in message_lower for word in ["yoga", "meditation"]):
        topics.extend(["Yoga centers", "Spiritual practices", "Ashram stays"])
    
    # Default topics
    if not topics:
        topics = ["Pilgrimage planning", "Local culture", "Travel tips"]
    
    return topics[:3]  # Return top 3 topics

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
    ai_metadata: Dict[str, Any]
    processing_time_ms: float
    model_used: str

class ConversationHistory(BaseModel):
    user_id: str
    messages: List[Dict]
    total_messages: int
    last_activity: str

@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest, http_request: Request):
    """
    AI-powered chat endpoint using Ollama for intelligent responses.
    Provides context-aware responses about Uttarakhand tourism and Char Dham pilgrimage.
    """
    start_time = time.time()
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    
    logger.info("AI chat query received", extra={
        "request_id": request_id,
        "user_id": request.user_id,
        "message_length": len(request.message),
        "language": request.language,
        "has_context": bool(request.context)
    })
    
    if not request.message.strip():
        logger.warning("Empty message received", extra={
            "request_id": request_id,
            "user_id": request.user_id
        })
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Get conversation history (mock for now - in production, fetch from database)
        conversation_history = []  # TODO: Implement conversation history from database
        
        # Generate AI response using Ollama
        ai_result = await ollama_service.generate_response(
            message=request.message,
            user_id=request.user_id,
            context=request.context,
            conversation_history=conversation_history,
            language=request.language
        )
        
        # Generate unique message ID
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        
        # Extract context and suggestions from AI response (simple keyword analysis)
        context_used = _extract_context_from_response(ai_result["response"])
        suggested_actions = _generate_suggested_actions(request.message, ai_result["response"])
        related_topics = _generate_related_topics(request.message, ai_result["response"])
        
        # Calculate total processing time
        total_processing_time = (time.time() - start_time) * 1000
        
        # Log successful response
        logger.info("AI chat query processed successfully", extra={
            "request_id": request_id,
            "user_id": request.user_id,
            "message_id": message_id,
            "ai_success": ai_result["success"],
            "model_used": ai_result["model"],
            "ai_processing_time_ms": ai_result["processing_time_ms"],
            "total_processing_time_ms": round(total_processing_time, 2),
            "response_length": len(ai_result["response"])
        })
        
        # Log conversation context and suggestions
        ai_response_logger.log_conversation_context(
            user_id=request.user_id,
            message_id=message_id,
            context_used=context_used,
            suggested_actions=suggested_actions,
            related_topics=related_topics,
            request_id=request_id
        )
        
        # Log performance if slow
        if total_processing_time > 2000:  # Log if over 2 seconds
            performance_logger.log_api_performance(
                endpoint="/api/v1/chat/query",
                method="POST",
                duration_ms=total_processing_time,
                status_code=200
            )
        
        return ChatResponse(
            response=ai_result["response"],
            user_id=request.user_id,
            message_id=message_id,
            timestamp=datetime.now().isoformat(),
            context_used=context_used,
            suggested_actions=suggested_actions,
            related_topics=related_topics,
            ai_metadata=ai_result.get("metadata", {}),
            processing_time_ms=round(total_processing_time, 2),
            model_used=ai_result["model"]
        )
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        
        error_tracker.log_validation_error(e, {
            "request_id": request_id,
            "user_id": request.user_id,
            "message": request.message[:100],  # First 100 chars for privacy
            "language": request.language
        })
        
        logger.error("Chat query processing failed", extra={
            "request_id": request_id,
            "user_id": request.user_id,
            "error": str(e),
            "processing_time_ms": round(processing_time, 2)
        })
        
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat query. Please try again later."
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

@router.get("/ollama/status")
async def get_ollama_status(request: Request):
    """
    Get Ollama service status and model information
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info("Ollama status check requested", extra={
        "request_id": request_id
    })
    
    try:
        # Check Ollama connection
        connection_ok = await ollama_service.check_connection()
        
        # Check model availability
        model_available = await ollama_service.check_model_availability() if connection_ok else False
        
        # Get model info
        model_info = await ollama_service.get_model_info() if connection_ok else {}
        
        status = {
            "ollama_connected": connection_ok,
            "model_available": model_available,
            "model_info": model_info,
            "configuration": {
                "host": ollama_service.host,
                "model": ollama_service.model,
                "timeout": ollama_service.timeout,
                "temperature": ollama_service.temperature,
                "max_tokens": ollama_service.max_tokens
            },
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("Ollama status check completed", extra={
            "request_id": request_id,
            "connected": connection_ok,
            "model_available": model_available
        })
        
        return status
        
    except Exception as e:
        error_tracker.log_external_api_error(e, "Ollama", "status_check")
        
        return {
            "ollama_connected": False,
            "model_available": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/ollama/pull-model")
async def pull_ollama_model(request: Request, model_name: Optional[str] = None):
    """
    Pull/download a model to Ollama
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    model = model_name or ollama_service.model
    
    logger.info("Model pull requested", extra={
        "request_id": request_id,
        "model": model
    })
    
    try:
        success = await ollama_service.pull_model(model)
        
        if success:
            logger.info("Model pulled successfully", extra={
                "request_id": request_id,
                "model": model
            })
            
            return {
                "success": True,
                "message": f"Model '{model}' pulled successfully",
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": f"Failed to pull model '{model}'",
                "model": model,
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        error_tracker.log_external_api_error(e, "Ollama", "pull_model")
        
        return {
            "success": False,
            "error": str(e),
            "model": model,
            "timestamp": datetime.now().isoformat()
        }

@router.post("/test-ai")
async def test_ai_response(request: Request):
    """
    Test AI response with a simple query
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info("AI test requested", extra={
        "request_id": request_id
    })
    
    try:
        test_message = "Hello, tell me about Kedarnath temple in one sentence."
        
        ai_result = await ollama_service.generate_response(
            message=test_message,
            user_id="test_user",
            context="Testing AI functionality",
            language="en"
        )
        
        logger.info("AI test completed", extra={
            "request_id": request_id,
            "success": ai_result["success"],
            "model": ai_result["model"],
            "processing_time_ms": ai_result["processing_time_ms"]
        })
        
        return {
            "test_message": test_message,
            "ai_response": ai_result["response"],
            "success": ai_result["success"],
            "model_used": ai_result["model"],
            "processing_time_ms": ai_result["processing_time_ms"],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_tracker.log_external_api_error(e, "Ollama", "test_ai")
        
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/ai-logs")
async def get_ai_response_logs(
    request: Request,
    limit: int = Query(50, ge=1, le=200, description="Number of logs to return"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    success_only: bool = Query(False, description="Show only successful responses")
):
    """
    Get recent AI response logs for monitoring and debugging
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info("AI logs requested", extra={
        "request_id": request_id,
        "limit": limit,
        "user_filter": user_id,
        "success_only": success_only
    })
    
    try:
        logs = []
        log_file_path = Path("logs/ai_responses.log")
        
        if log_file_path.exists():
            with open(log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Parse recent log lines
            for line in reversed(lines[-limit*2:]):  # Get more lines to filter
                try:
                    log_data = json.loads(line.strip())
                    
                    # Apply filters
                    if user_id and log_data.get('user_id') != user_id:
                        continue
                    if success_only and not log_data.get('success', True):
                        continue
                    
                    # Clean up log data for API response
                    clean_log = {
                        "timestamp": log_data.get('timestamp'),
                        "event_type": log_data.get('event_type'),
                        "user_id": log_data.get('user_id'),
                        "message_id": log_data.get('message_id'),
                        "user_message": log_data.get('user_message', ''),
                        "ai_response": log_data.get('ai_response', ''),
                        "model_used": log_data.get('model_used'),
                        "processing_time_ms": log_data.get('processing_time_ms'),
                        "language": log_data.get('language'),
                        "success": log_data.get('success', True),
                        "context": log_data.get('context'),
                        "context_used": log_data.get('context_used', []),
                        "suggested_actions": log_data.get('suggested_actions', []),
                        "related_topics": log_data.get('related_topics', [])
                    }
                    
                    logs.append(clean_log)
                    
                    if len(logs) >= limit:
                        break
                        
                except (json.JSONDecodeError, KeyError):
                    continue
        
        logger.info("AI logs retrieved", extra={
            "request_id": request_id,
            "logs_returned": len(logs)
        })
        
        return {
            "logs": logs,
            "total_returned": len(logs),
            "filters_applied": {
                "user_id": user_id,
                "success_only": success_only,
                "limit": limit
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        error_tracker.log_external_api_error(e, "FileSystem", "ai_logs")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve AI logs"
        )

@router.get("/ai-stats")
async def get_ai_statistics(
    request: Request,
    hours: int = Query(24, ge=1, le=168, description="Hours to analyze")
):
    """
    Get AI response statistics and performance metrics
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info("AI statistics requested", extra={
        "request_id": request_id,
        "hours": hours
    })
    
    try:
        # Parse AI logs for statistics
        stats = {
            "total_responses": 0,
            "successful_responses": 0,
            "failed_responses": 0,
            "avg_processing_time_ms": 0,
            "models_used": {},
            "languages_used": {},
            "most_common_contexts": {},
            "response_time_distribution": {
                "under_1s": 0,
                "1s_to_3s": 0,
                "3s_to_5s": 0,
                "over_5s": 0
            }
        }
        
        log_file_path = Path("logs/ai_responses.log")
        
        if log_file_path.exists():
            processing_times = []
            
            with open(log_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Analyze recent logs
            cutoff_time = datetime.now().timestamp() - (hours * 3600)
            
            for line in reversed(lines[-1000:]):  # Analyze last 1000 entries
                try:
                    log_data = json.loads(line.strip())
                    
                    # Check if log is within time range
                    log_time = datetime.fromisoformat(log_data.get('timestamp', '').replace('Z', '+00:00'))
                    if log_time.timestamp() < cutoff_time:
                        continue
                    
                    if log_data.get('event_type') == 'ai_response':
                        stats["total_responses"] += 1
                        
                        if log_data.get('success', True):
                            stats["successful_responses"] += 1
                        else:
                            stats["failed_responses"] += 1
                        
                        # Processing time analysis
                        proc_time = log_data.get('processing_time_ms', 0)
                        if proc_time > 0:
                            processing_times.append(proc_time)
                            
                            if proc_time < 1000:
                                stats["response_time_distribution"]["under_1s"] += 1
                            elif proc_time < 3000:
                                stats["response_time_distribution"]["1s_to_3s"] += 1
                            elif proc_time < 5000:
                                stats["response_time_distribution"]["3s_to_5s"] += 1
                            else:
                                stats["response_time_distribution"]["over_5s"] += 1
                        
                        # Model usage
                        model = log_data.get('model_used', 'unknown')
                        stats["models_used"][model] = stats["models_used"].get(model, 0) + 1
                        
                        # Language usage
                        language = log_data.get('language', 'unknown')
                        stats["languages_used"][language] = stats["languages_used"].get(language, 0) + 1
                        
                        # Context analysis
                        context = log_data.get('context')
                        if context:
                            stats["most_common_contexts"][context] = stats["most_common_contexts"].get(context, 0) + 1
                
                except (json.JSONDecodeError, KeyError, ValueError):
                    continue
            
            # Calculate averages
            if processing_times:
                stats["avg_processing_time_ms"] = round(sum(processing_times) / len(processing_times), 2)
        
        # Calculate success rate
        success_rate = 0
        if stats["total_responses"] > 0:
            success_rate = round((stats["successful_responses"] / stats["total_responses"]) * 100, 2)
        
        stats["success_rate_percent"] = success_rate
        stats["analysis_period_hours"] = hours
        stats["timestamp"] = datetime.now().isoformat()
        
        logger.info("AI statistics generated", extra={
            "request_id": request_id,
            "total_responses": stats["total_responses"],
            "success_rate": success_rate
        })
        
        return stats
        
    except Exception as e:
        error_tracker.log_external_api_error(e, "FileSystem", "ai_stats")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate AI statistics"
        )