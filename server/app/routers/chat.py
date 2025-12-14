"""
Enhanced Chat Router with async database operations, comprehensive logging and performance optimization
Provides async database operations and detailed request/response logging
"""

from fastapi import APIRouter, HTTPException, Query, Request, Depends
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
import time
import asyncio
from datetime import datetime
import uuid
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, update
from sqlalchemy.exc import DisconnectionError, OperationalError

from ..logging_config import get_logger, ErrorTracker, PerformanceLogger, get_ai_response_logger, AIResponseLogger
from ..services.ollama_service import ollama_service
from ..database import get_async_db, test_async_database_connection
from ..models import User, Chat, ChatMessage

async def cleanup_multiple_active_chats(db: AsyncSession, user_id: int, keep_chat_id: int = None):
    """Clean up multiple active chats by keeping only the most recent one or a specific one"""
    try:
        # Get all active chats for the user
        active_chats_query = select(Chat).where(
            Chat.user_id == user_id,
            Chat.is_active == True
        ).order_by(Chat.last_activity.desc())
        
        result = await db.execute(active_chats_query)
        active_chats = result.scalars().all()
        
        if len(active_chats) <= 1:
            return  # No cleanup needed
        
        logger.info(f"🧹 CLEANING UP MULTIPLE ACTIVE CHATS - User: {user_id}, Total: {len(active_chats)}")
        
        # Determine which chat to keep
        if keep_chat_id:
            # Keep the specified chat
            chat_to_keep = next((chat for chat in active_chats if chat.id == keep_chat_id), None)
            if not chat_to_keep:
                # If specified chat not found, keep the most recent
                chat_to_keep = active_chats[0]
        else:
            # Keep the most recent (first in the ordered list)
            chat_to_keep = active_chats[0]
        
        # Deactivate all other chats
        chats_to_deactivate = [chat for chat in active_chats if chat.id != chat_to_keep.id]
        
        for chat in chats_to_deactivate:
            chat.is_active = False
            logger.info(f"   Deactivating chat: ID={chat.id}, Messages={chat.message_count}")
        
        await db.commit()
        logger.info(f"✅ CLEANUP COMPLETED - Kept chat: ID={chat_to_keep.id}, Deactivated: {len(chats_to_deactivate)}")
        
    except Exception as e:
        logger.error(f"❌ CLEANUP FAILED - User: {user_id}, Error: {str(e)}")
        await db.rollback()

router = APIRouter()
logger = get_logger("chat")
error_tracker = ErrorTracker(logger)
performance_logger = PerformanceLogger(logger)
ai_response_logger = AIResponseLogger(get_ai_response_logger())

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    user_id: str = Field(..., description="Unique user identifier")
    context: Optional[str] = Field(None, description="Additional context for the query")
    language: Optional[str] = Field("en", description="Preferred response language")
    is_new_chat: Optional[bool] = Field(False, description="Indicates if this is the first message in a new chat")
    chat_id: Optional[Union[str, int]] = Field(None, description="Specific chat ID to use for this message")
    
    @validator('chat_id', pre=True)
    def convert_chat_id_to_string(cls, v):
        """Convert chat_id to string if it's provided as an integer"""
        if v is not None:
            return str(v)
        return v

class ChatResponse(BaseModel):
    response: str
    user_id: str
    message_id: str
    chat_id: Optional[str] = None
    timestamp: str
    context_used: List[str]
    suggested_actions: List[str]
    related_topics: List[str]
    ai_metadata: Dict[str, Any]
    processing_time_seconds: float
    model_used: str

class NewChatSessionRequest(BaseModel):
    user_id: str = Field(..., description="User ID")
    language: Optional[str] = Field("en", description="Preferred language")

# Helper functions
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
    
    return found_contexts[:3]

def _generate_suggested_actions(message: str, response: str) -> List[str]:
    """Generate suggested actions based on message and response"""
    message_lower = message.lower()
    
    suggestions = []
    
    if any(word in message_lower for word in ["weather", "temperature", "climate"]):
        suggestions.extend(["Check current weather", "View 7-day forecast", "Pack weather-appropriate gear"])
    
    if any(word in message_lower for word in ["route", "travel", "journey", "how to reach"]):
        suggestions.extend(["Calculate carbon footprint", "Find accommodation", "Check road conditions"])
    
    if any(word in message_lower for word in ["kedarnath", "badrinath", "gangotri", "yamunotri"]):
        suggestions.extend(["Check crowd status", "View shrine timings", "Book helicopter tickets"])
    
    if not suggestions:
        suggestions = ["Ask about Char Dham", "Check weather conditions", "Plan your journey"]
    
    return suggestions[:3]

