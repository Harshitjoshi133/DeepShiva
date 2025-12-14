"""
Yoga Pose Analysis Router
Handles yoga pose analysis using Gemma AI model through Ollama
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
import base64
import io
import time
import json
from typing import List, Optional, Dict, Any
from PIL import Image
import asyncio

from ..services.ollama_service import ollama_service
from ..logging_config import get_logger, ErrorTracker, PerformanceLogger

router = APIRouter()
logger = get_logger("yoga")
error_tracker = ErrorTracker(logger)
performance_logger = PerformanceLogger(logger)

class YogaPoseRequest(BaseModel):
    image: str = Field(..., description="Base64 encoded image")
    pose_type: Optional[str] = Field("auto", description="Expected pose type or 'auto' for detection")

class YogaPoseResponse(BaseModel):
    status: str
    feedback: str
    confidence: float
    detected_pose: str
    corrections: List[str]
    pose_score: int
    body_parts_detected: List[str]
    recommendations: List[str]

class PoseGuide(BaseModel):
    pose_name: str
    description: str
    benefits: List[str]
    difficulty_level: str
    duration_seconds: int
    key_points: List[str]
    common_mistakes: List[str]

def validate_image(base64_image: str) -> tuple[bool, str, Optional[Image.Image]]:
    """
    Validate and decode base64 image
    Returns: (is_valid, error_message, pil_image)
    """
    try:
        # Decode base64 image
        image_data = base64.b64decode(base64_image)
        
        # Check minimum size
        if len(image_data) < 1000:
            return False, "Image too small or corrupted", None
        
        # Check maximum size (10MB)
        if len(image_data) > 10 * 1024 * 1024:
            return False, "Image too large (max 10MB)", None
        
        # Try to open with PIL
        image = Image.open(io.BytesIO(image_data))
        
        # Validate image format
        if image.format not in ['JPEG', 'PNG', 'GIF', 'WEBP']:
            return False, f"Unsupported image format: {image.format}", None
        
        # Check image dimensions
        width, height = image.size
        if width < 100 or height < 100:
            return False, "Image resolution too low (minimum 100x100)", None
        
        return True, "", image
        
    except Exception as e:
        return False, f"Invalid image data: {str(e)}", None

def build_yoga_analysis_prompt(pose_type: str = "auto") -> str:
    """Build the system prompt for yoga pose analysis"""
    
    prompt = """You are an expert yoga instructor and pose analyst. Analyze the yoga pose in the provided image and provide detailed feedback.

Your analysis should include:

1. **Pose Identification**: Identify the yoga pose being performed
2. **Alignment Assessment**: Evaluate the alignment of body parts
3. **Form Analysis**: Check if the pose is performed correctly
4. **Specific Feedback**: Provide constructive feedback and corrections
5. **Safety Considerations**: Note any safety concerns

**Response Format** (JSON only):
{
    "detected_pose": "Name of the yoga pose",
    "status": "Perfect|Good|Needs Improvement|Incorrect|Unsafe",
    "confidence": 0.85,
    "pose_score": 85,
    "feedback": "Detailed feedback about the pose performance",
    "corrections": ["Specific correction 1", "Specific correction 2"],
    "body_parts_detected": ["head", "shoulders", "arms", "torso", "legs"],
    "recommendations": ["Hold for 30 seconds", "Focus on breathing", "Practice daily"]
}

**Scoring Guidelines**:
- Perfect (90-100): Excellent alignment, proper form
- Good (75-89): Minor adjustments needed
- Needs Improvement (60-74): Several corrections required
- Incorrect (40-59): Major form issues
- Unsafe (0-39): Risk of injury, stop immediately

**Common Yoga Poses to Recognize**:
- Mountain Pose (Tadasana)
- Tree Pose (Vrksasana)
- Warrior I, II, III (Virabhadrasana)
- Downward Facing Dog (Adho Mukha Svanasana)
- Chair Pose (Utkatasana)
- Triangle Pose (Trikonasana)
- Child's Pose (Balasana)
- Cobra Pose (Bhujangasana)
- Plank Pose
- Bridge Pose (Setu Bandhasana)

