import { useState, useRef } from 'react'
import Webcam from 'react-webcam'
import { Camera, Loader2, CheckCircle, AlertTriangle } from 'lucide-react'
import { motion } from 'framer-motion'

export default function YogaSentinel() {
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
    <div className="max-w-5xl mx-auto">
      <div className="card">
        <h2 className="text-3xl font-bold text-gray-800 mb-6">Yoga Sentinel</h2>
        <p className="text-gray-600 mb-6">
          Position yourself in front of the camera and click "Analyze Pose" for real-time feedback on your yoga posture.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Camera Feed */}
          <div className="relative bg-gray-900 rounded-lg overflow-hidden aspect-video">
            {cameraError ? (
              <div className="absolute inset-0 flex flex-col items-center justify-center text-white p-6 text-center">
                <AlertTriangle size={48} className="mb-4 text-yellow-500" />
                <h3 className="text-xl font-semibold mb-2">Camera Access Required</h3>
                <p className="text-gray-300">
                  Please allow camera access in your browser settings to use Yoga Sentinel.
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
          <div className="space-y-4">
            <button
              onClick={captureAndAnalyze}
              disabled={isAnalyzing || cameraError}
              className="w-full btn-primary flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="animate-spin" size={24} />
                  Analyzing...
                </>
              ) : (
                <>
                  <Camera size={24} />
                  Analyze Pose
                </>
              )}
            </button>

            {feedback && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`p-6 rounded-lg ${
                  feedback.status === 'Perfect' 
                    ? 'bg-green-100 border-2 border-green-500' 
                    : 'bg-orange-100 border-2 border-orange-500'
                }`}
              >
                <div className="flex items-start gap-3 mb-4">
                  {feedback.status === 'Perfect' ? (
                    <CheckCircle size={32} className="text-green-600 flex-shrink-0" />
                  ) : (
                    <AlertTriangle size={32} className="text-orange-600 flex-shrink-0" />
                  )}
                  <div>
                    <h3 className="text-xl font-bold text-gray-800 mb-2">{feedback.status}</h3>
                    <p className="text-gray-700 text-lg">{feedback.feedback}</p>
                  </div>
                </div>
                
                <div className="mt-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-semibold text-gray-700">Confidence</span>
                    <span className="text-sm font-bold text-gray-800">
                      {Math.round(feedback.confidence * 100)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-300 rounded-full h-3">
                    <div
                      className="bg-saffron h-3 rounded-full transition-all duration-500"
                      style={{ width: `${feedback.confidence * 100}%` }}
                    />
                  </div>
                </div>
              </motion.div>
            )}

            {/* Tips */}
            <div className="bg-blue-50 p-4 rounded-lg border-2 border-blue-200">
              <h4 className="font-semibold text-gray-800 mb-2">Tips for Best Results:</h4>
              <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
                <li>Ensure good lighting</li>
                <li>Stand 6-8 feet from camera</li>
                <li>Wear contrasting clothing</li>
                <li>Keep full body in frame</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