def _generate_related_topics(message: str, response: str) -> List[str]:
    """Generate related topics based on message and response"""
    message_lower = message.lower()
    
    topics = []
    
    if any(word in message_lower for word in ["kedarnath", "badrinath", "gangotri", "yamunotri", "char dham"]):
        topics.extend(["Temple timings", "Accommodation options", "Travel routes"])
    
    if any(word in message_lower for word in ["weather", "temperature"]):
        topics.extend(["Best travel time", "What to pack", "Seasonal guidelines"])
    
    if not topics:
        topics = ["Pilgrimage planning", "Local culture", "Travel tips"]
    
    return topics[:3]

def _determine_chat_type(message: str) -> str:
    """Determine chat type based on message content"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["kedarnath", "badrinath", "gangotri", "yamunotri", "char dham", "pilgrimage", "temple", "shrine"]):
        return "tourism"
    elif any(word in message_lower for word in ["culture", "tradition", "art", "handicraft", "festival", "dance", "music"]):
        return "culture"
    elif any(word in message_lower for word in ["yoga", "meditation", "pose", "asana", "breathing", "spiritual"]):
        return "yoga"
    elif any(word in message_lower for word in ["emergency", "help", "urgent", "accident", "medical", "police", "fire"]):
        return "emergency"
    else:
        return "general"

def _generate_chat_title(message: str) -> str:
    """Generate a chat title based on the first message"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["kedarnath"]):
        return "Kedarnath Pilgrimage"
    elif any(word in message_lower for word in ["badrinath"]):
        return "Badrinath Journey"
    elif any(word in message_lower for word in ["char dham"]):
        return "Char Dham Yatra"
    elif any(word in message_lower for word in ["yoga", "meditation"]):
        return "Yoga & Meditation"
    else:
        words = message.split()[:4]
        return " ".join(words).title() if len(" ".join(words)) <= 50 else " ".join(words[:3]).title() + "..."