**Key Assessment Points**:
- Spine alignment
- Joint positioning (knees, ankles, wrists)
- Weight distribution
- Muscle engagement
- Balance and stability
- Breathing space (chest open)
- Safety of the pose

Provide encouraging but honest feedback. Focus on improvement rather than criticism."""

    if pose_type != "auto":
        prompt += f"\n\nThe user expects this to be a {pose_type} pose. Analyze specifically for this pose."

    return prompt

async def analyze_pose_with_vision_model(base64_image: str, pose_type: str = "auto") -> Dict[str, Any]:
    """
    Analyze yoga pose using vision model (LLaVA) through Ollama
    """
    try:
        # Build the analysis prompt for vision model
        vision_prompt = f"""You are an expert yoga instructor analyzing a yoga pose image. 

Analyze this image and provide detailed feedback about the yoga pose being performed.

Instructions:
1. Identify the yoga pose being performed
2. Evaluate the alignment and form
3. Provide specific corrections if needed
4. Give a score from 0-100
5. Offer helpful recommendations

Expected pose type: {pose_type if pose_type != "auto" else "any yoga pose"}

Please respond in this JSON format:
{{
    "detected_pose": "Name of the yoga pose",
    "status": "Perfect|Good|Needs Improvement|Incorrect|Unsafe",
    "confidence": 0.85,
    "pose_score": 85,
    "feedback": "Detailed feedback about the pose performance",
    "corrections": ["Specific correction 1", "Specific correction 2"],
    "body_parts_detected": ["head", "shoulders", "arms", "torso", "legs"],
    "recommendations": ["Hold for 30 seconds", "Focus on breathing", "Practice daily"]
}}

Focus on:
- Spine alignment and posture
- Joint positioning (knees, ankles, wrists)
- Weight distribution and balance
- Muscle engagement
- Safety considerations
- Breathing space (open chest)

