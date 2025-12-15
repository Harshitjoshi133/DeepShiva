import { useState, useEffect, useRef } from 'react'
import { Play, Pause, RotateCcw, Settings, Brain, Heart, Leaf, Moon, Sun, Volume2, VolumeX } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useLanguage } from '../contexts/LanguageContext'
import BreathingAnimation from '../components/BreathingAnimation'
import MeditationAudioPlayer from '../components/MeditationAudioPlayer'
import VoiceGenerationLoader from '../components/VoiceGenerationLoader'

export default function Meditation() {
  const { t } = useLanguage()
  const [isActive, setIsActive] = useState(false)
  const [timeLeft, setTimeLeft] = useState(0)
  const [selectedDuration, setSelectedDuration] = useState(5)
  const [selectedType, setSelectedType] = useState('mindfulness')
  const [currentPhase, setCurrentPhase] = useState('setup') // setup, breathing, meditation, completion
  const [breathingPattern, setBreathingPattern] = useState('4-4-4-4') // inhale-hold-exhale-hold
  const [isMuted, setIsMuted] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [aiGuidance, setAiGuidance] = useState('')
  const [breathingCycle, setBreathingCycle] = useState(0)
  const [audioBase64, setAudioBase64] = useState(null)
  const [isAudioPlaying, setIsAudioPlaying] = useState(false)
  const [hasAudio, setHasAudio] = useState(false)
  const [voiceEnabled, setVoiceEnabled] = useState(true)
  const [availableVoices, setAvailableVoices] = useState([])
  const [selectedVoice, setSelectedVoice] = useState(0)
  const [voiceSpeed, setVoiceSpeed] = useState(130)
  const [ttsError, setTtsError] = useState(null)
  const [isVoiceServiceAvailable, setIsVoiceServiceAvailable] = useState(true)
  const [isGeneratingVoice, setIsGeneratingVoice] = useState(false)
  const [voiceReady, setVoiceReady] = useState(false)
  const [generationCancelled, setGenerationCancelled] = useState(false)
  const intervalRef = useRef(null)
  const audioRef = useRef(null)

  const meditationTypes = [
    {
      id: 'mindfulness',
      name: t('meditation.types.mindfulness', 'Mindfulness'),
      icon: Brain,
      description: t('meditation.types.mindfulnessDesc', 'Focus on present moment awareness'),
      color: 'from-blue-400 to-blue-600'
    },
    {
      id: 'loving-kindness',
      name: t('meditation.types.lovingKindness', 'Loving Kindness'),
      icon: Heart,
      description: t('meditation.types.lovingKindnessDesc', 'Cultivate compassion and love'),
      color: 'from-pink-400 to-pink-600'
    },
    {
      id: 'nature',
      name: t('meditation.types.nature', 'Nature Connection'),
      icon: Leaf,
      description: t('meditation.types.natureDesc', 'Connect with natural elements'),
      color: 'from-green-400 to-green-600'
    },
    {
      id: 'sleep',
      name: t('meditation.types.sleep', 'Sleep Preparation'),
      icon: Moon,
      description: t('meditation.types.sleepDesc', 'Prepare for restful sleep'),
      color: 'from-indigo-400 to-purple-600'
    },
    {
      id: 'energy',
      name: t('meditation.types.energy', 'Energy Boost'),
      icon: Sun,
      description: t('meditation.types.energyDesc', 'Increase vitality and focus'),
      color: 'from-yellow-400 to-orange-600'
    }
  ]

  const durations = [3, 5, 10, 15, 20, 30]
  const breathingPatterns = [
    { id: '4-4-4-4', name: 'Box Breathing', pattern: [4, 4, 4, 4] },
    { id: '4-7-8', name: '4-7-8 Technique', pattern: [4, 7, 8, 0] },
    { id: '6-2-6-2', name: 'Calm Breathing', pattern: [6, 2, 6, 2] }
  ]

  const getCurrentBreathingPattern = () => {
    return breathingPatterns.find(p => p.id === breathingPattern)?.pattern || [4, 4, 4, 4]
  }

  useEffect(() => {
    if (isActive && timeLeft > 0) {
      intervalRef.current = setInterval(() => {
        setTimeLeft(prev => {
          if (prev <= 1) {
            handleMeditationComplete()
            return 0
          }
          return prev - 1
        })
      }, 1000)
    } else {
      clearInterval(intervalRef.current)
    }

    return () => clearInterval(intervalRef.current)
  }, [isActive, timeLeft])

  useEffect(() => {
    // Only auto-generate guidance during active meditation phases
    if (currentPhase !== 'setup') {
      generateAIGuidance()
    }
  }, [selectedType, currentPhase])

  useEffect(() => {
    // Load available voices on component mount
    loadAvailableVoices()
  }, [])

  const generateAIGuidance = async () => {
    try {
      setTtsError(null) // Clear any previous errors
      setGenerationCancelled(false)
      
      // Import the meditation service dynamically to avoid circular imports
      const { meditationService } = await import('../services/meditationService')
      
      let response
      
      // For voice-guided meditation, always try to get audio
      if (voiceEnabled && isVoiceServiceAvailable) {
        setIsGeneratingVoice(true)
        setVoiceReady(false)
        
        try {
          response = await meditationService.getGuidanceWithAudio(selectedType, currentPhase, selectedDuration)
          
          // Check if generation was cancelled
          if (generationCancelled) {
            console.log('Voice generation cancelled by user')
            return
          }
          
          if (response && response.guidance) {
            setAiGuidance(response.guidance)
            
            // Handle audio - must be available for voice-guided meditation
            if (response.has_audio && response.audio_base64) {
              setAudioBase64(response.audio_base64)
              setHasAudio(true)
              setVoiceReady(true)
              console.log('🔊 Voice guidance generated successfully')
            } else {
              throw new Error('Voice guidance generation failed - no audio received')
            }
          } else {
            throw new Error('No guidance received from AI service')
          }
        } finally {
          setIsGeneratingVoice(false)
        }
      } else {
        // Voice disabled - use text-only mode
        response = await meditationService.getGuidance(selectedType, currentPhase, selectedDuration)
        
        if (response && response.guidance) {
          setAiGuidance(response.guidance)
          setAudioBase64(null)
          setHasAudio(false)
          setVoiceReady(true) // Text is immediately ready
          console.log('📝 Text-only guidance generated')
        } else {
          throw new Error('No guidance received from AI service')
        }
      }
      
    } catch (error) {
      console.error('❌ Error getting AI guidance:', error)
      setIsGeneratingVoice(false)
      
      // Check if this is a TTS service error
      if (error.message.includes('Voice-guided meditation') || error.message.includes('TTS')) {
        setTtsError(error.message)
        setIsVoiceServiceAvailable(false)
        setHasAudio(false)
        setAudioBase64(null)
        setVoiceReady(false)
        
        // Don't provide fallback guidance for voice-guided meditation
        setAiGuidance('')
        
        return // Exit without setting fallback guidance
      }
      
      // For other errors, provide basic fallback
      setAiGuidance('Unable to generate meditation guidance. Please check your connection and try again.')
      setAudioBase64(null)
      setHasAudio(false)
      setVoiceReady(false)
    }
  }

  const cancelVoiceGeneration = () => {
    setGenerationCancelled(true)
    setIsGeneratingVoice(false)
    setVoiceReady(false)
    console.log('Voice generation cancelled by user')
  }

  const loadAvailableVoices = async () => {
    try {
      const { meditationService } = await import('../services/meditationService')
      const voicesData = await meditationService.getAvailableVoices()
      
      if (voicesData.success && voicesData.voices) {
        setAvailableVoices(voicesData.voices)
        console.log(`🎤 Loaded ${voicesData.voices.length} available voices`)
      }
    } catch (error) {
      console.error('Error loading available voices:', error)
    }
  }

  const startMeditation = () => {
    // Check if voice is enabled but TTS service has errors
    if (voiceEnabled && (ttsError || !isVoiceServiceAvailable)) {
      alert(t('meditation.cannotStartVoiceError', 'Cannot start voice-guided meditation. Please fix voice service issues or disable voice guidance.'))
      return
    }
    
    // Check if voice is enabled but not ready yet
    if (voiceEnabled && !voiceReady && !ttsError) {
      alert(t('meditation.voiceNotReady', 'Please wait for voice generation to complete before starting meditation.'))
      return
    }
    
    setTimeLeft(selectedDuration * 60)
    setIsActive(true)
    setCurrentPhase('breathing')
    setBreathingCycle(0)
  }

  const generateVoiceGuidance = async () => {
    await generateAIGuidance()
  }

  const pauseMeditation = () => {
    setIsActive(!isActive)
  }

  const resetMeditation = () => {
    setIsActive(false)
    setTimeLeft(0)
    setCurrentPhase('setup')
    setBreathingCycle(0)
  }

  const handleMeditationComplete = async () => {
    setIsActive(false)
    setCurrentPhase('completion')
    setAiGuidance("Wonderful! You've completed your meditation. Take a moment to notice how you feel. Gently wiggle your fingers and toes, and when you're ready, slowly open your eyes.")
    
    // Save the meditation session
    try {
      const { meditationService } = await import('../services/meditationService')
      
      const sessionData = {
        meditation_type: selectedType,
        duration: selectedDuration,
        completed: true,
        user_rating: null,
        notes: null
      }
      
      const result = await meditationService.saveSession(sessionData)
      
      if (result) {
        console.log('✅ Meditation session completed and saved')
      }
    } catch (error) {
      console.error('❌ Error saving meditation session:', error)
      // Session will be handled by the service's fallback mechanism
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getSelectedType = () => meditationTypes.find(type => type.id === selectedType)
  const selectedTypeData = getSelectedType()

  return (
    <div className="max-w-4xl mx-auto space-y-4">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">
          {t('meditation.title', 'AI-Guided Meditation')}
        </h2>
        <p className="text-gray-600">
          {t('meditation.subtitle', 'Find inner peace with personalized meditation guidance')}
        </p>
      </div>

      {/* TTS Error Display */}
      {ttsError && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-card bg-gradient-to-r from-red-50 to-orange-50 border-2 border-red-200 mb-6"
        >
          <div className="flex items-center gap-3 mb-3">
            <VolumeX className="text-red-500" size={24} />
            <h3 className="text-lg font-semibold text-red-700">
              {t('meditation.voiceServiceError', 'Voice Service Unavailable')}
            </h3>
          </div>
          <p className="text-red-600 mb-4">{ttsError}</p>
          <div className="space-y-2">
            <p className="text-sm text-red-500">
              {t('meditation.voiceErrorHelp', 'To use voice-guided meditation:')}
            </p>
            <ul className="text-xs text-red-500 list-disc list-inside space-y-1">
              <li>Ensure TTS dependencies are installed (pyttsx3, gTTS)</li>
              <li>Check system voice settings and permissions</li>
              <li>Verify internet connection for online TTS</li>
              <li>Contact support if the issue persists</li>
            </ul>
          </div>
          <div className="flex gap-3 mt-4">
            <button
              onClick={() => {
                setTtsError(null)
                setIsVoiceServiceAvailable(true)
                generateAIGuidance()
              }}
              className="btn-primary"
            >
              {t('meditation.retryVoice', 'Retry Voice Service')}
            </button>
            <button
              onClick={() => {
                setVoiceEnabled(false)
                setTtsError(null)
                generateAIGuidance()
              }}
              className="btn-secondary"
            >
              {t('meditation.useTextOnly', 'Use Text Only')}
            </button>
          </div>
        </motion.div>
      )}

      {currentPhase === 'setup' && !ttsError && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6"
        >
          {/* Meditation Type Selection */}
          <div className="glass-card">
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Brain className="text-saffron" size={20} />
              {t('meditation.selectType', 'Choose Your Meditation Type')}
            </h3>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
              {meditationTypes.map((type) => {
                const Icon = type.icon
                return (
                  <motion.button
                    key={type.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setSelectedType(type.id)}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      selectedType === type.id
                        ? 'border-saffron bg-gradient-to-r ' + type.color + ' text-white'
                        : 'border-gray-200 hover:border-saffron bg-white'
                    }`}
                  >
                    <Icon size={24} className="mx-auto mb-2" />
                    <h4 className="font-semibold text-sm">{type.name}</h4>
                    <p className={`text-xs mt-1 ${selectedType === type.id ? 'text-white/90' : 'text-gray-600'}`}>
                      {type.description}
                    </p>
                  </motion.button>
                )
              })}
            </div>
          </div>

          {/* Duration Selection */}
          <div className="glass-card">
            <h3 className="text-lg font-semibold mb-4">
              {t('meditation.selectDuration', 'Choose Duration')}
            </h3>
            <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
              {durations.map((duration) => (
                <button
                  key={duration}
                  onClick={() => setSelectedDuration(duration)}
                  className={`py-3 px-4 rounded-lg font-semibold transition-all ${
                    selectedDuration === duration
                      ? 'bg-saffron text-white'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                  }`}
                >
                  {duration}m
                </button>
              ))}
            </div>
          </div>

          {/* Settings */}
          <div className="glass-card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                {t('meditation.settings', 'Settings')}
              </h3>
              <button
                onClick={() => setShowSettings(!showSettings)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <Settings size={20} />
              </button>
            </div>
            
            <AnimatePresence>
              {showSettings && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  className="space-y-4"
                >
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      {t('meditation.breathingPattern', 'Breathing Pattern')}
                    </label>
                    <select
                      value={breathingPattern}
                      onChange={(e) => setBreathingPattern(e.target.value)}
                      className="w-full p-2 border rounded-lg"
                    >
                      {breathingPatterns.map((pattern) => (
                        <option key={pattern.id} value={pattern.id}>
                          {pattern.name}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">
                      {t('meditation.voiceGuidance', 'Voice Guidance')}
                    </span>
                    <button
                      onClick={() => setVoiceEnabled(!voiceEnabled)}
                      className={`p-2 rounded-lg ${voiceEnabled ? 'bg-saffron text-white' : 'bg-gray-200'}`}
                    >
                      {voiceEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
                    </button>
                  </div>
                  
                  {voiceEnabled && (
                    <>
                      <div>
                        <label className="block text-sm font-medium mb-2">
                          {t('meditation.voiceSpeed', 'Voice Speed')}
                        </label>
                        <input
                          type="range"
                          min="80"
                          max="200"
                          value={voiceSpeed}
                          onChange={(e) => setVoiceSpeed(parseInt(e.target.value))}
                          className="w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                          <span>Slow</span>
                          <span>{voiceSpeed} WPM</span>
                          <span>Fast</span>
                        </div>
                      </div>
                      
                      {availableVoices.length > 0 && (
                        <div>
                          <label className="block text-sm font-medium mb-2">
                            {t('meditation.voiceSelection', 'Voice Selection')}
                          </label>
                          <select
                            value={selectedVoice}
                            onChange={(e) => setSelectedVoice(parseInt(e.target.value))}
                            className="w-full p-2 border rounded-lg"
                          >
                            {availableVoices.map((voice, index) => (
                              <option key={index} value={index}>
                                {voice.name} ({voice.gender})
                              </option>
                            ))}
                          </select>
                        </div>
                      )}
                    </>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Voice Generation Section */}
          {voiceEnabled && !ttsError && (
            <div className="space-y-4">
              {/* Voice Generation Loader */}
              {isGeneratingVoice && (
                <VoiceGenerationLoader
                  isGenerating={isGeneratingVoice}
                  currentPhase={currentPhase}
                  meditationType={selectedType}
                  onCancel={cancelVoiceGeneration}
                />
              )}

              {/* Voice Ready Indicator */}
              {voiceReady && hasAudio && !isGeneratingVoice && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="glass-card bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 text-center py-4"
                >
                  <div className="flex items-center justify-center gap-3 mb-2">
                    <Volume2 className="text-green-600" size={24} />
                    <h3 className="text-lg font-semibold text-green-700">
                      {t('meditation.voiceReady', 'Voice Guidance Ready!')}
                    </h3>
                  </div>
                  <p className="text-green-600 text-sm">
                    {t('meditation.voiceReadyDesc', 'Your personalized meditation guidance has been generated and is ready to play.')}
                  </p>
                </motion.div>
              )}

              {/* Generate Voice Button */}
              {!voiceReady && !isGeneratingVoice && !ttsError && (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={generateVoiceGuidance}
                  className="w-full btn-secondary py-4 text-lg font-semibold flex items-center justify-center gap-3"
                >
                  <Volume2 size={24} />
                  {t('meditation.generateVoice', 'Generate Voice Guidance')}
                </motion.button>
              )}
            </div>
          )}

          {/* Start Button */}
          <motion.button
            whileHover={{ scale: voiceReady || !voiceEnabled ? 1.02 : 1 }}
            whileTap={{ scale: voiceReady || !voiceEnabled ? 0.98 : 1 }}
            onClick={startMeditation}
            disabled={voiceEnabled && !voiceReady && !ttsError}
            className={`w-full py-4 text-lg font-semibold flex items-center justify-center gap-3 transition-all ${
              voiceEnabled && !voiceReady && !ttsError
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'btn-primary hover:scale-105'
            }`}
          >
            <Play size={24} />
            {voiceEnabled && !voiceReady && !ttsError
              ? t('meditation.waitingForVoice', 'Waiting for Voice...')
              : t('meditation.startMeditation', 'Start Meditation')
            }
          </motion.button>
        </motion.div>
      )}

      {(currentPhase === 'breathing' || currentPhase === 'meditation') && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-center space-y-6"
        >
          {/* Voice Generation Loader for Active Session */}
          {isGeneratingVoice && (
            <VoiceGenerationLoader
              isGenerating={isGeneratingVoice}
              currentPhase={currentPhase}
              meditationType={selectedType}
              onCancel={cancelVoiceGeneration}
            />
          )}

          {/* Timer Display */}
          {!isGeneratingVoice && (
            <div className="glass-card">
            <div className={`w-48 h-48 mx-auto rounded-full bg-gradient-to-r ${selectedTypeData.color} flex items-center justify-center text-white mb-6`}>
              <div className="text-center">
                <div className="text-4xl font-bold">{formatTime(timeLeft)}</div>
                <div className="text-sm opacity-90">{selectedTypeData.name}</div>
              </div>
            </div>

            {/* Controls */}
            <div className="flex justify-center gap-4 mb-6">
              <button
                onClick={pauseMeditation}
                className="p-3 bg-saffron text-white rounded-full hover:bg-saffron/90 transition-colors"
              >
                {isActive ? <Pause size={24} /> : <Play size={24} />}
              </button>
              <button
                onClick={resetMeditation}
                className="p-3 bg-gray-500 text-white rounded-full hover:bg-gray-600 transition-colors"
              >
                <RotateCcw size={24} />
              </button>
            </div>

            {/* Voice Guidance Audio Player */}
            {hasAudio && audioBase64 && (
              <div className="glass-card mb-6">
                <MeditationAudioPlayer
                  audioBase64={audioBase64}
                  isPlaying={isAudioPlaying}
                  onPlayPause={() => setIsAudioPlaying(!isAudioPlaying)}
                  onEnded={() => setIsAudioPlaying(false)}
                  currentPhase={currentPhase}
                  showControls={true}
                  autoPlay={isActive}
                />
              </div>
            )}

            {/* Breathing Animation */}
            {currentPhase === 'breathing' && (
              <div className="glass-card mb-6">
                <BreathingAnimation 
                  isActive={isActive} 
                  pattern={getCurrentBreathingPattern()}
                />
              </div>
            )}

            {/* AI Guidance Text */}
            {!isGeneratingVoice && (
              <div className="glass-card bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-gray-800">
                    {t('meditation.aiGuidance', 'AI Guidance')}
                  </h4>
                  {hasAudio && (
                    <div className="flex items-center text-xs text-green-600">
                      <Volume2 size={14} className="mr-1" />
                      <span>Voice Available</span>
                    </div>
                  )}
                </div>
                <p className="text-gray-700 leading-relaxed">{aiGuidance}</p>
                {!hasAudio && voiceEnabled && (
                  <p className="text-xs text-gray-500 mt-2 italic">
                    Voice guidance temporarily unavailable - using text guidance
                  </p>
                )}
              </div>
            )}
          </div>
          )}
        </motion.div>
      )}

      {currentPhase === 'completion' && (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center space-y-6"
        >
          <div className="glass-card">
            <div className="w-32 h-32 mx-auto rounded-full bg-gradient-to-r from-green-400 to-green-600 flex items-center justify-center text-white mb-6">
              <Heart size={48} />
            </div>
            
            <h3 className="text-2xl font-bold text-gray-800 mb-4">
              {t('meditation.completed', 'Meditation Complete!')}
            </h3>
            
            <div className="glass-card bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 mb-6">
              <p className="text-gray-700 leading-relaxed">{aiGuidance}</p>
            </div>

            <div className="flex justify-center gap-4">
              <button
                onClick={() => {
                  setCurrentPhase('setup')
                  setTimeLeft(0)
                }}
                className="btn-secondary"
              >
                {t('meditation.newSession', 'New Session')}
              </button>
              <button
                onClick={startMeditation}
                className="btn-primary"
              >
                {t('meditation.repeatSession', 'Repeat Session')}
              </button>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  )
}