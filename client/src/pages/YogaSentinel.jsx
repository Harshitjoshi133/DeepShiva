import { useState, useRef } from 'react'
import Webcam from 'react-webcam'
import { Camera, Loader2, CheckCircle, AlertTriangle } from 'lucide-react'
import { motion } from 'framer-motion'
import { useLanguage } from '../contexts/LanguageContext'

export default function YogaSentinel() {
  const { t } = useLanguage()
  const webcamRef = useRef(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [feedback, setFeedback] = useState(null)
  const [cameraError, setCameraError] = useState(false)

  const captureAndAnalyze = async () => {
    if (!webcamRef.current) return

    setIsAnalyzing(true)
    setFeedback(null)

    try {
      const imageSrc = webcamRef.current.getScreenshot()
      const base64Image = imageSrc.split(',')[1]

      const response = await fetch('/api/v1/vision/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: base64Image })
      })

      const data = await response.json()
      setFeedback(data)
    } catch (error) {
      setFeedback({
        status: 'Error',
        feedback: 'Failed to analyze pose. Please try again.',
        confidence: 0
      })
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleUserMediaError = () => {
    setCameraError(true)
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="glass-card shadow-2xl">
        <h2 className="text-xl font-bold gradient-text mb-3">{t('yoga.title', 'Yoga Sentinel')}</h2>
        <p className="text-gray-600 mb-3 text-sm">
          {t('yoga.description', 'Position yourself in front of the camera and click "Analyze Pose" for real-time feedback on your yoga posture.')}
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
          {/* Camera Feed */}
          <div className="relative bg-gray-900 rounded-lg overflow-hidden aspect-video">
            {cameraError ? (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-white p-4 text-center">
                <AlertTriangle size={40} className="mb-3 text-yellow-500" />
                <h3 className="text-lg font-semibold mb-2">{t('yoga.cameraRequired', 'Camera Access Required')}</h3>
                <p className="text-gray-300 text-sm">
                  {t('yoga.cameraMessage', 'Please allow camera access in your browser settings to use Yoga Sentinel.')}
                </p>
              </div>
            ) : (
              <>
                <Webcam
                  ref={webcamRef}
                  audio={false}
                  screenshotFormat="image/jpeg"
                  className="w-full h-full object-cover"
                  onUserMediaError={handleUserMediaError}
                />
                
                {/* Skeleton Overlay Guide */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-30">
                  <circle cx="50%" cy="20%" r="30" fill="none" stroke="#FF9933" strokeWidth="2" />
                  <line x1="50%" y1="25%" x2="50%" y2="45%" stroke="#FF9933" strokeWidth="2" />
                  <line x1="50%" y1="35%" x2="35%" y2="50%" stroke="#FF9933" strokeWidth="2" />
                  <line x1="50%" y1="35%" x2="65%" y2="50%" stroke="#FF9933" strokeWidth="2" />
                  <line x1="50%" y1="45%" x2="40%" y2="70%" stroke="#FF9933" strokeWidth="2" />
                  <line x1="50%" y1="45%" x2="60%" y2="70%" stroke="#FF9933" strokeWidth="2" />
                </svg>
              </>
            )}
          </div>

          {/* Feedback Panel */}
          <div className="space-y-2">
            <button
              onClick={captureAndAnalyze}
              disabled={isAnalyzing || cameraError}
              className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  {t('yoga.analyzing', 'Analyzing...')}
                </>
              ) : (
                <>
                  <Camera size={20} />
                  {t('yoga.analyzePose', 'Analyze Pose')}
                </>
              )}
            </button>

            {feedback && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`glass-card ${
                  feedback.status === 'Perfect' 
                    ? 'bg-green-100/80 border-2 border-green-500/30' 
                    : 'bg-orange-100/80 border-2 border-orange-500/30'
                } shadow-xl`}
              >
                <div className="flex items-start gap-2 mb-3">
                  {feedback.status === 'Perfect' ? (
                    <CheckCircle size={24} className="text-green-600 flex-shrink-0" />
                  ) : (
                    <AlertTriangle size={24} className="text-orange-600 flex-shrink-0" />
                  )}
                  <div>
                    <h3 className="text-lg font-bold text-gray-800 mb-1">{feedback.status}</h3>
                    <p className="text-gray-700 text-sm">{feedback.feedback}</p>
                  </div>
                </div>
                
                <div className="mt-3">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-xs font-semibold text-gray-700">{t('yoga.confidence', 'Confidence')}</span>
                    <span className="text-xs font-bold text-gray-800">
                      {Math.round(feedback.confidence * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-300 rounded-full h-2">
                    <div
                      className="bg-saffron h-2 rounded-full transition-all duration-500"
                      style={{ width: `${feedback.confidence * 100}%` }}
                    />
                  </div>
                </div>
              </motion.div>
            )}

            {/* Tips */}
            <div className="glass-card bg-blue-50/80 border-2 border-blue-200/30">
              <h4 className="font-semibold text-gray-800 mb-2 text-sm">{t('yoga.tipsTitle', 'Tips for Best Results:')}</h4>
              <ul className="text-xs text-gray-700 space-y-1 list-disc list-inside">
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
