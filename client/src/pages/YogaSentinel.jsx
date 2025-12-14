import { useState, useRef } from 'react'
import Webcam from 'react-webcam'
import { Camera, Loader2, CheckCircle, AlertTriangle, Upload, X, Check } from 'lucide-react'
import { motion } from 'framer-motion'
import { useLanguage } from '../contexts/LanguageContext'
import yogaService from '../services/yogaService'
import '../styles/YogaSentinel.css'

export default function YogaSentinel() {
  const { t } = useLanguage()
  const webcamRef = useRef(null)
  const fileInputRef = useRef(null)
  const [mode, setMode] = useState('camera') // 'camera' or 'upload'
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [feedback, setFeedback] = useState(null)
  const [cameraError, setCameraError] = useState(false)
  const [capturedImage, setCapturedImage] = useState(null)
  const [uploadedImage, setUploadedImage] = useState(null)


  const captureImage = () => {
    if (!webcamRef.current) return
    
    const imageSrc = webcamRef.current.getScreenshot()
    setCapturedImage(imageSrc)
    setFeedback(null) // Clear previous feedback
  }

  const analyzeImage = async (imageData) => {
    setIsAnalyzing(true)
    setFeedback(null)

    try {
      // Extract base64 image data
      const base64Image = imageData.split(',')[1]
      
      // Use the yoga service for analysis
      const result = await yogaService.analyzePose(base64Image, 'auto')
      
      // Set the feedback with the analysis result
      setFeedback(result)
      
      // Log successful analysis
      console.log('Yoga pose analysis completed:', {
        pose: result.detected_pose,
        status: result.status,
        score: result.pose_score
      })
      
    } catch (error) {
      console.error('Yoga pose analysis failed:', error)
      
      // Set error feedback
      setFeedback({
        status: 'Error',
        feedback: 'Failed to analyze pose. Please check your connection and try again.',
        confidence: 0,
        detected_pose: 'Unknown',
        corrections: ['Check your internet connection', 'Ensure good lighting', 'Try again'],
        pose_score: 0,
        body_parts_detected: [],
        recommendations: ['Try again later', 'Check network connection']
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleImageUpload = (event) => {
    const file = event.target.files[0]
    
    if (!file) return
    
    // Validate the image file
    const validation = yogaService.validateImage(file)
    if (!validation.valid) {
      alert(validation.error)
      return
    }
    
    // Read and set the uploaded image
    const reader = new FileReader()
    reader.onload = (e) => {
      setUploadedImage(e.target.result)
      setFeedback(null) // Clear previous feedback
    }
    reader.onerror = () => {
      alert('Failed to read the image file. Please try again.')
    }
    reader.readAsDataURL(file)
  }

  const confirmAndAnalyze = () => {
    const imageToAnalyze = capturedImage || uploadedImage
    if (imageToAnalyze) {
      analyzeImage(imageToAnalyze)
    }
  }

  const retakeImage = () => {
    setCapturedImage(null)
    setFeedback(null)
  }

  const reselectImage = () => {
    setUploadedImage(null)
    setFeedback(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  const handleUserMediaError = () => {
    setCameraError(true)
  }

  const handleModeChange = (newMode) => {
    // Clear all images and feedback when switching modes
    setCapturedImage(null)
    setUploadedImage(null)
    setFeedback(null)
    setIsAnalyzing(false)
    
    // Clear file input if switching away from upload mode
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
    
    setMode(newMode)
  }

  return (
    <div className="yoga-container">
      <div className="yoga-card">
        <h2 className="yoga-title">{t('yoga.title', 'Yoga Sentinel')}</h2>
        <p className="yoga-description">
          {t('yoga.description', 'Choose your preferred method to analyze your yoga pose and get real-time feedback.')}
        </p>

        {/* Mode Selection */}
        <div className="mode-selector">
          <button
            onClick={() => handleModeChange('camera')}
            className={`mode-button ${mode === 'camera' ? 'active' : 'inactive'}`}
          >
            <Camera size={16} />
            {t('yoga.analyzeMode', 'Analyze Pose')}
          </button>
          <button
            onClick={() => handleModeChange('upload')}
            className={`mode-button ${mode === 'upload' ? 'active' : 'inactive'}`}
          >
            <Upload size={16} />
            {t('yoga.uploadMode', 'Upload Image')}
          </button>
        </div>

        <div className="yoga-grid">
          {/* Camera/Upload Area */}
          <div className="camera-container">
            {/* Show captured image only in camera mode */}
            {mode === 'camera' && capturedImage ? (
              <div className="captured-image-container">
                <img
                  src={capturedImage}
                  alt="Captured pose"
                  className="image-preview"
                />
                <div className="image-overlay">
                  <p className="image-overlay-text">{t('yoga.capturedImage', 'Captured Image')}</p>
                </div>
              </div>
            ) : mode === 'upload' && uploadedImage ? (
              <div className="captured-image-container">
                <img
                  src={uploadedImage}
                  alt="Uploaded pose"
                  className="image-preview"
                />
                <div className="image-overlay">
                  <p className="image-overlay-text">{t('yoga.uploadedImage', 'Uploaded Image')}</p>
                </div>
              </div>
            ) : mode === 'camera' ? (
              cameraError ? (
                <div className="camera-error">
                  <AlertTriangle size={40} className="camera-error-icon" />
                  <h3 className="camera-error-title">{t('yoga.cameraRequired', 'Camera Access Required')}</h3>
                  <p className="camera-error-message">
                    {t('yoga.cameraMessage', 'Please allow camera access in your browser settings to use Yoga Sentinel.')}
                  </p>
                </div>
              ) : (
                <>
                  <Webcam
                    ref={webcamRef}
                    audio={false}
                    screenshotFormat="image/jpeg"
                    className="webcam"
                    onUserMediaError={handleUserMediaError}
                  />
                  
                  {/* Skeleton Overlay Guide */}
                  <svg className="skeleton-overlay">
                    <circle cx="50%" cy="20%" r="30" />
                    <line x1="50%" y1="25%" x2="50%" y2="45%" />
                    <line x1="50%" y1="35%" x2="35%" y2="50%" />
                    <line x1="50%" y1="35%" x2="65%" y2="50%" />
                    <line x1="50%" y1="45%" x2="40%" y2="70%" />
                    <line x1="50%" y1="45%" x2="60%" y2="70%" />
                  </svg>
                </>
              )
            ) : (
              <div 
                className="upload-area"
                onClick={() => fileInputRef.current?.click()}
                onDragOver={(e) => {
                  e.preventDefault()
                  e.currentTarget.classList.add('dragover')
                }}
                onDragLeave={(e) => {
                  e.currentTarget.classList.remove('dragover')
                }}
                onDrop={(e) => {
                  e.preventDefault()
                  e.currentTarget.classList.remove('dragover')
                  const files = e.dataTransfer.files
                  if (files[0]) {
                    const event = { target: { files } }
                    handleImageUpload(event)
                  }
                }}
              >
                <Upload size={48} className="upload-icon" />
                <p className="upload-text">{t('yoga.uploadText', 'Click to upload or drag and drop')}</p>
                <p className="upload-subtext">{t('yoga.uploadSubtext', 'PNG, JPG, GIF up to 10MB')}</p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden-input"
                />
              </div>
            )}
          </div>

          {/* Feedback Panel */}
          <div className="feedback-panel">
            {/* Action Buttons */}
            {mode === 'camera' && capturedImage ? (
              <div className="action-buttons">
                <button
                  onClick={confirmAndAnalyze}
                  disabled={isAnalyzing}
                  className="analyze-button"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="loading-spinner" size={20} />
                      {t('yoga.analyzing', 'Analyzing...')}
                    </>
                  ) : (
                    <>
                      <Check size={20} />
                      {t('yoga.analyzeThisImage', 'Analyze This Image')}
                    </>
                  )}
                </button>
                <button
                  onClick={retakeImage}
                  disabled={isAnalyzing}
                  className="retake-button"
                >
                  <Camera size={20} />
                  {t('yoga.retakeImage', 'Retake Image')}
                </button>
              </div>
            ) : mode === 'upload' && uploadedImage ? (
              <div className="action-buttons">
                <button
                  onClick={confirmAndAnalyze}
                  disabled={isAnalyzing}
                  className="analyze-button"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="loading-spinner" size={20} />
                      {t('yoga.analyzing', 'Analyzing...')}
                    </>
                  ) : (
                    <>
                      <Check size={20} />
                      {t('yoga.analyzeThisImage', 'Analyze This Image')}
                    </>
                  )}
                </button>
                <button
                  onClick={reselectImage}
                  disabled={isAnalyzing}
                  className="retake-button"
                >
                  <Upload size={20} />
                  {t('yoga.selectDifferentImage', 'Select Different Image')}
                </button>
              </div>
            ) : mode === 'camera' ? (
              <button
                onClick={captureImage}
                disabled={isAnalyzing || cameraError}
                className="analyze-button"
              >
                <Camera size={20} />
                {t('yoga.captureImage', 'Capture Image')}
              </button>
            ) : (
              <button
                onClick={() => fileInputRef.current?.click()}
                className="upload-button"
              >
                <Upload size={20} />
                {t('yoga.selectImage', 'Select Image')}
              </button>
            )}

            {feedback && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`feedback-card ${
                  feedback.status === 'Perfect' || feedback.status === 'Excellent' 
                    ? 'success' 
                    : feedback.status === 'Vision Model Not Found'
                    ? 'vision-error'
                    : feedback.status === 'Error' || feedback.status === 'Unsafe'
                    ? 'error'
                    : 'warning'
                } fade-in`}
              >
                <div className="feedback-header">
                  {feedback.status === 'Perfect' || feedback.status === 'Excellent' ? (
                    <CheckCircle size={24} className="feedback-icon success" />
                  ) : (
                    <AlertTriangle size={24} className="feedback-icon warning" />
                  )}
                  <div>
                    <h3 className="feedback-status">
                      {feedback.detected_pose && feedback.detected_pose !== 'Unknown' 
                        ? `${feedback.detected_pose} - ${feedback.status}`
                        : feedback.status
                      }
                    </h3>
                    <p className="feedback-message">{feedback.feedback}</p>
                  </div>
                </div>
                
                {/* Pose Score */}
                {feedback.pose_score !== undefined && (
                  <div className="score-section">
                    <div className="score-header">
                      <span className="score-label">{t('yoga.poseScore', 'Pose Score')}</span>
                      <span className="score-value">{feedback.pose_score}/100</span>
                    </div>
                    <div className="score-bar">
                      <div
                        className="score-fill"
                        style={{ width: `${feedback.pose_score}%` }}
                      />
                    </div>
                  </div>
                )}
                
                {/* Confidence */}
                <div className="confidence-section">
                  <div className="confidence-header">
                    <span className="confidence-label">{t('yoga.confidence', 'Confidence')}</span>
                    <span className="confidence-value">
                      {Math.round(feedback.confidence * 100)}%
                    </span>
                  </div>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{ width: `${feedback.confidence * 100}%` }}
                    />
                  </div>
                </div>

                {/* Corrections */}
                {feedback.corrections && feedback.corrections.length > 0 && (
                  <div className="corrections-section">
                    <h4 className="corrections-title">{t('yoga.corrections', 'Corrections:')}</h4>
                    <ul className="corrections-list">
                      {feedback.corrections.slice(0, 4).map((correction, index) => (
                        <li key={index} className="correction-item">{correction}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommendations */}
                {feedback.recommendations && feedback.recommendations.length > 0 && (
                  <div className="recommendations-section">
                    <h4 className="recommendations-title">{t('yoga.recommendations', 'Recommendations:')}</h4>
                    <ul className="recommendations-list">
                      {feedback.recommendations.slice(0, 3).map((recommendation, index) => (
                        <li key={index} className="recommendation-item">{recommendation}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </motion.div>
            )}

            {/* Tips */}
            <div className="tips-card">
              <h4 className="tips-title">{t('yoga.tipsTitle', 'Tips for Best Results:')}</h4>
              <ul className="tips-list">
                <li>{t('yoga.tips.lighting', 'Ensure good lighting')}</li>
                <li>{t('yoga.tips.distance', 'Stand 6-8 feet from camera')}</li>
                <li>{t('yoga.tips.clothing', 'Wear contrasting clothing')}</li>
                <li>{t('yoga.tips.frame', 'Keep full body in frame')}</li>
              </ul>
            </div>
          </div>
        </div>


      </div>
    </div>
  )
}
