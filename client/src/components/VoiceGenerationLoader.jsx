import { useState, useEffect } from 'react'
import { Volume2, Brain, Sparkles, Mic } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function VoiceGenerationLoader({ 
  isGenerating, 
  currentPhase = "setup",
  meditationType = "mindfulness",
  onCancel 
}) {
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0)
  const [dots, setDots] = useState('')

  const loadingMessages = [
    {
      icon: Brain,
      text: "AI is crafting your personalized meditation guidance...",
      subtext: "Analyzing your meditation preferences and generating wisdom"
    },
    {
      icon: Sparkles,
      text: "Converting text to natural voice using gTTS...",
      subtext: "Creating soothing speech patterns for deep relaxation"
    },
    {
      icon: Volume2,
      text: "Optimizing audio quality for meditation...",
      subtext: "Adjusting pace and tone for peaceful guidance"
    },
    {
      icon: Mic,
      text: "Almost ready for your spiritual journey...",
      subtext: "Final audio processing and quality checks"
    }
  ]

  const phaseMessages = {
    setup: "Preparing your meditation setup guidance",
    breathing: "Creating breathing exercise instructions", 
    meditation: "Crafting deep meditation guidance",
    completion: "Preparing session completion message"
  }

  const typeMessages = {
    mindfulness: "Focusing on present-moment awareness",
    'loving-kindness': "Cultivating compassion and love",
    nature: "Connecting with natural elements",
    sleep: "Preparing for restful sleep",
    energy: "Awakening inner vitality"
  }

  // Cycle through messages every 3 seconds
  useEffect(() => {
    if (!isGenerating) return

    const messageInterval = setInterval(() => {
      setCurrentMessageIndex(prev => (prev + 1) % loadingMessages.length)
    }, 3000)

    return () => clearInterval(messageInterval)
  }, [isGenerating, loadingMessages.length])

  // Animate dots
  useEffect(() => {
    if (!isGenerating) return

    const dotsInterval = setInterval(() => {
      setDots(prev => {
        if (prev === '...') return ''
        return prev + '.'
      })
    }, 500)

    return () => clearInterval(dotsInterval)
  }, [isGenerating])

  if (!isGenerating) return null

  const currentMessage = loadingMessages[currentMessageIndex]
  const Icon = currentMessage.icon

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="glass-card bg-gradient-to-br from-blue-50 to-purple-50 border-2 border-blue-200 text-center py-8 px-6"
    >
      {/* Animated Icon */}
      <motion.div
        animate={{ 
          scale: [1, 1.1, 1],
          rotate: [0, 5, -5, 0]
        }}
        transition={{ 
          duration: 2,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="w-16 h-16 mx-auto mb-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center"
      >
        <Icon size={32} className="text-white" />
      </motion.div>

      {/* Main Loading Message */}
      <AnimatePresence mode="wait">
        <motion.div
          key={currentMessageIndex}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.5 }}
          className="mb-4"
        >
          <h3 className="text-xl font-bold text-gray-800 mb-2">
            {currentMessage.text}{dots}
          </h3>
          <p className="text-gray-600 text-sm">
            {currentMessage.subtext}
          </p>
        </motion.div>
      </AnimatePresence>

      {/* Phase and Type Info */}
      <div className="space-y-2 mb-6">
        <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
          <span className="font-medium">Phase:</span>
          <span className="capitalize bg-blue-100 px-2 py-1 rounded-full">
            {phaseMessages[currentPhase] || currentPhase}
          </span>
        </div>
        <div className="flex items-center justify-center gap-2 text-sm text-gray-600">
          <span className="font-medium">Type:</span>
          <span className="capitalize bg-purple-100 px-2 py-1 rounded-full">
            {typeMessages[meditationType] || meditationType}
          </span>
        </div>
      </div>

      {/* Progress Animation */}
      <div className="mb-6">
        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-full"
            animate={{ 
              width: ["0%", "100%", "0%"]
            }}
            transition={{ 
              duration: 4,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Generating voice guidance with gTTS... This may take 5-15 seconds
        </p>
      </div>

      {/* Spinning Loader */}
      <div className="flex justify-center mb-6">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
          className="w-8 h-8 border-3 border-blue-500 border-t-transparent rounded-full"
        />
      </div>

      {/* Cancel Button */}
      {onCancel && (
        <button
          onClick={onCancel}
          className="text-gray-500 hover:text-gray-700 text-sm underline transition-colors"
        >
          Cancel Generation
        </button>
      )}

      {/* Tips */}
      <div className="mt-6 p-4 bg-white/50 rounded-lg">
        <p className="text-xs text-gray-600 mb-2 font-medium">💡 While you wait:</p>
        <ul className="text-xs text-gray-500 space-y-1">
          <li>• Find a quiet, comfortable space</li>
          <li>• Adjust your device volume</li>
          <li>• Take a few deep breaths to prepare</li>
          <li>• Close your eyes and relax</li>
        </ul>
      </div>
    </motion.div>
  )
}