Provide encouraging but honest feedback focused on improvement."""

        # Check if vision model is available
        vision_model = "llava:latest"  # Default vision model
        is_vision_available = await ollama_service.check_vision_model_availability(vision_model)
        
        if not is_vision_available:
            # Try alternative vision models
            alternative_models = ["llava:7b", "llava:13b", "bakllava:latest"]
            for alt_model in alternative_models:
                if await ollama_service.check_vision_model_availability(alt_model):
                    vision_model = alt_model
                    is_vision_available = True
                    break
        
        if is_vision_available:
            # Use vision model to analyze the actual image
            logger.info(f"Using vision model for analysis: {vision_model}")
            
            response = await ollama_service.analyze_image_with_vision_model(
                base64_image=base64_image,
                prompt=vision_prompt,
                user_id="yoga_analyzer",
                vision_model=vision_model
            )
            
            if response.get("success", False):
                ai_response = response.get("response", "")
                
                # Try to extract JSON from the response
                try:
                    # Look for JSON in the response
                    start_idx = ai_response.find('{')
                    end_idx = ai_response.rfind('}') + 1
                    
                    if start_idx != -1 and end_idx > start_idx:
                        json_str = ai_response[start_idx:end_idx]
                        analysis_result = json.loads(json_str)
                        
                        # Validate and clean the result
                        analysis_result = validate_and_clean_analysis_result(analysis_result)
                        
                        logger.info(f"Vision model analysis successful - Pose: {analysis_result.get('detected_pose', 'Unknown')}, Score: {analysis_result.get('pose_score', 0)}")
                        return analysis_result
                    else:
                        raise ValueError("No valid JSON found in vision model response")
                        
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning(f"Failed to parse vision model response as JSON: {e}")
                    
                    # Create structured response from vision model text
                    return create_fallback_analysis(ai_response, pose_type, is_vision_analysis=True)
            else:
                raise Exception(f"Vision model error: {response.get('error', 'Unknown error')}")
        else:
            # No vision model available - return clear error message
            logger.error("No vision model available for image analysis")
            
            # Get list of available models for better error message
            try:
                models_response = await asyncio.to_thread(ollama_service.client.list)
                available_models = ollama_service._extract_model_names(models_response)
                available_models_str = ", ".join(available_models) if available_models else "None"
            except Exception:
                available_models_str = "Unable to retrieve model list"
            
            raise Exception(f"Vision model not found. Image analysis requires a vision model like LLaVA. Available models: {available_models_str}. Please install a vision model using: ollama pull llava:latest")
    
    except Exception as e:
        logger.error(f"Vision model analysis failed: {e}")
        raise

def validate_and_clean_analysis_result(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean the analysis result from AI model"""
    
    # Ensure required fields exist
    required_fields = {
        "detected_pose": "Unknown Pose",
        "status": "Good",
        "confidence": 0.75,
        "pose_score": 75,
        "feedback": "Pose analysis completed."
    }
    
    for field, default_value in required_fields.items():
        if field not in analysis_result:
            analysis_result[field] = default_value
    
    # Ensure lists exist
    analysis_result.setdefault("corrections", [])
    analysis_result.setdefault("body_parts_detected", ["head", "torso", "arms", "legs"])
    analysis_result.setdefault("recommendations", ["Practice regularly", "Focus on breathing"])
    
    # Validate and clamp numeric values
    try:
        analysis_result["confidence"] = max(0.0, min(1.0, float(analysis_result["confidence"])))
    except (ValueError, TypeError):
        analysis_result["confidence"] = 0.75
    
    try:
        analysis_result["pose_score"] = max(0, min(100, int(analysis_result["pose_score"])))
    except (ValueError, TypeError):
        analysis_result["pose_score"] = 75
    
    # Ensure lists are actually lists and limit their length
    if not isinstance(analysis_result["corrections"], list):
        analysis_result["corrections"] = []
    analysis_result["corrections"] = analysis_result["corrections"][:5]  # Max 5 corrections
    
    if not isinstance(analysis_result["body_parts_detected"], list):
        analysis_result["body_parts_detected"] = ["head", "torso", "arms", "legs"]
    
    if not isinstance(analysis_result["recommendations"], list):
        analysis_result["recommendations"] = ["Practice regularly", "Focus on breathing"]
    analysis_result["recommendations"] = analysis_result["recommendations"][:4]  # Max 4 recommendations
    
    return analysis_result

def create_static_fallback_analysis(pose_type: str) -> Dict[str, Any]:
    """Create a static fallback analysis when AI services are unavailable"""
    
    # Determine pose name
    detected_pose = pose_type if pose_type != "auto" else "Yoga Pose"
    
    # Create encouraging general feedback
    feedback_templates = {
        "Tree Pose": "Tree Pose is excellent for balance and focus. Remember to keep your standing leg strong and find a focal point to help with stability.",
        "Mountain Pose": "Mountain Pose is the foundation of all standing poses. Focus on grounding through your feet and lengthening through the crown of your head.",
        "Warrior I": "Warrior I builds strength and confidence. Keep your front knee aligned over your ankle and square your hips toward the front.",
        "Downward Dog": "Downward Dog is a wonderful full-body stretch. Press firmly through your hands and lift your hips up and back.",
        "Chair Pose": "Chair Pose strengthens your legs and core. Sit back as if sitting in an invisible chair and keep your weight on your heels."
    }
    
    feedback = feedback_templates.get(detected_pose, 
        f"Great work practicing {detected_pose}! Focus on proper alignment, steady breathing, and listening to your body.")
    
    return {
        "detected_pose": detected_pose,
        "status": "Good",
        "confidence": 0.5,  # Lower confidence for static analysis
        "pose_score": 70,   # Moderate score
        "feedback": feedback,
        "corrections": [
            "Focus on proper alignment",
            "Breathe deeply and steadily", 
            "Engage your core muscles",
            "Hold the pose with stability"
        ],
        "body_parts_detected": ["head", "shoulders", "arms", "torso", "legs"],
        "recommendations": [
            "Practice regularly to improve",
            "Listen to your body's limits",
            "Focus on quality over quantity",
            "Consider taking a yoga class"
        ]
    }

