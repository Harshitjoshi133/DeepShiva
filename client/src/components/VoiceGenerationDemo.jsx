import { useState } from 'react'
import { Play, Volume2, Loader } from 'lucide-react'
import VoiceGenerationLoader from './VoiceGenerationLoader'

export default function VoiceGenerationDemo() {
  const [isGenerating, setIsGenerating] = useState(false)
  const [voiceReady, setVoiceReady] = useState(false)

  const startGeneration = () => {
    setIsGenerating(true)
    setVoiceReady(false)
    
    // Simulate voice generation (10 seconds)
    setTimeout(() => {
      setIsGenerating(false)
      setVoiceReady(true)
    }, 10000)
  }

  const cancelGeneration = () => {
    setIsGenerating(false)
    setVoiceReady(false)
  }

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <h2 className="text-2xl font-bold text-center text-gray-800">
        Voice Generation Demo
      </h2>

      {!isGenerating && !voiceReady && (
        <button
          onClick={startGeneration}
          className="w-full btn-primary py-4 text-lg font-semibold flex items-center justify-center gap-3"
        >
          <Volume2 size={24} />
          Generate Voice Guidance
        </button>
      )}

      {isGenerating && (
        <VoiceGenerationLoader
          isGenerating={isGenerating}
          currentPhase="setup"
          meditationType="mindfulness"
          onCancel={cancelGeneration}
        />
      )}

      {voiceReady && (
        <div className="glass-card bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 text-center py-6">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Volume2 className="text-green-600" size={32} />
            <h3 className="text-xl font-semibold text-green-700">
              Voice Guidance Ready!
            </h3>
          </div>
          <p className="text-green-600 mb-4">
            Your personalized meditation guidance has been generated.
          </p>
          <div className="flex gap-4 justify-center">
            <button className="btn-primary flex items-center gap-2">
              <Play size={20} />
              Start Meditation
            </button>
            <button 
              onClick={() => setVoiceReady(false)}
              className="btn-secondary"
            >
              Generate New Voice
            </button>
          </div>
        </div>
      )}
    </div>
  )
}