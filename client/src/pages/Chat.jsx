import { useState, useRef, useEffect } from 'react'
import { Send, Mic, MicOff, Loader2, ArrowLeft, Globe, Menu } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { motion, AnimatePresence } from 'framer-motion'
import { useLanguage } from '../contexts/LanguageContext'
import { Link } from 'react-router-dom'

export default function Chat() {
  const { t, language } = useLanguage()
  
  const getRandomGreeting = () => {
    const greetings = {
      en: [
        'Namaste! I am Deep-Shiva, your guide to Uttarakhand. How can I help you plan your spiritual journey today?',
        'Welcome, traveler! I\'m Deep-Shiva, ready to guide you through the sacred lands of Uttarakhand. What would you like to explore?',
        'Har Har Mahadev! I\'m Deep-Shiva, your spiritual companion for Uttarakhand. How may I assist your divine journey?',
        'Greetings! I\'m Deep-Shiva, here to help you discover the mystical beauty of Uttarakhand. What brings you here today?',
        'Om Namah Shivaya! I\'m Deep-Shiva, your trusted guide to the Himalayas. Ready to embark on a spiritual adventure?'
      ],
      hi: [
        'नमस्ते! मैं दीप-शिव हूं, उत्तराखंड का आपका गाइड। आज मैं आपकी आध्यात्मिक यात्रा की योजना बनाने में कैसे मदद कर सकता हूं?',
        'स्वागत है यात्री! मैं दीप-शिव हूं, उत्तराखंड की पवित्र भूमि में आपका मार्गदर्शन करने के लिए तैयार हूं। आप क्या खोजना चाहते हैं?',
        'हर हर महादेव! मैं दीप-शिव हूं, उत्तराखंड के लिए आपका आध्यात्मिक साथी। मैं आपकी दिव्य यात्रा में कैसे सहायता कर सकता हूं?',
        'नमस्कार! मैं दीप-शिव हूं, उत्तराखंड की रहस्यमय सुंदरता खोजने में आपकी मदद करने के लिए यहां हूं। आज आपको यहां क्या लाया है?',
        'ॐ नमः शिवाय! मैं दीप-शिव हूं, हिमालय का आपका विश्वसनीय गाइड। आध्यात्मिक साहसिक यात्रा शुरू करने के लिए तैयार हैं?'
      ],
      ga: [
        'जय भोले की! मैं दीप-शिव हूं, उत्तराखंड का तुम्हारा गाइड। आज मैं तुम्हारी आध्यात्मिक यात्रा की योजना में कैसे मदद कर सकता हूं?',
        'स्वागत छ यात्री! मैं दीप-शिव हूं, उत्तराखंड की पवित्र धरती में तुम्हारा मार्गदर्शन करने को तैयार हूं। तुम क्या खोजना चाहते हो?',
        'हर हर भोलेनाथ! मैं दीप-शिव हूं, उत्तराखंड के लिए तुम्हारा आध्यात्मिक साथी। मैं तुम्हारी दिव्य यात्रा में कैसे मदद कर सकता हूं?',
        'नमस्कार! मैं दीप-शिव हूं, उत्तराखंड की रहस्यमय सुंदरता खोजने में तुम्हारी मदद करने यहां हूं। आज तुमको यहां क्या लाया है?',
        'ॐ नमः शिवाय! मैं दीप-शिव हूं, हिमालय का तुम्हारा भरोसेमंद गाइड। आध्यात्मिक रोमांच शुरू करने को तैयार हो?'
      ]
    }
    
    const languageGreetings = greetings[language] || greetings.en
    return languageGreetings[Math.floor(Math.random() * languageGreetings.length)]
  }

  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isListening, setIsListening] = useState(false)
  const [recognition, setRecognition] = useState(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      const recognitionInstance = new SpeechRecognition()
      
      recognitionInstance.continuous = false
      recognitionInstance.interimResults = false
      recognitionInstance.lang = language === 'hi' ? 'hi-IN' : language === 'ga' ? 'hi-IN' : 'en-US'
      
      recognitionInstance.onstart = () => {
        setIsListening(true)
      }
      
      recognitionInstance.onresult = (event) => {
        const transcript = event.results[0][0].transcript
        setInput(transcript)
        setIsListening(false)
      }
      
      recognitionInstance.onerror = () => {
        setIsListening(false)
      }
      
      recognitionInstance.onend = () => {
        setIsListening(false)
      }
      
      setRecognition(recognitionInstance)
    }
  }, [language])

  const startVoiceInput = () => {
    if (recognition && !isListening) {
      recognition.start()
    }
  }

  const stopVoiceInput = () => {
    if (recognition && isListening) {
      recognition.stop()
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await fetch('/api/v1/chat/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userMessage, 
          user_id: 'demo-user',
          language: language 
        })
      })
      
      const data = await response.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
    } catch (error) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'I apologize, but I encountered an error. Please try again.' 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="w-full max-w-6xl mx-auto h-[calc(100vh-120px)] flex flex-col">
      <div className="chatgpt-container flex-1 overflow-hidden flex flex-col shadow-2xl">
        {/* Header */}
        <div className="chatgpt-header">
          <h2 className="text-xl font-bold gradient-text">{t('chat.title', 'Chat with Deep-Shiva')}</h2>
        </div>
        
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto chatgpt-messages">
          {messages.length === 0 ? (
            /* Welcome Screen */
            <div className="chatgpt-welcome">
              <div className="welcome-content">
                <div className="welcome-icon">
                  <div className="shiva-symbol">🕉️</div>
                </div>
                <h3 className="welcome-title gradient-text">Deep-Shiva</h3>
                <p className="welcome-subtitle">{getRandomGreeting()}</p>
                <div className="welcome-suggestions">
                  <div className="suggestion-card" onClick={() => setInput(t('chat.suggestion1', 'Tell me about Kedarnath temple'))}>
                    <span>{t('chat.suggestion1', 'Tell me about Kedarnath temple')}</span>
                  </div>
                  <div className="suggestion-card" onClick={() => setInput(t('chat.suggestion2', 'Best time to visit Char Dham'))}>
                    <span>{t('chat.suggestion2', 'Best time to visit Char Dham')}</span>
                  </div>
                  <div className="suggestion-card" onClick={() => setInput(t('chat.suggestion3', 'Weather in Rishikesh today'))}>
                    <span>{t('chat.suggestion3', 'Weather in Rishikesh today')}</span>
                  </div>
                  <div className="suggestion-card" onClick={() => setInput(t('chat.suggestion4', 'Plan a 7-day spiritual journey'))}>
                    <span>{t('chat.suggestion4', 'Plan a 7-day spiritual journey')}</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Chat Messages */
            <div className="chatgpt-conversation">
              <AnimatePresence>
                {messages.map((message, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`message-wrapper ${message.role}`}
                  >
                    <div className="message-content">
                      <div className="message-avatar">
                        {message.role === 'user' ? '👤' : '🕉️'}
                      </div>
                      <div className="message-text">
                        <ReactMarkdown 
                          className="chatgpt-markdown"
                          components={{
                            a: ({ href, children }) => (
                              <a 
                                href={href} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="chatgpt-link"
                              >
                                {children}
                              </a>
                            ),
                            p: ({ children }) => <p className="mb-2">{children}</p>,
                            ul: ({ children }) => <ul className="list-disc ml-4 mb-2">{children}</ul>,
                            ol: ({ children }) => <ol className="list-decimal ml-4 mb-2">{children}</ol>,
                            li: ({ children }) => <li className="mb-1">{children}</li>,
                            code: ({ children }) => <code className="chatgpt-code">{children}</code>,
                            pre: ({ children }) => <pre className="chatgpt-pre">{children}</pre>
                          }}
                        >
                          {message.content}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="message-wrapper assistant"
                >
                  <div className="message-content">
                    <div className="message-avatar">🕉️</div>
                    <div className="message-text">
                      <div className="typing-indicator">
                        <Loader2 className="animate-spin text-saffron mr-2" size={16} />
                        <span>{t('chat.thinking', 'Deep-Shiva is thinking...')}</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="chatgpt-input-area">
          <form onSubmit={handleSubmit} className="chatgpt-input-form">
            <div className="input-container">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={t('chat.placeholder', 'Ask about temples, routes, weather...')}
                className="chatgpt-input"
                disabled={isLoading || isListening}
              />
              <div className="input-actions">
                <button
                  type="button"
                  onClick={isListening ? stopVoiceInput : startVoiceInput}
                  className={`voice-button ${isListening ? 'listening' : ''}`}
                  title={isListening ? t('chat.stopVoice', 'Stop voice input') : t('chat.startVoice', 'Start voice input')}
                  disabled={!recognition}
                >
                  {isListening ? <MicOff size={18} /> : <Mic size={18} />}
                </button>
                <button
                  type="submit"
                  disabled={isLoading || !input.trim() || isListening}
                  className="send-button"
                  title={t('chat.send', 'Send message')}
                >
                  <Send size={18} />
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}