def create_fallback_analysis(ai_response: str, pose_type: str, is_vision_analysis: bool = False) -> Dict[str, Any]:
    """Create a structured analysis from unstructured AI response"""
    
    # Extract pose name if mentioned
    detected_pose = "Unknown Pose"
    if pose_type != "auto":
        detected_pose = pose_type
    else:
        # Try to find pose names in the response
        common_poses = [
            "Mountain Pose", "Tree Pose", "Warrior", "Downward Dog", 
            "Chair Pose", "Triangle", "Child's Pose", "Cobra", "Plank"
        ]
        for pose in common_poses:
            if pose.lower() in ai_response.lower():
                detected_pose = pose
                break
    
    # Determine status based on keywords
    status = "Good"
    confidence = 0.75
    pose_score = 75
    
    if any(word in ai_response.lower() for word in ["excellent", "perfect", "great"]):
        status = "Perfect"
        confidence = 0.9
        pose_score = 90
    elif any(word in ai_response.lower() for word in ["needs", "improve", "adjust"]):
        status = "Needs Improvement"
        confidence = 0.7
        pose_score = 65
    elif any(word in ai_response.lower() for word in ["incorrect", "wrong", "unsafe"]):
        status = "Incorrect"
        confidence = 0.6
        pose_score = 45
    
    # Extract corrections (look for bullet points or numbered lists)
    corrections = []
    lines = ai_response.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('-') or line.startswith('•') or any(line.startswith(f"{i}.") for i in range(1, 10)):
            correction = line.lstrip('-•0123456789. ').strip()
            if correction and len(correction) > 10:
                corrections.append(correction)
    
    if not corrections:
        corrections = ["Focus on proper alignment", "Engage core muscles", "Breathe steadily"]
    
    # Adjust confidence based on analysis type
    if not is_vision_analysis:
        confidence = max(0.3, confidence - 0.2)  # Lower confidence for non-vision analysis
        pose_score = max(50, pose_score - 10)  # Lower score for non-vision analysis
    
    return {
        "detected_pose": detected_pose,
        "status": status,
        "confidence": confidence,
        "pose_score": pose_score,
        "feedback": ai_response[:500] + "..." if len(ai_response) > 500 else ai_response,
        "corrections": corrections[:5],  # Limit to 5 corrections
        "body_parts_detected": ["head", "shoulders", "arms", "torso", "legs"],
        "recommendations": [
            "Hold the pose for 30-60 seconds",
            "Focus on steady breathing",
            "Practice regularly for improvement",
            "Listen to your body"
        ]
    }

