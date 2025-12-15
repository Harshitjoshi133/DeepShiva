from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import logging
from datetime import datetime, timedelta
import json

from ..services.ollama_service import OllamaService
from ..services.tts_service import tts_service
from ..database import get_db
import sqlite3

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/meditation", tags=["meditation"])

class MeditationGuidanceRequest(BaseModel):
    meditation_type: str
    phase: str
    duration: int

class MeditationSession(BaseModel):
    meditation_type: str
    duration: int
    completed: bool
    user_rating: Optional[int] = None
    notes: Optional[str] = None

class UserPreferences(BaseModel):
    preferred_types: List[str]
    preferred_duration: int
    experience_level: str
    goals: List[str]

class VoiceSettings(BaseModel):
    rate: Optional[str] = "slow"  # 'slow' or 'normal'
    lang: Optional[str] = "en"    # Language code
    tld: Optional[str] = "com"    # Top-level domain for accent

class TTSRequest(BaseModel):
    text: str
    voice_settings: Optional[VoiceSettings] = None
    language: Optional[str] = "en"

@router.post("/guidance")
async def get_meditation_guidance(request: MeditationGuidanceRequest):
    """Get AI-generated meditation guidance based on type and phase"""
    # Generate a user_id for meditation sessions (could be enhanced with actual user auth)
    user_id = f"meditation_user_{hash(str(request.dict())) % 10000}"
    
    try:
        ollama_service = OllamaService()
        
        # Create a detailed prompt for meditation guidance
        guidance_prompts = {
            "setup": {
                "mindfulness": "Guide the user to find a comfortable seated position for mindfulness meditation. Help them prepare their mind and body for present-moment awareness. Include breathing preparation and posture guidance.",
                "loving-kindness": "Help the user prepare for loving-kindness meditation. Guide them to place their hand on their heart, connect with feelings of warmth and compassion, and set an intention for the practice.",
                "nature": "Guide the user to imagine themselves in a peaceful natural setting. Help them connect with the elements - earth, air, water, and fire. Prepare them to feel their connection to the natural world.",
                "sleep": "Help the user prepare for sleep meditation. Guide them to lie down comfortably, release the tensions of the day, and prepare their mind and body for deep rest.",
                "energy": "Guide the user to sit with good posture for an energizing meditation. Help them connect with their inner vitality and prepare to awaken their life force energy."
            },
            "breathing": {
                "mindfulness": "Guide focused breathing for mindfulness. Instruct on observing the natural breath without changing it, noticing the sensations of breathing, and gently returning attention when the mind wanders.",
                "loving-kindness": "Guide breathing with loving-kindness. Instruct on breathing in love and compassion for oneself, breathing out any self-criticism or tension. Include phrases like 'May I be happy, may I be peaceful.'",
                "nature": "Guide nature-connected breathing. Instruct on breathing in the life force of nature, imagining breathing with trees and plants, feeling the connection to all living beings through breath.",
                "sleep": "Guide relaxing breath for sleep preparation. Instruct on slow, deep breathing that releases tension with each exhale, helping the body become heavier and more relaxed.",
                "energy": "Guide energizing breath work. Instruct on breathing in bright, golden energy, feeling it fill the body with vitality and strength, awakening inner power."
            },
            "meditation": {
                "mindfulness": "Guide deep mindfulness practice. Instruct on resting in present-moment awareness, observing thoughts and feelings without judgment, being the witness of experience.",
                "loving-kindness": "Guide loving-kindness meditation. Instruct on sending love to oneself, then to loved ones, neutral people, difficult people, and finally all beings everywhere.",
                "nature": "Guide nature connection meditation. Instruct on feeling unity with all life, sensing the interconnectedness of all beings, resting in the wisdom of the natural world.",
                "sleep": "Guide sleep meditation. Instruct on complete letting go, trusting the body's natural healing processes, releasing all concerns and worries.",
                "energy": "Guide energy cultivation meditation. Instruct on feeling energy circulating through the body, connecting with inner strength and vitality, awakening potential."
            }
        }
        
        base_prompt = guidance_prompts.get(request.phase, {}).get(request.meditation_type, "Focus on your breath and be present.")
        
        prompt = f"""You are a wise and compassionate meditation teacher. Provide gentle, calming guidance for a {request.meditation_type} meditation in the {request.phase} phase, lasting {request.duration} minutes.

{base_prompt}

Provide 2-3 sentences of gentle, soothing guidance. Use calming language and speak directly to the meditator. Keep it simple and peaceful. Do not use any special formatting or bullet points."""

        # Call generate_response with all required parameters
        response = await ollama_service.generate_response(
            message=prompt,
            user_id=user_id,
            context=f"Meditation guidance for {request.meditation_type} meditation, {request.phase} phase",
            language="en"
        )
        
        logger.info(f"Generated meditation guidance successfully - Type: {request.meditation_type}, Phase: {request.phase}, User: {user_id}")
        
        return {
            "guidance": response.get("response", "Focus on your breath and be present in this moment."),
            "meditation_type": request.meditation_type,
            "phase": request.phase,
            "duration": request.duration,
            "success": response.get("success", False),
            "model_used": response.get("model", "unknown")
        }
        
    except Exception as e:
        logger.error(f"Error generating meditation guidance: {e}", exc_info=True)
        
        # Enhanced fallback guidance with more variety
        fallback_guidance = {
            "setup": {
                "mindfulness": "Find a comfortable seated position with your spine straight but relaxed. Close your eyes gently and take three deep breaths. Allow your body to settle and your mind to become present.",
                "loving-kindness": "Sit comfortably and place your hand on your heart. Feel the warmth and rhythm of your heartbeat. Set an intention to cultivate love and compassion for yourself and others.",
                "nature": "Imagine yourself in a peaceful natural setting - perhaps a forest, mountain, or by a flowing river. Feel the earth beneath you and the air around you. Connect with the natural world.",
                "sleep": "Lie down comfortably and let your body sink into complete relaxation. Release the tensions and worries of the day. Prepare your mind and body for peaceful, restorative sleep.",
                "energy": "Sit tall with your spine straight and shoulders relaxed. Feel the energy flowing through your body. Take a moment to connect with your inner vitality and life force."
            },
            "breathing": {
                "mindfulness": "Focus on your natural breath without trying to change it. Notice the sensation of air flowing in and out. When your mind wanders, gently guide your attention back to your breath.",
                "loving-kindness": "Breathe in love and compassion for yourself. With each exhale, release any self-criticism or tension. You are worthy of love and kindness just as you are.",
                "nature": "Breathe in the fresh, clean air of nature. Imagine breathing in the life force of trees and plants around you. Feel your connection to all living beings through your breath.",
                "sleep": "Let each exhale release more tension from your body. Feel yourself becoming heavier and more relaxed with each breath. Allow sleep to come naturally.",
                "energy": "Breathe in bright, golden energy. Feel it filling your body with vitality and strength. With each breath, awaken your inner power and potential."
            },
            "meditation": {
                "mindfulness": "Rest in the present moment. Notice thoughts and feelings as they arise, without judgment. You are the peaceful observer of your experience.",
                "loving-kindness": "Send loving thoughts first to yourself, then to your loved ones, and finally to all beings everywhere. May all beings be happy, peaceful, and free from suffering.",
                "nature": "Feel your deep connection to all living things. You are part of the web of life, connected to earth, sky, and all creatures. Rest in this unity.",
                "sleep": "Let go of the day completely. Trust in your body's natural wisdom to restore and heal during sleep. Release all concerns and drift into peaceful rest.",
                "energy": "Feel the energy circulating through your body like a gentle current. You are vibrant, alive, and full of unlimited potential. Embrace your inner strength."
            }
        }
        
        # Get fallback guidance with type-specific content
        phase_guidance = fallback_guidance.get(request.phase, {})
        guidance = phase_guidance.get(request.meditation_type, "Focus on your breath and be present in this moment. Allow yourself to simply be here, now.")
        
        return {
            "guidance": guidance,
            "meditation_type": request.meditation_type,
            "phase": request.phase,
            "duration": request.duration,
            "success": False,
            "model_used": "fallback",
            "error": "AI service temporarily unavailable, using fallback guidance"
        }