@router.post("/query", response_model=ChatResponse)
async def chat_query(request: ChatRequest, http_request: Request, db: AsyncSession = Depends(get_async_db)):
    """
    Enhanced AI-powered chat endpoint with async database operations, comprehensive logging and performance monitoring.
    Provides context-aware responses about Uttarakhand tourism and Char Dham pilgrimage.
    """
    start_time = time.time()
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    
    # Enhanced request logging
    message_preview = request.message[:100] + "..." if len(request.message) > 100 else request.message
    logger.info(f"🚀 CHAT QUERY STARTED - Request ID: {request_id}, User: {request.user_id}, Message Length: {len(request.message)}, Preview: {message_preview}, Language: {request.language}, Has Context: {bool(request.context)}, New Chat: {request.is_new_chat}")
    
    if not request.message.strip():
        logger.warning(f"❌ EMPTY MESSAGE REJECTED - Request ID: {request_id}, User: {request.user_id}")
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        # Database operations timing
        db_start_time = time.time()
        
        # Always use user ID 10 for chat operations
        target_user_id = 10
        
        logger.info(f"🔍 DATABASE LOOKUP STARTED - Request ID: {request_id}, Target User: {target_user_id}, Requested User: {request.user_id}")
        
        # Get user with ID 10 (async)
        user_query = select(User).where(User.id == target_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        db_user_time = (time.time() - db_start_time) * 1000
        
        user_info = f"ID: {user.id}, Username: {user.username}, Active: {user.is_active}" if user else "None"
        logger.info(f"✅ USER LOOKUP COMPLETED - Request ID: {request_id}, Target User: {target_user_id}, Found: {user is not None}, Query Time: {round(db_user_time, 2)}ms, User: {user_info}")
        
        if not user:
            logger.error(f"❌ USER NOT FOUND - Request ID: {request_id}, Target User: {target_user_id}")
            raise HTTPException(
                status_code=404,
                detail=f"User ID {target_user_id} not found. Please run ensure_user_10.py script to create the default user."
            )
        
        # Handle chat session logic (async)
        chat_session_start = time.time()
        active_chat = None
        
        # If a specific chat_id is provided, try to use that chat first
        if request.chat_id:
            try:
                chat_id_int = int(request.chat_id)
                specific_chat_query = select(Chat).where(
                    Chat.id == chat_id_int,
                    Chat.user_id == user.id,
                )
                specific_chat_result = await db.execute(specific_chat_query)
                active_chat = specific_chat_result.scalar_one_or_none()
                
                if active_chat:
                    logger.info(f"🎯 USING SPECIFIC CHAT - Request ID: {request_id}, Chat ID: {active_chat.id}, Title: {active_chat.title}")
                else:
                    logger.warning(f"⚠️ SPECIFIC CHAT NOT FOUND - Request ID: {request_id}, Requested Chat ID: {request.chat_id}")
            except (ValueError, TypeError):
                logger.warning(f"⚠️ INVALID CHAT ID FORMAT - Request ID: {request_id}, Chat ID: {request.chat_id}")
        
        # If no specific chat found or provided, use the normal logic
        if not active_chat and request.is_new_chat:
            chat_type = _determine_chat_type(request.message)
            logger.info(f"🆕 CREATING NEW CHAT SESSION - Request ID: {request_id}, User: {target_user_id}, Chat Type: {chat_type}")
            
            # Check for existing empty chat session
            existing_chat_query = select(Chat).where(
                Chat.user_id == user.id,
                Chat.is_active == True
            ).order_by(Chat.last_activity.desc())
            
            existing_result = await db.execute(existing_chat_query)
            all_active_chats = existing_result.scalars().all()
            
            # Log if multiple active chats found and clean up
            if len(all_active_chats) > 1:
                logger.warning(f"⚠️ MULTIPLE ACTIVE CHATS FOUND - Request ID: {request_id}, User: {target_user_id}, Count: {len(all_active_chats)}")
                for i, chat in enumerate(all_active_chats):
                    logger.warning(f"   Chat {i+1}: ID={chat.id}, Messages={chat.message_count}, Last Activity={chat.last_activity}")
                
                # Clean up multiple active chats
                await cleanup_multiple_active_chats(db, user.id)
                
                # Re-query to get the remaining active chat
                existing_result = await db.execute(existing_chat_query)
                all_active_chats = existing_result.scalars().all()
            
            active_chat = all_active_chats[0] if all_active_chats else None
            
            if active_chat and active_chat.message_count == 0:
                # Update existing empty chat
                chat_type = _determine_chat_type(request.message)
                active_chat.title = _generate_chat_title(request.message)
                active_chat.chat_type = chat_type
                active_chat.tags = _extract_context_from_response(request.message)
                
                metadata = active_chat.chat_metadata or {}
                metadata.update({
                    "language": request.language,
                    "context": request.context,
                    "created_from": "new_chat",
                    "is_empty": False
                })
                active_chat.chat_metadata = metadata
                
                await db.commit()
                await db.refresh(active_chat)
            else:
                # Create completely new chat
                chat_type = _determine_chat_type(request.message)
                
                active_chat = Chat(
                    user_id=user.id,
                    title=_generate_chat_title(request.message),
                    chat_type=chat_type,
                    session_id=uuid.uuid4(),
                    chat_metadata={
                        "language": request.language,
                        "context": request.context,
                        "created_from": "new_chat"
                    },
                    tags=_extract_context_from_response(request.message)
                )
                db.add(active_chat)
                await db.commit()
                await db.refresh(active_chat)
        elif not active_chat:
            # Get existing active chat session (only if no specific chat was found)
            active_chat_query = select(Chat).where(
                Chat.user_id == user.id,
                Chat.is_active == True
            ).order_by(Chat.last_activity.desc())
            
            active_chat_result = await db.execute(active_chat_query)
            all_active_chats = active_chat_result.scalars().all()
            
            # Log if multiple active chats found and clean up
            if len(all_active_chats) > 1:
                logger.warning(f"⚠️ MULTIPLE ACTIVE CHATS FOUND - Request ID: {request_id}, User: {target_user_id}, Count: {len(all_active_chats)}")
                for i, chat in enumerate(all_active_chats):
                    logger.warning(f"   Chat {i+1}: ID={chat.id}, Messages={chat.message_count}, Last Activity={chat.last_activity}")
                
                # Clean up multiple active chats
                await cleanup_multiple_active_chats(db, user.id)
                
                # Re-query to get the remaining active chat
                active_chat_result = await db.execute(active_chat_query)
                all_active_chats = active_chat_result.scalars().all()
            
            active_chat = all_active_chats[0] if all_active_chats else None
            
            if not active_chat or (datetime.now() - active_chat.last_activity.replace(tzinfo=None)).total_seconds() > 3600:
                # Create new chat if none exists or too old
                chat_type = _determine_chat_type(request.message)
                
                active_chat = Chat(
                    user_id=user.id,
                    title=_generate_chat_title(request.message),
                    chat_type=chat_type,
                    session_id=uuid.uuid4(),
                    chat_metadata={
                        "language": request.language,
                        "context": request.context,
                        "created_from": "chat_query"
                    },
                    tags=_extract_context_from_response(request.message)
                )
                db.add(active_chat)
                await db.commit()
                await db.refresh(active_chat)
        
        chat_session_time = (time.time() - chat_session_start) * 1000
        
        logger.info(f"✅ CHAT SESSION READY - Request ID: {request_id}, Chat ID: {active_chat.id}, Session: {active_chat.session_id}, Type: {active_chat.chat_type}, Title: {active_chat.title}, Setup Time: {round(chat_session_time, 2)}ms")
        
        # Get conversation history (async)
        history_start = time.time()
        
        recent_messages_query = select(ChatMessage).where(
            ChatMessage.chat_id == active_chat.id
        ).order_by(ChatMessage.created_at.desc()).limit(10)
        
        messages_result = await db.execute(recent_messages_query)
        recent_messages = messages_result.scalars().all()
        
        conversation_history = []
        for msg in reversed(recent_messages):
            conversation_history.append({"role": "user", "content": msg.message})
            if msg.response:
                conversation_history.append({"role": "assistant", "content": msg.response})
        
        history_time = (time.time() - history_start) * 1000
        
        logger.info(f"📚 CONVERSATION HISTORY LOADED - Request ID: {request_id}, Chat ID: {active_chat.id}, Messages: {len(conversation_history)}, Load Time: {round(history_time, 2)}ms")
        
        # Generate AI response
        ai_start_time = time.time()
        
        logger.info(f"🤖 AI PROCESSING STARTED - Request ID: {request_id}, Message: {request.message[:50]}..., Language: {request.language}, Context: {request.context}, History Length: {len(conversation_history)}")
        
        ai_result = await ollama_service.generate_response(
            message=request.message,
            user_id=request.user_id,
            context=request.context,
            conversation_history=conversation_history,
            language=request.language
        )
        
        ai_time = (time.time() - ai_start_time) * 1000
        
        logger.info(f"✅ AI PROCESSING COMPLETED - Request ID: {request_id}, Success: {ai_result['success']}, Model: {ai_result['model']}, Time: {round(ai_time, 2)}ms, Response Length: {len(ai_result['response'])}, Tokens: {ai_result.get('tokens_used', 0)}")
        
        # Generate metadata
        message_id = f"msg_{uuid.uuid4().hex[:8]}"
        context_used = _extract_context_from_response(ai_result["response"])
        suggested_actions = _generate_suggested_actions(request.message, ai_result["response"])
        related_topics = _generate_related_topics(request.message, ai_result["response"])
        
        # Store chat message in database (async)
        db_save_start = time.time()
        
        total_processing_time = (time.time() - start_time) * 1000
        
        chat_message = ChatMessage(
            chat_id=active_chat.id,
            user_id=user.id,
            message=request.message,
            response=ai_result["response"],
            message_type="text",
            language=request.language,
            ai_model=ai_result["model"],
            tokens_used=ai_result.get("tokens_used", 0),
            response_time=total_processing_time / 1000,
            confidence_score=ai_result.get("confidence", 0.0),
            context_data={
                "context_used": context_used,
                "suggested_actions": suggested_actions,
                "related_topics": related_topics,
                "request_context": request.context
            }
        )
        db.add(chat_message)
        
        # Update chat metadata
        active_chat.message_count += 1
        active_chat.total_tokens += ai_result.get("tokens_used", 0)
        active_chat.last_activity = datetime.now()
        
        if active_chat.avg_response_time:
            active_chat.avg_response_time = (
                (active_chat.avg_response_time * (active_chat.message_count - 1) + 
                 total_processing_time / 1000) / active_chat.message_count
            )
        else:
            active_chat.avg_response_time = total_processing_time / 1000
        
        existing_tags = active_chat.tags or []
        new_tags = list(set(existing_tags + context_used))
        active_chat.tags = new_tags[:10]
        
        await db.commit()
        
        db_save_time = (time.time() - db_save_start) * 1000
        
        # Final comprehensive logging
        total_time = (time.time() - start_time) * 1000
        
        logger.info(f"🎉 CHAT QUERY COMPLETED SUCCESSFULLY - Request ID: {request_id}, User: {request.user_id}, Message ID: {message_id}, Chat ID: {active_chat.id}, Total Time: {round(total_time, 2)}ms, Performance: [DB Lookup: {round(db_user_time, 2)}ms, Chat Session: {round(chat_session_time, 2)}ms, History: {round(history_time, 2)}ms, AI: {round(ai_time, 2)}ms, DB Save: {round(db_save_time, 2)}ms], Response Length: {len(ai_result['response'])}, Context: {context_used}, Actions: {suggested_actions}, Topics: {related_topics}")
        
        # Log AI conversation
        ai_response_logger.log_ai_response(
            user_id=request.user_id,
            message_id=message_id,
            user_message=request.message,
            ai_response=ai_result["response"],
            model_used=ai_result["model"],
            processing_time_ms=ai_time,
            language=request.language,
            context=request.context,
            success=ai_result["success"],
            request_id=request_id
        )
        
        return ChatResponse(
            response=ai_result["response"],
            user_id=request.user_id,
            message_id=message_id,
            chat_id=str(active_chat.id),
            timestamp=datetime.now().isoformat(),
            context_used=context_used,
            suggested_actions=suggested_actions,
            related_topics=related_topics,
            ai_metadata=ai_result.get("metadata", {}),
            processing_time_seconds=round(total_time / 1000, 2),
            model_used=ai_result["model"]
        )
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        
        message_preview = request.message[:100] + "..." if len(request.message) > 100 else request.message
        logger.error(f"💥 CHAT QUERY FAILED - Request ID: {request_id}, User: {request.user_id}, Error: {type(e).__name__}: {str(e)}, Time: {round(processing_time, 2)}ms, Message: {message_preview}, Language: {request.language}", exc_info=True)
        
        error_tracker.log_validation_error(e, {
            "request_id": request_id,
            "user_id": request.user_id,
            "message": request.message[:100],
            "language": request.language
        })
        
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat query. Please try again later."
        )