@router.post("/analyze", response_model=YogaPoseResponse)
async def analyze_yoga_pose(request: YogaPoseRequest, http_request: Request):
    """
    Analyze yoga pose using Gemma AI model
    """
    start_time = time.time()
    request_id = getattr(http_request.state, 'request_id', 'unknown')
    
    logger.info("Yoga pose analysis request received", extra={
        "request_id": request_id,
        "pose_type": request.pose_type,
        "image_size_bytes": len(request.image)
    })
    
    try:
        # Validate image
        is_valid, error_msg, pil_image = validate_image(request.image)
        if not is_valid:
            logger.warning(f"Image validation failed: {error_msg}", extra={"request_id": request_id})
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info("Image validation successful", extra={
            "request_id": request_id,
            "image_format": pil_image.format,
            "image_size": pil_image.size
        })
        
        # Check Ollama service availability
        ollama_available = False
        try:
            ollama_available = await ollama_service.check_connection()
        except Exception as e:
            logger.warning(f"Ollama connection check failed: {e}", extra={"request_id": request_id})
        
        if not ollama_available:
            logger.warning("Ollama service unavailable, using static fallback", extra={"request_id": request_id})
            
            # Return a static fallback response when Ollama is completely unavailable
            static_fallback = create_static_fallback_analysis(request.pose_type)
            
            processing_time = (time.time() - start_time) * 1000
            logger.info("Static fallback analysis completed", extra={
                "request_id": request_id,
                "processing_time_ms": round(processing_time, 2),
                "fallback_type": "static"
            })
            
            return YogaPoseResponse(**static_fallback)
        
        # Analyze pose with vision model (send actual image)
        analysis_result = await analyze_pose_with_vision_model(
            base64_image=request.image,
            pose_type=request.pose_type
        )
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000
        
        logger.info("Yoga pose analysis completed", extra={
            "request_id": request_id,
            "detected_pose": analysis_result["detected_pose"],
            "pose_score": analysis_result["pose_score"],
            "confidence": analysis_result["confidence"],
            "processing_time_ms": round(processing_time, 2)
        })
        
        # Log performance metrics
        performance_logger.log_api_performance(
            endpoint="/api/v1/yoga/analyze",
            method="POST",
            duration_ms=processing_time,
            status_code=200
        )
        
        return YogaPoseResponse(**analysis_result)
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = (time.time() - start_time) * 1000
        
        error_tracker.log_validation_error(e, {
            "request_id": request_id,
            "pose_type": request.pose_type,
            "processing_time_ms": round(processing_time, 2)
        })
        
        logger.error(f"Yoga pose analysis failed: {str(e)}", extra={
            "request_id": request_id,
            "error": str(e)
        })
        
        # Check if this is a vision model error
        error_message = str(e)
        if "vision model not found" in error_message.lower() or "llava" in error_message.lower():
            # Vision model specific error
            fallback_response = {
                "status": "Vision Model Not Found",
                "feedback": "Image analysis requires a vision model (LLaVA) to be installed. The system cannot analyze images without a vision-capable AI model.",
                "confidence": 0.0,
                "detected_pose": "Unknown",
                "corrections": [
                    "Install a vision model: ollama pull llava:latest",
                    "Restart the Ollama service after installation",
                    "Verify the model is available: ollama list",
                    "Contact system administrator if needed"
                ],
                "pose_score": 0,
                "body_parts_detected": [],
                "recommendations": [
                    "Install LLaVA vision model for image analysis",
                    "Use text-based yoga guidance in the meantime",
                    "Check system requirements for vision models",
                    "Contact support for installation help"
                ]
            }
        else:
            # General error fallback
            fallback_response = {
                "status": "Error",
                "feedback": "Unable to analyze pose at the moment. Please ensure good lighting and try again.",
                "confidence": 0.0,
                "detected_pose": "Unknown",
                "corrections": [
                    "Ensure good lighting in the image",
                    "Make sure your full body is visible",
                    "Try taking the photo from a different angle",
                    "Check your internet connection"
                ],
                "pose_score": 0,
                "body_parts_detected": [],
                "recommendations": [
                    "Try again with better lighting",
                    "Ensure stable internet connection",
                    "Contact support if the issue persists"
                ]
            }
        
        return YogaPoseResponse(**fallback_response)

