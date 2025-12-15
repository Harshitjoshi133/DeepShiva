import { useState, useEffect, useRef } from 'react'
import { Play, Pause, Volume2, VolumeX, RotateCcw, Settings } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export default function MeditationAudioPlayer({ 
  audioBase64, 
  isPlaying, 
  onPlayPause, 
  onEnded,
  currentPhase = "meditation",
  showControls = true,
  autoPlay = false 
}) {
  const [volume, setVolume] = useState(0.8)
  const [isMuted, setIsMuted] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const audioRef = useRef(null)
  const progressRef = useRef(null)

  // Create audio element when audioBase64 changes
  useEffect(() => {
    if (audioBase64) {
      setIsLoading(true)
      setError(null)
      
      try {
        // Convert base64 to blob URL
        const audioBlob = base64ToBlob(audioBase64, 'audio/wav')
        const audioUrl = URL.createObjectURL(audioBlob)
        
        // Create new audio element
        const audio = new Audio(audioUrl)
        audioRef.current = audio
        
        // Set up event listeners
        audio.addEventListener('loadedmetadata', () => {
          setDuration(audio.duration)
          setIsLoading(false)
        })
        
        audio.addEventListener('timeupdate', () => {
          setCurrentTime(audio.currentTime)
        })
        
        audio.addEventListener('ended', () => {
          setCurrentTime(0)
          if (onEnded) onEnded()
        })
        
        audio.addEventListener('error', (e) => {
          console.error('Audio playback error:', e)
          setError('Failed to load audio')
          setIsLoading(false)
        })
        
        // Set initial volume
        audio.volume = volume
        audio.muted = isMuted
        
        // Auto play if requested
        if (autoPlay) {
          audio.play().catch(e => {
            console.error('Auto-play failed:', e)
            setError('Auto-play blocked by browser')
          })
        }
        
        // Cleanup function
        return () => {
          audio.pause()
          URL.revokeObjectURL(audioUrl)
        }
        
      } catch (e) {
        console.error('Error creating audio element:', e)
        setError('Failed to create audio player')
        setIsLoading(false)
      }
    }
  }, [audioBase64, autoPlay])

  // Handle play/pause from parent component
  useEffect(() => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.play().catch(e => {
          console.error('Play failed:', e)
          setError('Playback failed')
        })
      } else {
        audioRef.current.pause()
      }
    }
  }, [isPlaying])

  // Update volume
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = volume
    }
  }, [volume])

  // Update mute state
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.muted = isMuted
    }
  }, [isMuted])

  const base64ToBlob = (base64, mimeType) => {
    const byteCharacters = atob(base64)
    const byteNumbers = new Array(byteCharacters.length)
    
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i)
    }
    
    const byteArray = new Uint8Array(byteNumbers)
    return new Blob([byteArray], { type: mimeType })
  }

  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00'
    
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const handleProgressClick = (e) => {
    if (!audioRef.current || !progressRef.current) return
    
    const rect = progressRef.current.getBoundingClientRect()
    const clickX = e.clientX - rect.left
    const width = rect.width
    const percentage = clickX / width
    const newTime = percentage * duration
    
    audioRef.current.currentTime = newTime
    setCurrentTime(newTime)
  }

  const handlePlayPause = () => {
    if (onPlayPause) {
      onPlayPause()
    }
  }

  const handleRestart = () => {
    if (audioRef.current) {
      audioRef.current.currentTime = 0
      setCurrentTime(0)
    }
  }

  const toggleMute = () => {
    setIsMuted(!isMuted)
  }

  const progressPercentage = duration > 0 ? (currentTime / duration) * 100 : 0

  if (!audioBase64) {
    return (
      <div className="flex items-center justify-center p-4 text-gray-500">
        <Volume2 size={20} className="mr-2" />
        <span>No audio available</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center p-4 text-red-500">
        <VolumeX size={20} className="mr-2" />
        <span>{error}</span>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-4 space-y-4">
      {/* Phase Indicator */}
      <div className="text-center">
        <h4 className="text-sm font-semibold text-gray-600 uppercase tracking-wide">
          {currentPhase} Guidance
        </h4>
      </div>

      {/* Progress Bar */}
      <div className="space-y-2">
        <div 
          ref={progressRef}
          className="w-full h-2 bg-gray-200 rounded-full cursor-pointer relative overflow-hidden"
          onClick={handleProgressClick}
        >
          <motion.div
            className="h-full bg-gradient-to-r from-blue-400 to-purple-500 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progressPercentage}%` }}
            transition={{ duration: 0.1 }}
          />
        </div>
        
        <div className="flex justify-between text-xs text-gray-500">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      {/* Controls */}
      {showControls && (
        <div className="flex items-center justify-center space-x-4">
          {/* Restart Button */}
          <button
            onClick={handleRestart}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-full transition-colors"
            title="Restart"
          >
            <RotateCcw size={20} />
          </button>

          {/* Play/Pause Button */}
          <button
            onClick={handlePlayPause}
            disabled={isLoading}
            className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-full hover:from-blue-600 hover:to-purple-700 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
            title={isPlaying ? "Pause" : "Play"}
          >
            {isLoading ? (
              <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : isPlaying ? (
              <Pause size={24} />
            ) : (
              <Play size={24} />
            )}
          </button>

          {/* Mute Button */}
          <button
            onClick={toggleMute}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-full transition-colors"
            title={isMuted ? "Unmute" : "Mute"}
          >
            {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
          </button>
        </div>
      )}

      {/* Volume Control */}
      {showControls && (
        <div className="flex items-center space-x-3">
          <Volume2 size={16} className="text-gray-500" />
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={volume}
            onChange={(e) => setVolume(parseFloat(e.target.value))}
            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
          />
          <span className="text-xs text-gray-500 w-8">
            {Math.round(volume * 100)}%
          </span>
        </div>
      )}

      {/* Loading State */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="text-center text-sm text-gray-500"
          >
            Loading audio guidance...
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}