@router.post("/sessions")
async def save_meditation_session(session: MeditationSession, db: sqlite3.Connection = Depends(get_db)):
    """Save a completed meditation session"""
    try:
        cursor = db.cursor()
        
        # Create meditation_sessions table if it doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meditation_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                meditation_type TEXT NOT NULL,
                duration INTEGER NOT NULL,
                completed BOOLEAN NOT NULL,
                user_rating INTEGER,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert the session
        cursor.execute("""
            INSERT INTO meditation_sessions (meditation_type, duration, completed, user_rating, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (session.meditation_type, session.duration, session.completed, session.user_rating, session.notes))
        
        db.commit()
        session_id = cursor.lastrowid
        
        logger.info(f"Saved meditation session: {session_id}")
        
        return {
            "id": session_id,
            "message": "Meditation session saved successfully",
            "session": session.dict()
        }
        
    except Exception as e:
        logger.error(f"Error saving meditation session: {e}")
        raise HTTPException(status_code=500, detail="Failed to save meditation session")

@router.get("/history")
async def get_meditation_history(db: sqlite3.Connection = Depends(get_db)):
    """Get user's meditation history"""
    try:
        cursor = db.cursor()
        
        # Get recent meditation sessions
        cursor.execute("""
            SELECT id, meditation_type, duration, completed, user_rating, notes, created_at
            FROM meditation_sessions
            ORDER BY created_at DESC
            LIMIT 50
        """)
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append({
                "id": row[0],
                "meditation_type": row[1],
                "duration": row[2],
                "completed": bool(row[3]),
                "user_rating": row[4],
                "notes": row[5],
                "created_at": row[6]
            })
        
        # Get statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_sessions,
                SUM(duration) as total_minutes,
                AVG(user_rating) as avg_rating,
                COUNT(CASE WHEN completed = 1 THEN 1 END) as completed_sessions
            FROM meditation_sessions
        """)
        
        stats_row = cursor.fetchone()
        stats = {
            "total_sessions": stats_row[0] or 0,
            "total_minutes": stats_row[1] or 0,
            "average_rating": round(stats_row[2] or 0, 1),
            "completed_sessions": stats_row[3] or 0
        }
        
        return {
            "sessions": sessions,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting meditation history: {e}")
        return {
            "sessions": [],
            "statistics": {
                "total_sessions": 0,
                "total_minutes": 0,
                "average_rating": 0,
                "completed_sessions": 0
            }
        }

@router.post("/recommendations")
async def get_meditation_recommendations(preferences: UserPreferences):
    """Get personalized meditation recommendations"""
    # Generate a user_id for recommendations
    user_id = f"recommendations_user_{hash(str(preferences.dict())) % 10000}"
    
    try:
        ollama_service = OllamaService()
        
        prompt = f"""You are a meditation expert. Based on the user's preferences, provide personalized meditation recommendations.

User Preferences:
- Preferred types: {', '.join(preferences.preferred_types)}
- Preferred duration: {preferences.preferred_duration} minutes
- Experience level: {preferences.experience_level}
- Goals: {', '.join(preferences.goals)}

Provide 3-5 specific meditation recommendations. For each recommendation, include:
1. Type of meditation (mindfulness, loving-kindness, nature, sleep, or energy)
2. Suggested duration in minutes
3. Brief description of the practice
4. Key benefits
5. Why it matches their preferences

Respond in a clear, structured format but avoid JSON formatting. Use simple text with clear sections."""

        # Call generate_response with all required parameters
        response = await ollama_service.generate_response(
            message=prompt,
            user_id=user_id,
            context=f"Meditation recommendations for user with {preferences.experience_level} experience level",
            language="en"
        )
        
        # Parse the AI response into structured recommendations
        ai_text = response.get("response", "")
        
        # Create structured recommendations from AI response
        recommendations = []
        
        # If AI response is available, try to extract recommendations
        if ai_text and response.get("success", False):
            # For now, create intelligent recommendations based on preferences
            base_recommendations = [
                {
                    "type": "mindfulness",
                    "duration": preferences.preferred_duration,
                    "description": "Present-moment awareness meditation focusing on breath and body sensations",
                    "benefits": "Reduces stress, improves focus, enhances emotional regulation",
                    "match_reason": "Excellent foundation for all meditation practices"
                },
                {
                    "type": "loving-kindness",
                    "duration": max(5, preferences.preferred_duration - 5),
                    "description": "Cultivate compassion and love for yourself and others",
                    "benefits": "Improves emotional well-being, enhances relationships, reduces negative emotions",
                    "match_reason": "Perfect for developing positive mental states"
                },
                {
                    "type": "nature",
                    "duration": preferences.preferred_duration,
                    "description": "Connect with natural elements and feel unity with all life",
                    "benefits": "Increases environmental awareness, provides grounding, enhances peace",
                    "match_reason": "Ideal for those seeking deeper spiritual connection"
                }
            ]
            
            # Filter based on user preferences
            if preferences.preferred_types:
                recommendations = [r for r in base_recommendations if r["type"] in preferences.preferred_types]
            else:
                recommendations = base_recommendations[:3]
                
        else:
            # Fallback recommendations
            recommendations = [
                {
                    "type": "mindfulness",
                    "duration": preferences.preferred_duration or 10,
                    "description": "Basic mindfulness meditation focusing on breath awareness",
                    "benefits": "Reduces stress, improves focus and emotional regulation",
                    "match_reason": "Suitable for all experience levels and goals"
                },
                {
                    "type": "loving-kindness",
                    "duration": max(5, (preferences.preferred_duration or 10) - 5),
                    "description": "Cultivate compassion and love for self and others",
                    "benefits": "Improves emotional well-being and relationships",
                    "match_reason": "Helps develop positive emotions and reduce stress"
                }
            ]
        
        logger.info(f"Generated meditation recommendations successfully - User: {user_id}, Count: {len(recommendations)}")
        
        return {
            "recommendations": recommendations,
            "user_preferences": preferences.dict(),
            "ai_response": ai_text if response.get("success", False) else None,
            "success": True,
            "model_used": response.get("model", "fallback")
        }
        
    except Exception as e:
        logger.error(f"Error generating meditation recommendations: {e}", exc_info=True)
        
        # Enhanced fallback recommendations based on preferences
        fallback_recommendations = []
        
        # Mindfulness - always include as it's foundational
        fallback_recommendations.append({
            "type": "mindfulness",
            "duration": preferences.preferred_duration or 10,
            "description": "Basic mindfulness meditation focusing on breath awareness and present-moment attention",
            "benefits": "Reduces stress, improves focus, enhances emotional regulation and self-awareness",
            "match_reason": "Foundational practice suitable for all experience levels and meditation goals"
        })
        
        # Add recommendations based on experience level
        if preferences.experience_level == "beginner":
            fallback_recommendations.append({
                "type": "loving-kindness",
                "duration": max(5, (preferences.preferred_duration or 10) - 5),
                "description": "Gentle practice of sending love and compassion to yourself and others",
                "benefits": "Improves emotional well-being, reduces self-criticism, enhances relationships",
                "match_reason": "Beginner-friendly practice that builds positive mental states"
            })
        else:
            fallback_recommendations.extend([
                {
                    "type": "nature",
                    "duration": preferences.preferred_duration or 15,
                    "description": "Connect with natural elements and feel your unity with all living beings",
                    "benefits": "Increases environmental awareness, provides grounding, enhances spiritual connection",
                    "match_reason": "Advanced practice for deepening spiritual awareness and connection"
                },
                {
                    "type": "energy",
                    "duration": max(10, (preferences.preferred_duration or 15) - 5),
                    "description": "Awaken and circulate life force energy throughout your body",
                    "benefits": "Increases vitality, enhances mental clarity, boosts motivation and focus",
                    "match_reason": "Energizing practice perfect for experienced meditators seeking vitality"
                }
            ])
        
        return {
            "recommendations": fallback_recommendations,
            "user_preferences": preferences.dict(),
            "success": False,
            "model_used": "fallback",
            "error": "AI service temporarily unavailable, using intelligent fallback recommendations"
        }

@router.get("/types")
async def get_meditation_types():
    """Get available meditation types with descriptions"""
    return {
        "types": [
            {
                "id": "mindfulness",
                "name": "Mindfulness",
                "description": "Focus on present moment awareness and breath observation",
                "benefits": ["Stress reduction", "Improved focus", "Emotional regulation"],
                "difficulty": "beginner"
            },
            {
                "id": "loving-kindness",
                "name": "Loving Kindness",
                "description": "Cultivate compassion and love for self and others",
                "benefits": ["Increased empathy", "Better relationships", "Emotional healing"],
                "difficulty": "beginner"
            },
            {
                "id": "nature",
                "name": "Nature Connection",
                "description": "Connect with natural elements and feel unity with life",
                "benefits": ["Environmental awareness", "Grounding", "Peace"],
                "difficulty": "intermediate"
            },
            {
                "id": "sleep",
                "name": "Sleep Preparation",
                "description": "Prepare mind and body for restful sleep",
                "benefits": ["Better sleep quality", "Relaxation", "Stress relief"],
                "difficulty": "beginner"
            },
            {
                "id": "energy",
                "name": "Energy Boost",
                "description": "Awaken inner vitality and increase life force energy",
                "benefits": ["Increased energy", "Mental clarity", "Motivation"],
                "difficulty": "intermediate"
            }
        ]
    }

@router.post("/guidance/audio")
async def get_meditation_guidance_with_audio(request: MeditationGuidanceRequest):
    """Get AI-generated meditation guidance with voice audio"""
    # Generate a user_id for meditation sessions
    user_id = f"meditation_audio_user_{hash(str(request.dict())) % 10000}"
    
    try:
        # First get the text guidance
        text_response = await get_meditation_guidance(request)
        
        if not text_response.get("success", True):
            # Return text-only response if guidance generation failed
            return text_response
        
        guidance_text = text_response.get("guidance", "")
        
        if not guidance_text:
            raise Exception("No guidance text available for TTS conversion")
        
        # Convert text to speech using base64 approach
        tts_result = await tts_service.text_to_speech_base64(
            text=guidance_text,
            voice_settings={"rate": "slow", "lang": "en", "tld": "com"},  # Slower for meditation
            language="en"
        )
        
        logger.info(f"Generated meditation guidance with audio - Type: {request.meditation_type}, Phase: {request.phase}")
        
        return {
            **text_response,  # Include all text response data
            "audio_base64": tts_result.get("audio_base64"),
            "audio_format": tts_result.get("audio_format", "wav"),
            "has_audio": True,
            "tts_processing_time_ms": tts_result.get("processing_time_ms", 0)
        }
            
    except Exception as e:
        logger.error(f"Error generating meditation guidance with audio: {e}", exc_info=True)
        
        # For voice-guided meditation, TTS failure is critical - throw error
        raise HTTPException(
            status_code=503, 
            detail=f"Voice-guided meditation unavailable: {str(e)}. Please ensure TTS service is properly configured."
        )

@router.post("/tts/convert")
async def convert_text_to_speech(request: TTSRequest):
    """Convert text to speech audio (base64 response)"""
    try:
        logger.info(f"Converting text to speech (base64) - Length: {len(request.text)}, Language: {request.language}")
        
        # Prepare voice settings
        voice_settings = {}
        if request.voice_settings:
            voice_settings = {
                "rate": request.voice_settings.rate or "slow",
                "lang": request.voice_settings.lang or "en",
                "tld": request.voice_settings.tld or "com"
            }
        
        # Convert text to speech
        result = await tts_service.text_to_speech_base64(
            text=request.text,
            voice_settings=voice_settings,
            language=request.language or "en"
        )
        
        logger.info(f"TTS conversion successful - Audio size: {len(result.get('audio_base64', ''))} chars")
        return result
            
    except Exception as e:
        logger.error(f"Error in TTS conversion endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts/stream")
async def convert_text_to_speech_stream(request: TTSRequest):
    """Convert text to speech audio (streaming response like your Voice AI Agent)"""
    try:
        logger.info(f"Converting text to speech (streaming) - Length: {len(request.text)}, Language: {request.language}")
        
        # Convert text to speech with streaming response
        streaming_response = await tts_service.text_to_speech_streaming(
            text=request.text,
            language=request.language or "en"
        )
        
        logger.info("TTS streaming conversion successful")
        return streaming_response
            
    except Exception as e:
        logger.error(f"Error in TTS streaming endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tts/voices")
async def get_available_voices():
    """Get list of available TTS voices"""
    try:
        voices_info = tts_service.get_available_voices()
        
        if voices_info.get("success"):
            logger.info(f"Retrieved {len(voices_info.get('voices', []))} available voices")
            return voices_info
        else:
            logger.error(f"Failed to get voices: {voices_info.get('error')}")
            raise HTTPException(status_code=500, detail=voices_info.get("error", "Failed to get voices"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting available voices: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tts/settings")
async def update_voice_settings(settings: VoiceSettings):
    """Update TTS voice settings"""
    try:
        settings_dict = {
            "rate": settings.rate,
            "volume": settings.volume,
            "voice_id": settings.voice_id
        }
        
        success = tts_service.update_voice_settings({
            "rate": settings.rate,
            "lang": settings.lang,
            "tld": settings.tld
        })
        
        if success:
            logger.info(f"Voice settings updated successfully")
            return {
                "success": True,
                "message": "Voice settings updated successfully",
                "settings": {
                    "rate": settings.rate,
                    "lang": settings.lang,
                    "tld": settings.tld
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update voice settings")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating voice settings: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/audio-sequence")
async def generate_meditation_audio_sequence(
    meditation_type: str,
    duration: int,
    voice_settings: Optional[VoiceSettings] = None
):
    """Generate complete audio sequence for a meditation session"""
    user_id = f"audio_sequence_user_{hash(f'{meditation_type}_{duration}') % 10000}"
    
    try:
        logger.info(f"Generating complete audio sequence - Type: {meditation_type}, Duration: {duration}min")
        
        # Generate guidance for all phases
        phases = ["setup", "breathing", "meditation"]
        guidance_texts = {}
        timings = {
            "setup": 60,  # 1 minute setup
            "breathing": min(300, duration * 20),  # 20% of session or max 5 minutes
            "meditation": max(180, duration * 60 - 360)  # Remaining time, minimum 3 minutes
        }
        
        # Get guidance text for each phase
        for phase in phases:
            try:
                guidance_request = MeditationGuidanceRequest(
                    meditation_type=meditation_type,
                    phase=phase,
                    duration=duration
                )
                
                guidance_response = await get_meditation_guidance(guidance_request)
                guidance_texts[phase] = guidance_response.get("guidance", "")
                
            except Exception as e:
                logger.error(f"Failed to get guidance for phase {phase}: {e}")
                guidance_texts[phase] = f"Focus on your {phase} practice and be present."
        
        # Prepare voice settings
        voice_settings_dict = {}
        if voice_settings:
            voice_settings_dict = {
                "rate": voice_settings.rate or "slow",  # Slower for meditation
                "lang": voice_settings.lang or "en",
                "tld": voice_settings.tld or "com"
            }
        
        # Generate audio sequence
        audio_result = await tts_service.generate_meditation_audio_sequence(
            guidance_texts=guidance_texts,
            timings=timings,
            voice_settings=voice_settings_dict
        )
        
        if audio_result.get("success"):
            logger.info(f"Audio sequence generated successfully - Phases: {audio_result.get('successful_phases')}/{audio_result.get('total_phases')}")
            
            return {
                **audio_result,
                "meditation_type": meditation_type,
                "duration": duration,
                "timings": timings,
                "voice_settings": voice_settings_dict
            }
        else:
            raise Exception(audio_result.get("error", "Failed to generate audio sequence"))
            
    except Exception as e:
        logger.error(f"Error generating meditation audio sequence: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))