# Include the existing pose guides and session endpoints from vision.py
@router.get("/poses", response_model=List[PoseGuide])
async def get_yoga_poses():
    """Get list of supported yoga poses with detailed guides"""
    
    yoga_poses = [
        {
            "pose_name": "Mountain Pose (Tadasana)",
            "description": "A foundational standing pose that improves posture and balance",
            "benefits": [
                "Improves posture and balance",
                "Strengthens legs and core",
                "Increases awareness of body alignment",
                "Calms the mind and reduces stress"
            ],
            "difficulty_level": "Beginner",
            "duration_seconds": 60,
            "key_points": [
                "Stand tall with feet hip-width apart",
                "Distribute weight evenly on both feet",
                "Engage leg muscles and lift kneecaps",
                "Lengthen spine and relax shoulders",
                "Arms at sides, palms facing forward"
            ],
            "common_mistakes": [
                "Locking knees too rigidly",
                "Tilting pelvis forward or back",
                "Tensing shoulders",
                "Holding breath"
            ]
        },
        {
            "pose_name": "Tree Pose (Vrksasana)",
            "description": "A balancing pose that improves focus and strengthens legs",
            "benefits": [
                "Improves balance and coordination",
                "Strengthens standing leg",
                "Opens hips and groin",
                "Enhances concentration and focus"
            ],
            "difficulty_level": "Beginner",
            "duration_seconds": 30,
            "key_points": [
                "Stand on left leg, bend right knee",
                "Place right foot on inner left thigh",
                "Avoid placing foot on side of knee",
                "Hands in prayer at heart or overhead",
                "Find a focal point (drishti)"
            ],
            "common_mistakes": [
                "Placing foot on side of knee",
                "Collapsing into standing hip",
                "Looking around instead of focusing",
                "Tensing the body"
            ]
        },
        {
            "pose_name": "Warrior I (Virabhadrasana I)",
            "description": "A powerful standing pose that builds strength and stability",
            "benefits": [
                "Strengthens legs, arms, and back",
                "Improves balance and stability",
                "Opens hips and chest",
                "Builds confidence and focus"
            ],
            "difficulty_level": "Intermediate",
            "duration_seconds": 45,
            "key_points": [
                "Step left foot back 3-4 feet",
                "Turn left foot out 45-60 degrees",
                "Bend right knee over ankle",
                "Square hips toward front",
                "Reach arms overhead"
            ],
            "common_mistakes": [
                "Front knee extending past ankle",
                "Back leg not straight",
                "Hips not squared forward",
                "Leaning forward too much"
            ]
        },
        {
            "pose_name": "Downward Facing Dog (Adho Mukha Svanasana)",
            "description": "An inversion that stretches and strengthens the entire body",
            "benefits": [
                "Stretches hamstrings and calves",
                "Strengthens arms and shoulders",
                "Improves circulation",
                "Calms the nervous system"
            ],
            "difficulty_level": "Beginner",
            "duration_seconds": 60,
            "key_points": [
                "Start on hands and knees",
                "Tuck toes under, lift hips up",
                "Straighten legs as much as possible",
                "Press hands firmly into ground",
                "Create inverted V shape"
            ],
            "common_mistakes": [
                "Placing too much weight on hands",
                "Rounding the back",
                "Turning feet outward",
                "Holding breath"
            ]
        },
        {
            "pose_name": "Chair Pose (Utkatasana)",
            "description": "A strengthening pose that builds power in the legs and core",
            "benefits": [
                "Strengthens quadriceps and glutes",
                "Improves balance and stability",
                "Builds heat in the body",
                "Develops mental determination"
            ],
            "difficulty_level": "Intermediate",
            "duration_seconds": 30,
            "key_points": [
                "Stand with feet hip-width apart",
                "Bend knees and sit back like sitting in chair",
                "Keep weight on heels",
                "Reach arms overhead",
                "Keep chest lifted"
            ],
            "common_mistakes": [
                "Knees extending past toes",
                "Weight on toes instead of heels",
                "Rounding the back",
                "Holding breath"
            ]
        }
    ]
    
    return [PoseGuide(**pose) for pose in yoga_poses]

@router.get("/poses/{pose_name}", response_model=PoseGuide)
async def get_pose_guide(pose_name: str):
    """Get detailed guide for a specific yoga pose"""
    
    poses = await get_yoga_poses()
    
    for pose in poses:
        if pose_name.lower().replace("-", " ") in pose.pose_name.lower():
            return pose
    
    raise HTTPException(status_code=404, detail=f"Pose guide for '{pose_name}' not found")