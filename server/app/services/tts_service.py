"""
Text-to-Speech Service for Deep-Shiva API
Handles conversion of meditation guidance text to natural voice audio using streaming approach
"""

import asyncio
import io
import base64
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from fastapi.responses import StreamingResponse

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

from ..config import settings
from ..logging_config import get_logger

logger = get_logger("tts_service")

class TTSService:
    """Service class for Text-to-Speech conversion"""
    
    def __init__(self):
        self.voice_settings = {
            'rate': 'slow',  # 'slow' or 'normal' for meditation
            'lang': 'en',    # Language code
            'tld': 'com'     # Top-level domain for accent
        }
        
        # Validate TTS availability - REQUIRED for voice-guided meditation
        if not GTTS_AVAILABLE:
            error_msg = "gTTS not available. Voice-guided meditation requires gTTS for streaming audio."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        logger.info(f"TTS Service initialized successfully - gTTS: {GTTS_AVAILABLE}")
    
    def _is_tts_available(self) -> bool:
        """Check if TTS engine is available"""
        return GTTS_AVAILABLE
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages for gTTS"""
        return {
            "en": "English",
            "hi": "Hindi",
            "es": "Spanish", 
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "ru": "Russian",
            "ja": "Japanese",
            "ko": "Korean",
            "zh": "Chinese"
        }
    
    async def text_to_speech_streaming(
        self,
        text: str,
        language: str = "en"
    ) -> StreamingResponse:
        """
        Convert text to speech and return as streaming audio response
        
        Args:
            text: Text to convert to speech
            language: Language code for TTS
            
        Returns:
            StreamingResponse with audio data
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Converting text to speech (streaming) - Length: {len(text)}, Language: {language}")
            
            # Map language codes for gTTS
            lang_map = {
                "en": "en",
                "hi": "hi", 
                "ga": "hi"  # Use Hindi for Garhwali
            }
            
            tts_lang = lang_map.get(language, "en")
            
            # Create gTTS object with slow speech for meditation
            tts = gTTS(
                text=text, 
                lang=tts_lang, 
                slow=True,  # Slower speech for meditation
                tld='com'   # Use .com for consistent accent
            )
            
            # Generate audio to BytesIO buffer
            audio_buffer = io.BytesIO()
            await asyncio.to_thread(tts.write_to_fp, audio_buffer)
            audio_buffer.seek(0)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.info(f"TTS streaming conversion successful - Time: {processing_time:.2f}ms")
            
            # Return streaming response
            return StreamingResponse(
                audio_buffer, 
                media_type="audio/mpeg",
                headers={
                    "Content-Disposition": "inline; filename=meditation_guidance.mp3",
                    "X-Processing-Time": str(round(processing_time, 2)),
                    "X-Text-Length": str(len(text)),
                    "X-Language": tts_lang
                }
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            error_msg = f"TTS streaming conversion failed: {e}"
            logger.error(f"{error_msg}, Time: {processing_time:.2f}ms")
            
            # For voice-guided meditation, TTS failure is critical
            raise Exception(f"Voice generation failed: {str(e)}. Voice-guided meditation requires working TTS.")

    async def text_to_speech_base64(
        self,
        text: str,
        voice_settings: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Convert text to speech and return as base64 encoded audio
        
        Args:
            text: Text to convert to speech
            voice_settings: Optional voice configuration
            language: Language code for TTS
            
        Returns:
            Dict containing base64 audio data and metadata
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Converting text to speech (base64) - Length: {len(text)}, Language: {language}")
            
            # Map language codes for gTTS
            lang_map = {
                "en": "en",
                "hi": "hi", 
                "ga": "hi"  # Use Hindi for Garhwali
            }
            
            tts_lang = lang_map.get(language, "en")
            
            # Create gTTS object with slow speech for meditation
            tts = gTTS(
                text=text, 
                lang=tts_lang, 
                slow=True,  # Slower speech for meditation
                tld='com'   # Use .com for consistent accent
            )
            
            # Generate audio to BytesIO buffer
            audio_buffer = io.BytesIO()
            await asyncio.to_thread(tts.write_to_fp, audio_buffer)
            audio_buffer.seek(0)
            
            # Get audio data
            audio_data = audio_buffer.read()
            
            if not audio_data:
                raise Exception("Failed to generate audio data")
            
            # Convert to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            logger.info(f"TTS base64 conversion successful - Audio size: {len(audio_data)} bytes, Time: {processing_time:.2f}ms")
            
            return {
                "audio_base64": audio_base64,
                "audio_format": "mp3",
                "text_length": len(text),
                "processing_time_ms": round(processing_time, 2),
                "voice_settings": self.voice_settings.copy(),
                "language": tts_lang,
                "success": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            error_msg = f"TTS base64 conversion failed: {e}"
            logger.error(f"{error_msg}, Time: {processing_time:.2f}ms")
            
            # For voice-guided meditation, TTS failure is critical
            raise Exception(f"Voice generation failed: {str(e)}. Voice-guided meditation requires working TTS.")
    
    def update_voice_settings(self, settings: Dict[str, Any]) -> bool:
        """Update voice settings for gTTS"""
        try:
            # Validate and update settings
            if 'lang' in settings:
                supported_langs = self.get_supported_languages()
                if settings['lang'] in supported_langs:
                    self.voice_settings['lang'] = settings['lang']
            
            if 'rate' in settings:
                # Map rate to gTTS slow parameter
                if settings['rate'] in ['slow', 'normal']:
                    self.voice_settings['rate'] = settings['rate']
            
            if 'tld' in settings:
                # Top-level domain for accent variation
                if settings['tld'] in ['com', 'co.uk', 'com.au', 'ca']:
                    self.voice_settings['tld'] = settings['tld']
            
            logger.info(f"Voice settings updated: {self.voice_settings}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating voice settings: {e}")
            return False
    
    def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available gTTS voices/languages"""
        try:
            supported_langs = self.get_supported_languages()
            voice_list = []
            
            # Create voice options based on supported languages
            for lang_code, lang_name in supported_langs.items():
                voice_info = {
                    "id": lang_code,
                    "name": f"gTTS {lang_name}",
                    "language": lang_code,
                    "gender": "neutral",  # gTTS doesn't specify gender
                    "accent_options": ["com", "co.uk", "com.au", "ca"] if lang_code == "en" else ["com"]
                }
                voice_list.append(voice_info)
            
            return {
                "voices": voice_list,
                "current_voice": self.voice_settings['lang'],
                "current_settings": self.voice_settings,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return {"voices": [], "error": str(e), "success": False}
    
    async def generate_meditation_audio_sequence(
        self,
        guidance_texts: Dict[str, str],
        timings: Dict[str, int],
        voice_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a sequence of audio clips for a complete meditation session
        
        Args:
            guidance_texts: Dict of phase -> text mappings
            timings: Dict of phase -> duration in seconds
            voice_settings: Optional voice configuration
            
        Returns:
            Dict containing audio sequence data
        """
        try:
            logger.info(f"Generating meditation audio sequence - Phases: {list(guidance_texts.keys())}")
            
            audio_sequence = {}
            total_processing_time = 0
            
            for phase, text in guidance_texts.items():
                if text:
                    result = await self.text_to_speech_base64(text, voice_settings)
                    
                    if result.get('success'):
                        audio_sequence[phase] = {
                            "audio_base64": result['audio_base64'],
                            "duration": timings.get(phase, 30),  # Default 30 seconds
                            "text": text,
                            "processing_time_ms": result['processing_time_ms']
                        }
                        total_processing_time += result['processing_time_ms']
                    else:
                        logger.error(f"Failed to generate audio for phase: {phase}")
                        audio_sequence[phase] = {
                            "error": result.get('error', 'Unknown error'),
                            "text": text
                        }
            
            return {
                "audio_sequence": audio_sequence,
                "total_phases": len(guidance_texts),
                "successful_phases": len([p for p in audio_sequence.values() if 'audio_base64' in p]),
                "total_processing_time_ms": total_processing_time,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error generating meditation audio sequence: {e}")
            return {
                "error": str(e),
                "success": False
            }

# Global TTS service instance
tts_service = TTSService()