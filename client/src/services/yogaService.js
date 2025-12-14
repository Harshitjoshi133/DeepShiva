/**
 * Yoga Pose Analysis API Service
 * Handles communication with the backend for yoga pose analysis
 */

const API_BASE_URL = '/api/v1/yoga'

class YogaService {
  /**
   * Analyze a yoga pose from an image
   * @param {string} base64Image - Base64 encoded image data
   * @param {string} poseType - Expected pose type or 'auto' for detection
   * @returns {Promise<Object>} Analysis result
   */
  async analyzePose(base64Image, poseType = 'auto') {
    try {
      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: base64Image,
          pose_type: poseType
        })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      const result = await response.json()
      
      // Log successful analysis
      console.log('Yoga pose analysis completed:', {
        pose: result.detected_pose,
        score: result.pose_score,
        confidence: result.confidence
      })

      return result
    } catch (error) {
      console.error('Yoga pose analysis failed:', error)
      
      // Check if this is a vision model error
      const errorMessage = error.message.toLowerCase()
      const isVisionModelError = errorMessage.includes('vision model not found') || 
                                errorMessage.includes('llava') ||
                                errorMessage.includes('vision model')
      
      if (isVisionModelError) {
        // Return specific vision model error response
        return {
          status: 'Vision Model Not Found',
          feedback: 'Image analysis requires a vision model (LLaVA) to be installed. The system cannot analyze yoga poses from images without a vision-capable AI model.',
          confidence: 0,
          detected_pose: 'Unknown',
          corrections: [
            'Vision model (LLaVA) needs to be installed on the server',
            'Contact system administrator to install: ollama pull llava:latest',
            'Restart the AI service after installation',
            'Verify model availability with system admin'
          ],
          pose_score: 0,
          body_parts_detected: [],
          recommendations: [
            'Ask administrator to install LLaVA vision model',
            'Use text-based yoga guidance in the meantime',
            'Try again after vision model is installed',
            'Contact support for technical assistance'
          ],
          error: error.message,
          errorType: 'VISION_MODEL_NOT_FOUND'
        }
      }
      
      // Return general error fallback response
      return {
        status: 'Error',
        feedback: 'Unable to analyze pose at the moment. Please check your connection and try again.',
        confidence: 0,
        detected_pose: 'Unknown',
        corrections: ['Please try again with better lighting', 'Ensure your full body is visible in the frame'],
        pose_score: 0,
        body_parts_detected: [],
        recommendations: ['Try again later', 'Check your internet connection'],
        error: error.message,
        errorType: 'GENERAL_ERROR'
      }
    }
  }

  /**
   * Get list of supported yoga poses
   * @returns {Promise<Array>} List of yoga poses with guides
   */
  async getYogaPoses() {
    try {
      const response = await fetch(`${API_BASE_URL}/poses`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to fetch yoga poses:', error)
      return []
    }
  }

  /**
   * Get detailed guide for a specific pose
   * @param {string} poseName - Name of the pose
   * @returns {Promise<Object>} Pose guide details
   */
  async getPoseGuide(poseName) {
    try {
      const response = await fetch(`${API_BASE_URL}/poses/${encodeURIComponent(poseName)}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        }
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to fetch pose guide:', error)
      return null
    }
  }

  /**
   * Start a guided yoga session
   * @param {Object} sessionConfig - Session configuration
   * @returns {Promise<Object>} Session details
   */
  async startYogaSession(sessionConfig) {
    try {
      const response = await fetch(`${API_BASE_URL}/session/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sessionConfig)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to start yoga session:', error)
      return null
    }
  }

  /**
   * Submit feedback about a pose
   * @param {Object} feedback - Feedback data
   * @returns {Promise<Object>} Submission result
   */
  async submitPoseFeedback(feedback) {
    try {
      const response = await fetch(`${API_BASE_URL}/feedback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedback)
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Failed to submit feedback:', error)
      return { success: false, error: error.message }
    }
  }

  /**
   * Convert image file to base64
   * @param {File} file - Image file
   * @returns {Promise<string>} Base64 encoded image
   */
  async fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        // Remove the data URL prefix (data:image/jpeg;base64,)
        const base64 = reader.result.split(',')[1]
        resolve(base64)
      }
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }

  /**
   * Validate image before analysis
   * @param {File} file - Image file
   * @returns {Object} Validation result
   */
  validateImage(file) {
    const maxSize = 10 * 1024 * 1024 // 10MB
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']

    if (!file) {
      return { valid: false, error: 'No file provided' }
    }

    if (file.size > maxSize) {
      return { valid: false, error: 'Image size must be less than 10MB' }
    }

    if (!allowedTypes.includes(file.type)) {
      return { valid: false, error: 'Invalid file type. Please use JPEG, PNG, GIF, or WebP' }
    }

    return { valid: true }
  }

  /**
   * Process image for analysis (resize if needed)
   * @param {string} base64Image - Base64 encoded image
   * @param {number} maxWidth - Maximum width for resizing
   * @returns {Promise<string>} Processed base64 image
   */
  async processImageForAnalysis(base64Image, maxWidth = 1024) {
    return new Promise((resolve) => {
      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        const ctx = canvas.getContext('2d')

        // Calculate new dimensions
        let { width, height } = img
        if (width > maxWidth) {
          height = (height * maxWidth) / width
          width = maxWidth
        }

        canvas.width = width
        canvas.height = height

        // Draw and compress
        ctx.drawImage(img, 0, 0, width, height)
        const processedImage = canvas.toDataURL('image/jpeg', 0.8).split(',')[1]
        resolve(processedImage)
      }
      img.src = `data:image/jpeg;base64,${base64Image}`
    })
  }
}

// Export singleton instance
export default new YogaService()