@router.post("/new-session")
async def create_new_chat_session(
    request: NewChatSessionRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new chat session with async database operations and comprehensive logging.
    """
    start_time = time.time()
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    
    logger.info(f"🆕 NEW CHAT SESSION STARTED - Request ID: {request_id}, User: {request.user_id}, Language: {request.language}")
    
    try:
        target_user_id = 10
        
        # Get user (async)
        user_query = select(User).where(User.id == target_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            logger.error(f"❌ USER NOT FOUND FOR NEW SESSION - Request ID: {request_id}, Target User: {target_user_id}")
            raise HTTPException(
                status_code=404,
                detail=f"User ID {target_user_id} not found."
            )
        
        # Mark existing active chats as inactive (async)
        await db.execute(
            update(Chat)
            .where(Chat.user_id == user.id, Chat.is_active == True)
            .values(is_active=False)
        )
        
        # Create new chat session
        new_chat = Chat(
            user_id=user.id,
            title="New Chat",
            chat_type="general",
            session_id=uuid.uuid4(),
            chat_metadata={
                "language": request.language,
                "created_from": "new_session",
                "is_empty": True
            },
            tags=[]
        )
        db.add(new_chat)
        await db.commit()
        await db.refresh(new_chat)
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"✅ NEW CHAT SESSION CREATED - Request ID: {request_id}, User: {request.user_id}, Chat ID: {new_chat.id}, Session: {new_chat.session_id}, Time: {round(processing_time, 2)}ms")
        
        return {
            "chat_id": str(new_chat.id),
            "session_id": str(new_chat.session_id),
            "title": new_chat.title,
            "chat_type": new_chat.chat_type,
            "created_at": new_chat.created_at.isoformat(),
            "status": "success",
            "message": "New chat session created successfully",
            "processing_time_ms": round(processing_time, 2)
        }
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        
        logger.error(f"💥 NEW CHAT SESSION FAILED - Request ID: {request_id}, User: {request.user_id}, Error: {type(e).__name__}: {str(e)}, Time: {round(processing_time, 2)}ms", exc_info=True)
        
        raise HTTPException(
            status_code=500,
            detail="Failed to create new chat session"
        )

@router.get("/sessions/{user_id}")
async def get_chat_sessions(
    user_id: str,
    request: Request,
    limit: int = Query(10, ge=1, le=50, description="Number of chat sessions to return"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get chat sessions for a user with async database operations and comprehensive logging.
    """
    start_time = time.time()
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"📂 CHAT SESSIONS REQUEST STARTED - Request ID: {request_id}, User: {user_id}, Limit: {limit}")
    
    try:
        # Always use user ID 10 for chat operations
        target_user_id = 10
        
        # Get user (async)
        user_query = select(User).where(User.id == target_user_id)
        user_result = await db.execute(user_query)
        
        user = user_result.scalar_one_or_none()
        logger.info(user.id)
        if not user:
            logger.warning(f"❌ USER NOT FOUND FOR SESSIONS - Request ID: {request_id}, Target User: {target_user_id}, Requested User: {user_id}")
            return {
                "user_id": str(target_user_id),
                "sessions": [],
                "total_sessions": 0,
                "status": "user_not_found",
                "message": f"User ID {target_user_id} not found."
            }
        
        # Get chat sessions (async)
        sessions_query = select(Chat).where(
            Chat.user_id == user.id
        ).order_by(Chat.last_activity.desc()).limit(limit)
        
        sessions_result = await db.execute(sessions_query)
        sessions = sessions_result.scalars().all()
        
        # Format sessions
        formatted_sessions = []
        for session in sessions:
            formatted_session = {
                "session_id": str(session.session_id),
                "chat_id": session.id,
                "title": session.title or "Untitled Chat",
                "chat_type": session.chat_type or "general",
                "message_count": session.message_count or 0,
                "total_tokens": session.total_tokens or 0,
                "avg_response_time": float(session.avg_response_time) if session.avg_response_time else 0.0,
                "user_rating": session.user_rating,
                "tags": session.tags or [],
                "is_favorite": session.is_favorite or False,
                "last_activity": session.last_activity.isoformat() if session.last_activity else datetime.now().isoformat(),
                "created_at": session.created_at.isoformat() if session.created_at else datetime.now().isoformat(),
                "chat_metadata": session.chat_metadata or {}
            }
            formatted_sessions.append(formatted_session)
        
        # Get total session count
        count_query = select(Chat).where(
            Chat.user_id == user.id,
            Chat.is_active == True
        )
        count_result = await db.execute(count_query)
        total_sessions = len(count_result.scalars().all())
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"✅ CHAT SESSIONS REQUEST COMPLETED - Request ID: {request_id}, User: {user_id}, Sessions Returned: {len(formatted_sessions)}, Total: {total_sessions}, Time: {round(processing_time, 2)}ms")
        
        return {
            "user_id": str(target_user_id),
            "database_user_id": target_user_id,
            "requested_user_id": user_id,
            "sessions": formatted_sessions,
            "total_sessions": total_sessions,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        
        logger.error(f"💥 CHAT SESSIONS REQUEST FAILED - Request ID: {request_id}, User: {user_id}, Error: {type(e).__name__}: {str(e)}, Time: {round(processing_time, 2)}ms", exc_info=True)
        
        return {
            "user_id": str(10),
            "database_user_id": 10,
            "requested_user_id": user_id,
            "sessions": [],
            "total_sessions": 0,
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error_message": "Unable to fetch chat sessions at this time."
        }

@router.get("/messages/{chat_id}")
async def get_chat_messages(
    chat_id: str,
    request: Request,
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(100, ge=1, le=200, description="Number of messages to return"),
    offset: int = Query(0, ge=0, description="Number of messages to skip"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get messages for a specific chat with async database operations and comprehensive logging.
    """
    start_time = time.time()
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"📨 CHAT MESSAGES REQUEST STARTED - Request ID: {request_id}, Chat: {chat_id}, User: {user_id}, Limit: {limit}, Offset: {offset}")
    
    try:
        target_user_id = 10
        
        # Get user first to verify ownership
        user_query = select(User).where(User.id == target_user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            logger.warning(f"❌ USER NOT FOUND FOR MESSAGES - Request ID: {request_id}, Target User: {target_user_id}, Requested User: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get chat (async) - verify it belongs to the user
        chat_query = select(Chat).where(
            Chat.id == int(chat_id),
            Chat.user_id == user.id  # Ensure chat belongs to the user
        )
        chat_result = await db.execute(chat_query)
        chat = chat_result.scalar_one_or_none()
        
        if not chat:
            logger.warning(f"❌ CHAT NOT FOUND OR ACCESS DENIED - Request ID: {request_id}, Chat: {chat_id}, User: {user_id}, Target User: {target_user_id}")
            raise HTTPException(status_code=404, detail="Chat not found or access denied")
        
        # Get messages (async)
        messages_query = select(ChatMessage).where(
            ChatMessage.chat_id == chat.id
        ).order_by(ChatMessage.created_at.asc()).offset(offset).limit(limit)
        
        messages_result = await db.execute(messages_query)
        messages = messages_result.scalars().all()
        
        # Get total message count
        total_count_query = select(ChatMessage).where(ChatMessage.chat_id == chat.id)
        total_count_result = await db.execute(total_count_query)
        total_messages = len(total_count_result.scalars().all())
        
        # Format messages for frontend
        formatted_messages = []
        for msg in messages:
            # Add user message
            formatted_messages.append({
                "message_id": f"msg_{msg.id}",
                "role": "user",
                "content": msg.message,
                "timestamp": msg.created_at.isoformat(),
                "language": msg.language,
                "message_type": msg.message_type
            })
            
            # Add assistant response if exists
            if msg.response:
                formatted_messages.append({
                    "message_id": f"msg_{msg.id}_response",
                    "role": "assistant", 
                    "content": msg.response,
                    "timestamp": msg.created_at.isoformat(),
                    "response_time": f"{msg.response_time}s" if msg.response_time else None,
                    "ai_model": msg.ai_model,
                    "tokens_used": msg.tokens_used,
                    "confidence_score": msg.confidence_score,
                    "context_data": msg.context_data
                })
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(f"✅ CHAT MESSAGES REQUEST COMPLETED - Request ID: {request_id}, Chat: {chat_id}, User: {user_id}, Messages Returned: {len(formatted_messages)}, Total: {total_messages}, Time: {round(processing_time, 2)}ms")
        
        return {
            "chat_id": chat_id,
            "user_id": str(target_user_id),
            "requested_user_id": user_id,
            "chat_info": {
                "title": chat.title,
                "chat_type": chat.chat_type,
                "session_id": str(chat.session_id),
                "created_at": chat.created_at.isoformat(),
                "last_activity": chat.last_activity.isoformat(),
                "message_count": chat.message_count,
                "total_tokens": chat.total_tokens,
                "avg_response_time": chat.avg_response_time,
                "user_rating": chat.user_rating,
                "tags": chat.tags or [],
                "is_favorite": chat.is_favorite,
                "chat_metadata": chat.chat_metadata or {}
            },
            "messages": formatted_messages,
            "pagination": {
                "total_messages": total_messages,
                "returned_count": len(formatted_messages),
                "limit": limit,
                "offset": offset,
                "has_more": (offset + len(formatted_messages)) < total_messages
            },
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        
        logger.error(f"💥 CHAT MESSAGES REQUEST FAILED - Request ID: {request_id}, Chat: {chat_id}, User: {user_id}, Error: {type(e).__name__}: {str(e)}, Time: {round(processing_time, 2)}ms", exc_info=True)
        
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch chat messages"
        )

@router.get("/database-status")
async def get_database_status(request: Request):
    """
    Get comprehensive database status and performance metrics.
    """
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"🔍 DATABASE STATUS CHECK STARTED - Request ID: {request_id}")
    
    try:
        # Test async database connection
        async_status = await test_async_database_connection()
        
        logger.info(f"✅ DATABASE STATUS CHECK COMPLETED - Request ID: {request_id}, Status: {async_status['status']}, Connection Time: {async_status.get('connection_time_ms', 0)}ms, Performance: {async_status.get('performance_rating', 'unknown')}")
        
        return {
            "async_database": async_status,
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "status": "healthy" if async_status["status"] == "connected" else "degraded"
        }
        
    except Exception as e:
        logger.error(f"💥 DATABASE STATUS CHECK FAILED - Request ID: {request_id}, Error: {type(e).__name__}: {str(e)}", exc_info=True)
        
        return {
            "async_database": {
                "status": "failed",
                "error": str(e),
                "error_type": type(e).__name__
            },
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "status": "error"
        }