"""
Ollama AI Service for Deep-Shiva API
Handles communication with Ollama for AI-powered chat responses
"""

import ollama
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from ..config import settings
from ..logging_config import get_logger, ErrorTracker, get_ai_response_logger, AIResponseLogger

logger = get_logger("ollama_service")
error_tracker = ErrorTracker(logger)
ai_response_logger = AIResponseLogger(get_ai_response_logger())

class OllamaService:
    """Service class for interacting with Ollama AI models"""
    
    def __init__(self):
        self.host = settings.ollama_host
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout
        self.temperature = settings.ollama_temperature
        self.max_tokens = settings.ollama_max_tokens
        
        # Initialize Ollama client
        self.client = ollama.Client(host=self.host)
        
        logger.info("Ollama service initialized", extra={
            "host": self.host,
            "model": self.model,
            "timeout": self.timeout
        })
    
    async def check_connection(self) -> bool:
        """Check if Ollama server is accessible"""
        try:
            # Test connection by listing models
            models = await asyncio.to_thread(self.client.list)
            logger.info("Ollama connection successful", extra={
                "available_models": len(models.get('models', []))
            })
            return True
        except Exception as e:
            logger.error("Ollama connection failed", extra={
                "host": self.host,
                "error": str(e)
            })
            return False
    
    async def check_model_availability(self) -> bool:
        """Check if the configured model is available"""
        try:
            models = await asyncio.to_thread(self.client.list)
            available_models = [model['name'] for model in models.get('models', [])]
            
            if self.model in available_models:
                logger.info("Model is available", extra={"model": self.model})
                return True
            else:
                logger.warning("Model not found", extra={
                    "requested_model": self.model,
                    "available_models": available_models
                })
                return False
        except Exception as e:
            error_tracker.log_external_api_error(e, "Ollama", "list_models")
            return False
    
    def _build_system_prompt(self, context: Optional[str] = None) -> str:
        """Build system prompt for Deep-Shiva tourism chatbot"""
        base_prompt = """You are Deep-Shiva, an AI assistant specialized in Uttarakhand tourism and spiritual guidance. You help visitors with:

1. Char Dham Yatra information (Kedarnath, Badrinath, Gangotri, Yamunotri)
2. Travel planning and routes
3. Weather conditions and best visit times
4. Local culture and traditions
5. Yoga and spiritual practices
6. Accommodation and transportation
7. Safety guidelines and emergency information

Guidelines:
- Be helpful, informative, and culturally sensitive
- Provide practical, actionable advice
- Include safety considerations when relevant
- Respect local customs and traditions
- Keep responses concise but comprehensive
- Use a warm, welcoming tone
- If you don't know something specific, suggest reliable sources

Current context: You are helping with Uttarakhand tourism and pilgrimage planning."""

        if context:
            base_prompt += f"\n\nAdditional context: {context}"
        
        return base_prompt
    
    async def generate_response(
        self,
        message: str,
        user_id: str,
        context: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Generate AI response using Ollama
        
        Args:
            message: User's message
            user_id: Unique user identifier
            context: Additional context for the query
            conversation_history: Previous conversation messages
            language: Preferred response language
            
        Returns:
            Dict containing response and metadata
        """
        start_time = datetime.now()
        
        try:
            logger.info("Generating AI response", extra={
                "user_id": user_id,
                "message_length": len(message),
                "has_context": bool(context),
                "has_history": bool(conversation_history),
                "language": language
            })
            
            # Also log COMPLETE user request to console
            print(f"\n{'='*80}")
            print(f"🤖 [AI REQUEST] User: {user_id}")
            print(f"{'='*80}")
            print(f"👤 User Message: {message}")
            print(f"🌐 Language: {language}")
            if context:
                print(f"📝 Context: {context}")
            print(f"{'='*80}")
            print(f"⏳ Processing with {self.model}...")
            
            # Build the prompt
            system_prompt = self._build_system_prompt(context)
            
            # Prepare conversation messages
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history if available
            if conversation_history:
                for msg in conversation_history[-5:]:  # Last 5 messages for context
                    messages.append({
                        "role": "user" if msg.get("role") == "user" else "assistant",
                        "content": msg.get("content", "")
                    })
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Add language instruction if not English
            if language != "en":
                language_instruction = {
                    "hi": "Please respond in Hindi (हिंदी में उत्तर दें).",
                    "ga": "Please respond in Garhwali if possible, otherwise Hindi."
                }.get(language, "Please respond in English.")
                
                messages.append({"role": "system", "content": language_instruction})
            
            # Generate response using Ollama
            response = await asyncio.to_thread(
                self.client.chat,
                model=self.model,
                messages=messages,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                }
            )
            
            # Extract response content
            ai_response = response.get('message', {}).get('content', '')
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Log successful response
            logger.info("AI response generated successfully", extra={
                "user_id": user_id,
                "response_length": len(ai_response),
                "processing_time_ms": round(processing_time, 2),
                "model": self.model
            })
            
            # Immediate console output for COMPLETE AI response
            print(f"\n{'='*80}")
            print(f"🧠 [AI RESPONSE] Model: {self.model} | Time: {processing_time:.1f}ms")
            print(f"{'='*80}")
            print(f"{ai_response}")
            print(f"{'='*80}\n")
            
            # Log detailed AI response for monitoring
            ai_response_logger.log_ai_response(
                user_id=user_id,
                message_id=f"ollama_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[:8]}",
                user_message=message,
                ai_response=ai_response,
                model_used=self.model,
                processing_time_ms=round(processing_time, 2),
                language=language,
                context=context,
                success=True
            )
            
            return {
                "response": ai_response,
                "model": self.model,
                "processing_time_ms": round(processing_time, 2),
                "timestamp": datetime.now().isoformat(),
                "success": True,
                "metadata": {
                    "temperature": self.temperature,
                    "max_tokens": self.max_tokens,
                    "message_count": len(messages)
                }
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            error_tracker.log_external_api_error(e, "Ollama", "chat_completion")
            
            logger.error("AI response generation failed", extra={
                "user_id": user_id,
                "error": str(e),
                "processing_time_ms": round(processing_time, 2)
            })
            
            # Generate fallback response
            fallback_response = self._get_fallback_response(message, language)
            
            # Immediate console output for error with COMPLETE fallback
            print(f"\n{'='*80}")
            print(f"❌ [AI ERROR] {str(e)}")
            print(f"{'='*80}")
            print(f"🔄 [FALLBACK RESPONSE]:")
            print(f"{fallback_response}")
            print(f"{'='*80}\n")
            
            # Log AI error and fallback usage
            ai_response_logger.log_ai_error(
                user_id=user_id,
                user_message=message,
                error_message=str(e),
                fallback_response=fallback_response,
                model_attempted=self.model
            )
            
            # Return fallback response
            return {
                "response": fallback_response,
                "model": "fallback",
                "processing_time_ms": round(processing_time, 2),
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e),
                "metadata": {
                    "fallback_used": True
                }
            }
    
    def _get_fallback_response(self, message: str, language: str = "en") -> str:
        """Generate fallback response when Ollama is unavailable"""
        
        fallback_responses = {
            "en": {
                "greeting": "Hello! I'm Deep-Shiva, your Uttarakhand tourism guide. I'm currently experiencing technical difficulties, but I'm here to help with basic information about the Char Dham yatra and Uttarakhand tourism.",
                "char_dham": "The Char Dham includes Kedarnath, Badrinath, Gangotri, and Yamunotri. These sacred sites are typically open from May to October. Would you like specific information about any of these shrines?",
                "weather": "Weather in Uttarakhand varies by altitude and season. The best time for pilgrimage is May-June and September-October. Always check current conditions before traveling.",
                "travel": "Travel to Char Dham involves road journeys from Rishikesh/Haridwar. Kedarnath requires a 16km trek from Gaurikund. Helicopter services are available during peak season.",
                "default": "I apologize, but I'm currently experiencing technical difficulties. For immediate assistance with Uttarakhand tourism, please contact local tourism offices or check official government tourism websites."
            },
            "hi": {
                "greeting": "नमस्ते! मैं दीप-शिव हूं, आपका उत्तराखंड पर्यटन गाइड। मुझे तकनीकी समस्या हो रही है, लेकिन मैं चार धाम यात्रा की बुनियादी जानकारी में आपकी मदद कर सकता हूं।",
                "char_dham": "चार धाम में केदारनाथ, बद्रीनाथ, गंगोत्री और यमुनोत्री शामिल हैं। ये पवित्र स्थान आमतौर पर मई से अक्टूबर तक खुले रहते हैं।",
                "weather": "उत्तराखंड में मौसम ऊंचाई और मौसम के अनुसार बदलता रहता है। तीर्थयात्रा के लिए सबसे अच्छा समय मई-जून और सितंबर-अक्टूबर है।",
                "travel": "चार धाम की यात्रा ऋषिकेश/हरिद्वार से सड़क मार्ग से होती है। केदारनाथ के लिए गौरीकुंड से 16 किमी की पैदल यात्रा करनी पड़ती है।",
                "default": "मुझे खेद है, लेकिन मुझे तकनीकी समस्या हो रही है। उत्तराखंड पर्यटन की तत्काल सहायता के लिए स्थानीय पर्यटन कार्यालयों से संपर्क करें।"
            }
        }
        
        responses = fallback_responses.get(language, fallback_responses["en"])
        
        # Simple keyword matching for fallback
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["hello", "hi", "namaste", "नमस्ते"]):
            return responses["greeting"]
        elif any(word in message_lower for word in ["char dham", "kedarnath", "badrinath", "चार धाम"]):
            return responses["char_dham"]
        elif any(word in message_lower for word in ["weather", "temperature", "मौसम"]):
            return responses["weather"]
        elif any(word in message_lower for word in ["travel", "route", "यात्रा"]):
            return responses["travel"]
        else:
            return responses["default"]
    
    async def pull_model(self, model_name: Optional[str] = None) -> bool:
        """Pull/download a model from Ollama registry"""
        model = model_name or self.model
        
        try:
            logger.info("Pulling Ollama model", extra={"model": model})
            
            await asyncio.to_thread(self.client.pull, model)
            
            logger.info("Model pulled successfully", extra={"model": model})
            return True
            
        except Exception as e:
            error_tracker.log_external_api_error(e, "Ollama", "pull_model")
            return False
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        try:
            models = await asyncio.to_thread(self.client.list)
            
            for model in models.get('models', []):
                if model['name'] == self.model:
                    return {
                        "name": model['name'],
                        "size": model.get('size', 0),
                        "modified_at": model.get('modified_at', ''),
                        "available": True
                    }
            
            return {
                "name": self.model,
                "available": False,
                "error": "Model not found"
            }
            
        except Exception as e:
            error_tracker.log_external_api_error(e, "Ollama", "model_info")
            return {
                "name": self.model,
                "available": False,
                "error": str(e)
            }

# Global service instance
ollama_service = OllamaService()