const API_BASE_URL = 'http://localhost:8000/api/v1'

export const meditationService = {
  // Get personalized meditation guidance
  async getGuidance(type, phase, duration) {
    try {
      const response = await fetch(`${API_BASE_URL}/meditation/guidance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          meditation_type: type,
          phase: phase,
          duration: duration
        })
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      const data = await response.json()
      
      // Log successful guidance retrieval
      console.log(`✅ Meditation guidance received: ${type} - ${phase} (${duration}min)`)
      
      return data
    } catch (error) {
      console.error('❌ Error getting meditation guidance:', error)
      
      // Enhanced fallback guidance based on type and phase
      const fallbackGuidance = {
        setup: {
          mindfulness: "Find a comfortable seated position with your spine straight but relaxed. Close your eyes gently and take three deep breaths. Allow your body to settle and your mind to become present.",
          'loving-kindness': "Sit comfortably and place your hand on your heart. Feel the warmth and rhythm of your heartbeat. Set an intention to cultivate love and compassion for yourself and others.",
          nature: "Imagine yourself in a peaceful natural setting. Feel the earth beneath you and the air around you. Connect with the natural world around you.",
          sleep: "Lie down comfortably and let your body sink into complete relaxation. Release the tensions of the day and prepare for peaceful rest.",
          energy: "Sit tall with your spine straight and shoulders relaxed. Feel the energy flowing through your body and connect with your inner vitality."
        },
        breathing: {
          mindfulness: "Focus on your natural breath without trying to change it. Notice the sensation of air flowing in and out. When your mind wanders, gently return to your breath.",
          'loving-kindness': "Breathe in love and compassion for yourself. With each exhale, release any self-criticism or tension. You are worthy of love and kindness.",
          nature: "Breathe in the fresh, clean air of nature. Imagine breathing in the life force of trees and plants around you.",
          sleep: "Let each exhale release more tension from your body. Feel yourself becoming heavier and more relaxed with each breath.",
          energy: "Breathe in bright, golden energy. Feel it filling your body with vitality and strength."
        },
        meditation: {
          mindfulness: "Rest in the present moment. Notice thoughts and feelings as they arise, without judgment. You are the peaceful observer of your experience.",
          'loving-kindness': "Send loving thoughts first to yourself, then to your loved ones, and finally to all beings everywhere. May all beings be happy and peaceful.",
          nature: "Feel your deep connection to all living things. You are part of the web of life, connected to earth, sky, and all creatures.",
          sleep: "Let go of the day completely. Trust in your body's natural wisdom to restore and heal during sleep.",
          energy: "Feel the energy circulating through your body. You are vibrant, alive, and full of unlimited potential."
        }
      }
      
      const phaseGuidance = fallbackGuidance[phase] || fallbackGuidance.meditation
      const guidance = phaseGuidance[type] || phaseGuidance.mindfulness || 'Focus on your breath and be present in this moment.'
      
      return { 
        guidance,
        meditation_type: type,
        phase: phase,
        duration: duration,
        success: false,
        model_used: 'fallback',
        error: 'Using offline guidance due to connection issue'
      }
    }
  },

  // Save meditation session
  async saveSession(sessionData) {
    try {
      const response = await fetch(`${API_BASE_URL}/meditation/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sessionData)
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      const result = await response.json()
      console.log(`✅ Meditation session saved: ${sessionData.meditation_type} (${sessionData.duration}min)`)
      return result
    } catch (error) {
      console.error('❌ Error saving meditation session:', error)
      
      // Store session locally as fallback
      try {
        const localSessions = JSON.parse(localStorage.getItem('meditation_sessions') || '[]')
        const sessionWithId = {
          ...sessionData,
          id: Date.now(),
          created_at: new Date().toISOString(),
          saved_locally: true
        }
        localSessions.push(sessionWithId)
        localStorage.setItem('meditation_sessions', JSON.stringify(localSessions))
        
        console.log('💾 Session saved locally as fallback')
        return { 
          id: sessionWithId.id, 
          message: 'Session saved locally (offline mode)',
          session: sessionWithId,
          saved_locally: true
        }
      } catch (localError) {
        console.error('❌ Failed to save session locally:', localError)
        return null
      }
    }
  },

  // Get meditation history
  async getHistory() {
    try {
      const response = await fetch(`${API_BASE_URL}/meditation/history`)
      
      if (!response.ok) {
        throw new Error('Failed to get meditation history')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error getting meditation history:', error)
      return []
    }
  },

  // Get meditation recommendations
  async getRecommendations(userPreferences) {
    try {
      const response = await fetch(`${API_BASE_URL}/meditation/recommendations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userPreferences)
      })
      
      if (!response.ok) {
        throw new Error('Failed to get meditation recommendations')
      }
      
      return await response.json()
    } catch (error) {
      console.error('Error getting meditation recommendations:', error)
      return []
    }
  },

  // Get meditation guidance with voice audio
  async getGuidanceWithAudio(type, phase, duration) {
    try {
      const response = await fetch(`${API_BASE_URL}/meditation/guidance/audio`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          meditation_type: type,
          phase: phase,
          duration: duration
        })
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        
        // Parse error details if available
        let errorDetail = errorText
        try {
          const errorJson = JSON.parse(errorText)
          errorDetail = errorJson.detail || errorText
        } catch (e) {
          // Use raw error text if not JSON
        }
        
        throw new Error(`Voice guidance unavailable (${response.status}): ${errorDetail}`)
      }
      
      const data = await response.json()
      
      console.log(`✅ Meditation guidance with audio received: ${type} - ${phase} (${duration}min), Has Audio: ${data.has_audio}`)
      
      return data
    } catch (error) {
      console.error('❌ Error getting meditation guidance with audio:', error)
      
      // For voice-guided meditation, TTS failure is critical - throw error instead of fallback
      throw new Error(`Voice-guided meditation failed: ${error.message}`)
    }
  },

  // Convert text to speech (base64 response)
  async convertTextToSpeech(text, voiceSettings = null, language = 'en') {
    try {
      const response = await fetch(`${API_BASE_URL}/meditation/tts/convert`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          voice_settings: voiceSettings,
          language: language
        })
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      const data = await response.json()
      
      console.log(`✅ Text converted to speech: ${text.length} chars → ${data.audio_base64?.length || 0} audio chars`)
      
      return data
    } catch (error) {
      console.error('❌ Error converting text to speech:', error)
      return {
        success: false,
        error: error.message,
        audio_base64: null
      }
    }
  },

  // Convert text to speech (streaming response like Voice AI Agent)
  async convertTextToSpeechStream(text, language = 'en') {
    try {
      const response = await fetch(`${API_BASE_URL}/meditation/tts/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text,
          language: language
        })
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      // Get the audio blob from streaming response
      const audioBlob = await response.blob()
      
      console.log(`✅ Text converted to speech (streaming): ${text.length} chars → ${audioBlob.size} bytes`)
      
      return {
        success: true,
        audioBlob: audioBlob,
        audioUrl: URL.createObjectURL(audioBlob),
        processing_time_ms: response.headers.get('X-Processing-Time'),
        text_length: response.headers.get('X-Text-Length'),
        language: response.headers.get('X-Language')
      }
    } catch (error) {
      console.error('❌ Error converting text to speech (streaming):', error)
      return {
        success: false,
        error: error.message,
        audioBlob: null,
        audioUrl: null
      }
    }
  },

  // Get available TTS voices
  async getAvailableVoices() {
    try {
      const response = await fetch(`${API_BASE_URL}/meditation/tts/voices`)
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      const data = await response.json()
      
      console.log(`✅ Retrieved ${data.voices?.length || 0} available voices`)
      
      return data
    } catch (error) {
      console.error('❌ Error getting available voices:', error)
      return {
        voices: [],
        success: false,
        error: error.message
      }
    }
  },

  // Update voice settings
  async updateVoiceSettings(settings) {
    try {
      const response = await fetch(`${API_BASE_URL}/meditation/tts/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings)
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      const data = await response.json()
      
      console.log(`✅ Voice settings updated:`, settings)
      
      return data
    } catch (error) {
      console.error('❌ Error updating voice settings:', error)
      return {
        success: false,
        error: error.message
      }
    }
  },

  // Generate complete audio sequence for meditation session
  async generateAudioSequence(meditationType, duration, voiceSettings = null) {
    try {
      const params = new URLSearchParams({
        meditation_type: meditationType,
        duration: duration.toString()
      })
      
      const response = await fetch(`${API_BASE_URL}/meditation/session/audio-sequence?${params}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(voiceSettings || {})
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP ${response.status}: ${errorText}`)
      }
      
      const data = await response.json()
      
      console.log(`✅ Audio sequence generated: ${meditationType} (${duration}min), Phases: ${data.successful_phases}/${data.total_phases}`)
      
      return data
    } catch (error) {
      console.error('❌ Error generating audio sequence:', error)
      return {
        success: false,
        error: error.message,
        audio_sequence: {}
      }
    }
  },

  // Play audio from base64 data
  playAudioFromBase64(audioBase64, onEnded = null) {
    try {
      // Convert base64 to blob
      const byteCharacters = atob(audioBase64)
      const byteNumbers = new Array(byteCharacters.length)
      
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i)
      }
      
      const byteArray = new Uint8Array(byteNumbers)
      const audioBlob = new Blob([byteArray], { type: 'audio/wav' })
      const audioUrl = URL.createObjectURL(audioBlob)
      
      // Create and play audio
      const audio = new Audio(audioUrl)
      
      if (onEnded) {
        audio.addEventListener('ended', onEnded)
      }
      
      // Cleanup URL when audio ends
      audio.addEventListener('ended', () => {
        URL.revokeObjectURL(audioUrl)
      })
      
      audio.play().catch(error => {
        console.error('Audio playback failed:', error)
        URL.revokeObjectURL(audioUrl)
      })
      
      return audio
    } catch (error) {
      console.error('❌ Error playing audio from base64:', error)
      return null
    }
  }
}