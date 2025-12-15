import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

export default function BreathingAnimation({ isActive, pattern = [4, 4, 4, 4] }) {
  const [phase, setPhase] = useState(0) // 0: inhale, 1: hold, 2: exhale, 3: hold
  const [count, setCount] = useState(0)
  
  const phaseNames = ['Inhale', 'Hold', 'Exhale', 'Hold']
  const [inhale, hold1, exhale, hold2] = pattern

  useEffect(() => {
    if (!isActive) return

    const interval = setInterval(() => {
      setCount(prev => {
        const currentPhaseDuration = pattern[phase]
        if (prev >= currentPhaseDuration - 1) {
          setPhase(prevPhase => (prevPhase + 1) % 4)
          return 0
        }
        return prev + 1
      })
    }, 1000)

    return () => clearInterval(interval)
  }, [isActive, phase, pattern])

  const getCircleScale = () => {
    switch (phase) {
      case 0: // inhale
        return 1 + (count / inhale) * 0.5
      case 1: // hold after inhale
        return 1.5
      case 2: // exhale
        return 1.5 - (count / exhale) * 0.5
      case 3: // hold after exhale
        return 1
      default:
        return 1
    }
  }

  const getCircleOpacity = () => {
    switch (phase) {
      case 0: // inhale
        return 0.3 + (count / inhale) * 0.4
      case 1: // hold after inhale
        return 0.7
      case 2: // exhale
        return 0.7 - (count / exhale) * 0.4
      case 3: // hold after exhale
        return 0.3
      default:
        return 0.3
    }
  }

  if (!isActive) {
    return (
      <div className="flex flex-col items-center justify-center h-64">
        <div className="w-32 h-32 rounded-full bg-gradient-to-r from-blue-400 to-purple-500 opacity-30"></div>
        <p className="mt-4 text-gray-500">Press play to start breathing guidance</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center justify-center h-64">
      <motion.div
        className="w-32 h-32 rounded-full bg-gradient-to-r from-blue-400 to-purple-500 flex items-center justify-center"
        animate={{
          scale: getCircleScale(),
          opacity: getCircleOpacity()
        }}
        transition={{
          duration: 1,
          ease: "easeInOut"
        }}
      >
        <div className="text-white font-semibold text-lg">
          {pattern[phase] - count}
        </div>
      </motion.div>
      
      <div className="mt-6 text-center">
        <p className="text-xl font-semibold text-gray-700 mb-2">
          {phaseNames[phase]}
        </p>
        <div className="flex justify-center space-x-2">
          {pattern.map((duration, index) => (
            <div
              key={index}
              className={`w-3 h-3 rounded-full transition-colors ${
                index === phase ? 'bg-blue-500' : 'bg-gray-300'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  )
}