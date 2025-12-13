import { useState, useRef, useEffect } from 'react'
import { Send, Mic, MicOff, Loader2, ArrowLeft, Globe, Menu, X } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { motion, AnimatePresence } from 'framer-motion'
import { useLanguage } from '../contexts/LanguageContext'
import { Link } from 'react-router-dom'

export default function Chat() {
  const { t, language, changeLanguage } = useLanguage()
  
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
  const [showHistory, setShowHistory] = useState(true)
  const [chatHistory, setChatHistory] = useState([])
  const [currentChatId, setCurrentChatId] = useState(null)
  const [showLanguageMenu, setShowLanguageMenu] = useState(false)
  const [showAbout, setShowAbout] = useState(false)
  const [responseTime, setResponseTime] = useState(null)
  const [isInitialLoading, setIsInitialLoading] = useState(true)
  const [userId] = useState('demo-user') // Consistent user ID
  const messagesEndRef = useRef(null)

  const languages = {
    en: 'English',
    hi: 'हिंदी',
    ga: 'गढ़वळी'
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Keyboard shortcut for toggling sidebar
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.ctrlKey && e.key === 'b') {
        e.preventDefault()
        setShowHistory(!showHistory)
      }
      if (e.key === 'Escape' && showHistory) {
        setShowHistory(false)
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [showHistory])

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      const recognitionInstance = new SpeechRecognition()
      
      recognitionInstance.continuous = false
      recognitionInstance.interimResults = true
      recognitionInstance.maxAlternatives = 1
      
      // Set language based on current language
      const langMap = {
        'hi': 'hi-IN',
        'ga': 'hi-IN', // Garhwali uses Hindi recognition
        'en': 'en-US'
      }
      recognitionInstance.lang = langMap[language] || 'en-US'
      
      recognitionInstance.onstart = () => {
        console.log('Speech recognition started')
        setIsListening(true)
      }
      
      recognitionInstance.onresult = (event) => {
        console.log('Speech recognition result:', event)
        let transcript = ''
        
        // Get the final result
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            transcript += event.results[i][0].transcript
          }
        }
        
        if (transcript.trim()) {
          setInput(transcript.trim())
        }
      }
      
      recognitionInstance.onerror = (event) => {
        console.error('Speech recognition error:', event.error)
        setIsListening(false)
        
        // Show user-friendly error message
        if (event.error === 'no-speech') {
          console.log('No speech detected')
        } else if (event.error === 'network') {
          console.log('Network error occurred')
        }
      }
      
      recognitionInstance.onend = () => {
        console.log('Speech recognition ended')
        setIsListening(false)
      }
      
      setRecognition(recognitionInstance)
    }
  }, [language])

  // Load chat history from localStorage and backend
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        // Load from localStorage first for immediate display
        const savedHistory = localStorage.getItem('deepshiva-chat-history')
        if (savedHistory) {
          setChatHistory(JSON.parse(savedHistory))
        }
        
        // Then try to load from backend
        await loadChatSessions()
        
      } catch (error) {
        console.error('Error loading chat history:', error)
      } finally {
        setIsInitialLoading(false)
      }
    }
    
    // Use requestAnimationFrame for smooth transition
    requestAnimationFrame(loadInitialData)
  }, [])

  // Function to load chat sessions from backend
  const loadChatSessions = async () => {
    try {
      const response = await fetch(`/api/v1/chat/sessions/${userId}?limit=20`)
      if (response.ok) {
        const data = await response.json()
        if (data.sessions && data.sessions.length > 0) {
          // Convert backend format to frontend format
          const backendChats = data.sessions.map(session => ({
            id: session.session_id,
            title: session.title,
            messages: [], // We'll load messages when needed
            timestamp: session.last_activity,
            chat_type: session.chat_type,
            message_count: session.message_count,
            chat_id: session.chat_id // Store the actual chat ID
          }))
          
          // Update chat history with backend data
          setChatHistory(backendChats)
          
          // Update localStorage with backend data
          localStorage.setItem('deepshiva-chat-history', JSON.stringify(backendChats))
          
          console.log('Loaded chat sessions:', backendChats.length)
        }
      } else {
        console.log('Failed to load chat sessions:', response.status)
      }
    } catch (backendError) {
      console.log('Backend chat loading failed, using localStorage:', backendError)
    }
  }

  const startVoiceInput = () => {
    if (recognition && !isListening) {
      try {
        recognition.start()
      } catch (error) {
        console.error('Error starting speech recognition:', error)
        setIsListening(false)
      }
    }
  }

  const stopVoiceInput = () => {
    if (recognition && isListening) {
      try {
        recognition.stop()
      } catch (error) {
        console.error('Error stopping speech recognition:', error)
      }
      setIsListening(false)
    }
  }

  // Save current chat to history
  const saveCurrentChat = () => {
    if (messages.length > 0) {
      const chatId = currentChatId || Date.now().toString()
      const chatTitle = messages.find(m => m.role === 'user')?.content.slice(0, 50) + '...' || 'New Chat'
      const chatData = {
        id: chatId,
        title: chatTitle,
        messages: messages,
        timestamp: new Date().toISOString()
      }
      
      const updatedHistory = chatHistory.filter(chat => chat.id !== chatId)
      updatedHistory.unshift(chatData)
      
      // Keep only last 20 chats
      const limitedHistory = updatedHistory.slice(0, 20)
      setChatHistory(limitedHistory)
      localStorage.setItem('deepshiva-chat-history', JSON.stringify(limitedHistory))
      setCurrentChatId(chatId)
    }
  }

  // Load a chat from history
  const loadChat = async (chat) => {
    try {
      setIsLoading(true)
      
      // If chat has messages in localStorage, use them
      if (chat.messages && chat.messages.length > 0) {
        setMessages(chat.messages)
        setCurrentChatId(chat.id)
        return
      }
      
      // Otherwise, try to load from backend
      const response = await fetch(`/api/v1/chat/history/${userId}?limit=50`)
      if (response.ok) {
        const data = await response.json()
        
        // Filter messages for this chat session (approximate matching)
        // Since we don't have perfect session tracking, we'll load recent messages
        const chatMessages = data.messages || []
        
        // Convert backend format to frontend format
        const formattedMessages = []
        chatMessages.forEach(msg => {
          formattedMessages.push({
            role: 'user',
            content: msg.user_message,
            timestamp: msg.timestamp
          })
          if (msg.bot_response) {
            formattedMessages.push({
              role: 'assistant',
              content: msg.bot_response,
              timestamp: msg.timestamp,
              responseTime: msg.response_time ? `${msg.response_time}s` : undefined
            })
          }
        })
        
        setMessages(formattedMessages)
        setCurrentChatId(chat.id)
        
        // Update localStorage with loaded messages
        const updatedChat = { ...chat, messages: formattedMessages }
        const updatedHistory = chatHistory.map(h => h.id === chat.id ? updatedChat : h)
        setChatHistory(updatedHistory)
        localStorage.setItem('deepshiva-chat-history', JSON.stringify(updatedHistory))
      } else {
        // Fallback to localStorage data
        setMessages(chat.messages || [])
        setCurrentChatId(chat.id)
      }
    } catch (error) {
      console.error('Error loading chat:', error)
      // Fallback to localStorage data
      setMessages(chat.messages || [])
      setCurrentChatId(chat.id)
    } finally {
      setIsLoading(false)
    }
  }

  // Start new chat
  const startNewChat = () => {
    saveCurrentChat()
    setMessages([])
    setCurrentChatId(null)
    // Keep sidebar open after starting new chat
  }

  // Delete chat from history
  const deleteChat = (chatId) => {
    const updatedHistory = chatHistory.filter(chat => chat.id !== chatId)
    setChatHistory(updatedHistory)
    localStorage.setItem('deepshiva-chat-history', JSON.stringify(updatedHistory))
    
    if (currentChatId === chatId) {
      setMessages([])
      setCurrentChatId(null)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    const startTime = Date.now()
    
    const newMessages = [...messages, { 
      role: 'user', 
      content: userMessage,
      timestamp: new Date().toISOString()
    }]
    setMessages(newMessages)
    setIsLoading(true)
    setResponseTime(null)

    try {
      const response = await fetch('/api/v1/chat/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userMessage, 
          user_id: userId,
          language: language 
        })
      })
      
      const endTime = Date.now()
      const timeTaken = endTime - startTime
      setResponseTime(timeTaken)
      
      const data = await response.json()
      const finalMessages = [...newMessages, { 
        role: 'assistant', 
        content: data.response,
        timestamp: new Date().toISOString(),
        responseTime: data.processing_time_seconds ? `${data.processing_time_seconds}s` : `${(timeTaken/1000).toFixed(2)}s`
      }]
      setMessages(finalMessages)
      
      // Auto-save after each exchange and refresh chat sessions
      setTimeout(() => {
        saveCurrentChat()
        loadChatSessions() // Refresh the chat list to show new/updated chats
      }, 1000)
    } catch (error) {
      const endTime = Date.now()
      const timeTaken = endTime - startTime
      setResponseTime(timeTaken)
      
      const errorMessages = [...newMessages, { 
        role: 'assistant', 
        content: 'I apologize, but I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
        responseTime: `${(timeTaken/1000).toFixed(2)}s`,
        isError: true
      }]
      setMessages(errorMessages)
    } finally {
      setIsLoading(false)
    }
  }

  // Show loading screen on initial load
  if (isInitialLoading) {
    return (
      <div className="fullscreen-chat">
        <div className="initial-loading-screen">
          <div className="loading-content">
            <div className="loading-icon">
              <div className="shiva-symbol-loading">🕉️</div>
            </div>
            <h2 className="loading-title">Deep-Shiva</h2>
            <p className="loading-subtitle">{t('chat.initializing', 'Initializing your spiritual guide...')}</p>
            <div className="loading-spinner">
              <div className="spinner-ring"></div>
              <div className="spinner-ring"></div>
              <div className="spinner-ring"></div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fullscreen-chat">
      {/* Mobile Overlay */}
      <AnimatePresence mode="wait">
        {showHistory && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ 
              duration: 0.3,
              ease: [0.25, 0.46, 0.45, 0.94]
            }}
            className="sidebar-overlay md:hidden"
            onClick={() => setShowHistory(false)}
          />
        )}
      </AnimatePresence>

      {/* Chat History Sidebar */}
      <AnimatePresence mode="wait">
        {showHistory && (
          <motion.div
            initial={{ x: -320 }}
            animate={{ x: 0 }}
            exit={{ x: -320 }}
            transition={{ 
              type: "tween",
              ease: [0.25, 0.46, 0.45, 0.94],
              duration: 0.3
            }}
            className="chat-history-sidebar"
          >
            <div className="sidebar-header">
              <div className="sidebar-header-top">
                <h3 className="sidebar-title">Deep-Shiva</h3>
                <button 
                  onClick={() => setShowHistory(false)}
                  className="sidebar-close-button"
                  title={t('chat.closeSidebar', 'Close Sidebar')}
                >
                  <X size={18} />
                </button>
              </div>
              <div className="sidebar-tabs">
                <button 
                  onClick={() => setShowAbout(false)}
                  className={`sidebar-tab ${!showAbout ? 'active' : ''}`}
                >
                  {t('chat.chats', 'Chats')}
                </button>
                <button 
                  onClick={() => setShowAbout(true)}
                  className={`sidebar-tab ${showAbout ? 'active' : ''}`}
                >
                  {t('chat.about', 'About')}
                </button>
              </div>
            </div>
            
            {!showAbout ? (
              <div className="chat-history-content">
                <div className="new-chat-section">
                  <button 
                    onClick={startNewChat} 
                    className="new-chat-button"
                  >
                    {t('chat.newChat', 'New Chat')}
                  </button>
                </div>
                <div className="history-section">
                  <h4 className="section-title">{t('chat.recentChats', 'Recent Chats')}</h4>
                  <div className="history-list">
                    {chatHistory.length > 0 ? (
                      chatHistory.map((chat) => (
                        <div key={chat.id} className="history-item">
                          <button
                            onClick={() => loadChat(chat)}
                            className={`history-item-button ${currentChatId === chat.id ? 'active' : ''}`}
                          >
                            <div className="history-item-title">{chat.title}</div>
                            <div className="history-item-date">
                              {new Date(chat.timestamp).toLocaleDateString()}
                            </div>
                          </button>
                          <button
                            onClick={() => deleteChat(chat.id)}
                            className="delete-chat-button"
                            title={t('chat.delete', 'Delete chat')}
                          >
                            <X size={16} />
                          </button>
                        </div>
                      ))
                    ) : (
                      <div className="no-history">
                        <p className="no-history-text">{t('chat.noHistory', 'No chat history yet')}</p>
                        <p className="no-history-subtitle">{t('chat.startChatting', 'Start a conversation to see your chats here')}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="about-content">
                <div className="about-section">
                  <div className="about-icon">🕉️</div>
                  <h3 className="about-title">Deep-Shiva</h3>
                  <p className="about-description">
                    {t('chat.aboutDescription', 'Your AI-powered spiritual guide to Uttarakhand. I can help you plan pilgrimages, find temples, check weather, and discover the rich culture of the Himalayas.')}
                  </p>
                </div>
                
                <div className="features-section">
                  <h4 className="features-title">{t('chat.features', 'Features')}</h4>
                  <ul className="features-list">
                    <li className="feature-item">
                      <span className="feature-icon">🏔️</span>
                      <span>{t('chat.feature1', 'Temple & Pilgrimage Information')}</span>
                    </li>
                    <li className="feature-item">
                      <span className="feature-icon">🌤️</span>
                      <span>{t('chat.feature2', 'Real-time Weather Updates')}</span>
                    </li>
                    <li className="feature-item">
                      <span className="feature-icon">🗺️</span>
                      <span>{t('chat.feature3', 'Route Planning & Navigation')}</span>
                    </li>
                    <li className="feature-item">
                      <span className="feature-icon">🎭</span>
                      <span>{t('chat.feature4', 'Cultural Insights & Traditions')}</span>
                    </li>
                    <li className="feature-item">
                      <span className="feature-icon">🎤</span>
                      <span>{t('chat.feature5', 'Voice Input Support')}</span>
                    </li>
                    <li className="feature-item">
                      <span className="feature-icon">🌐</span>
                      <span>{t('chat.feature6', 'Multi-language Support')}</span>
                    </li>
                  </ul>
                </div>
                
                <div className="stats-section">
                  <h4 className="stats-title">{t('chat.stats', 'Statistics')}</h4>
                  <div className="stats-grid">
                    <div className="stat-item">
                      <div className="stat-number">{chatHistory.length}</div>
                      <div className="stat-label">{t('chat.totalChats', 'Total Chats')}</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-number">{messages.length}</div>
                      <div className="stat-label">{t('chat.currentMessages', 'Current Messages')}</div>
                    </div>
                    {responseTime && (
                      <div className="stat-item">
                        <div className="stat-number">{(responseTime/1000).toFixed(2)}s</div>
                        <div className="stat-label">{t('chat.lastResponseTime', 'Last Response Time')}</div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Chat Container */}
      <motion.div 
        className="chatgpt-fullscreen-container"
        animate={{ 
          marginLeft: showHistory ? 0 : 0,
          opacity: 1 
        }}
        transition={{ 
          duration: 0.3,
          ease: [0.25, 0.46, 0.45, 0.94]
        }}
      >
        {/* Enhanced Top Bar */}
        <div className="chatgpt-topbar">
          <div className="topbar-left">
            <button 
              onClick={() => setShowHistory(!showHistory)}
              className={`sidebar-toggle-button group ${showHistory ? 'active' : ''}`}
              title={`${showHistory ? t('chat.hideSidebar', 'Hide Sidebar') : t('chat.showSidebar', 'Show Sidebar')} (Ctrl+B)`}
            >
              <Menu size={20} />
              {!showHistory && (
                <span className="toggle-hint">Ctrl+B</span>
              )}
            </button>
            <div className="topbar-divider"></div>
            <Link to="/" className="back-button">
              <ArrowLeft size={20} />
              <span className="back-text">{t('chat.backToMenu', 'Back to Menu')}</span>
            </Link>
            <div className="chat-title">
              <div className="title-icon">🕉️</div>
              <h1 className="title-text">{t('chat.title', 'Chat with Deep-Shiva')}</h1>
            </div>
          </div>
          
          <div className="topbar-right">
            <div className="chat-status">
              {currentChatId && (
                <span className="current-chat-indicator">
                  {t('chat.activeChat', 'Active Chat')}
                </span>
              )}
              {responseTime && (
                <span className="response-time-indicator">
                  {(responseTime/1000).toFixed(2)}s
                </span>
              )}
            </div>
            <div className="language-selector">
              <button 
                onClick={() => setShowLanguageMenu(!showLanguageMenu)}
                className="language-button"
              >
                <Globe size={18} />
                <span>{languages[language]}</span>
              </button>
              {showLanguageMenu && (
                <div className="language-dropdown">
                  {Object.entries(languages).map(([code, name]) => (
                    <button
                      key={code}
                      onClick={() => {
                        changeLanguage(code)
                        setShowLanguageMenu(false)
                      }}
                      className={`language-option ${language === code ? 'active' : ''}`}
                    >
                      {name}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
        
        {/* Messages Container */}
        <div className="chatgpt-messages-fullscreen">
          {messages.length === 0 ? (
            /* Welcome Screen */
            <div className="chatgpt-welcome-fullscreen">
              <div className="welcome-content-fullscreen">
                <div className="welcome-icon-fullscreen">
                  <div className="shiva-symbol-fullscreen">🕉️</div>
                </div>
                <h3 className="welcome-title-fullscreen">Deep-Shiva</h3>
                <p className="welcome-subtitle-fullscreen">{getRandomGreeting()}</p>
                <div className="welcome-suggestions-fullscreen">
                  <div className="suggestion-card-fullscreen" onClick={() => setInput(t('chat.suggestion1', 'Tell me about Kedarnath temple'))}>
                    <span>{t('chat.suggestion1', 'Tell me about Kedarnath temple')}</span>
                  </div>
                  <div className="suggestion-card-fullscreen" onClick={() => setInput(t('chat.suggestion2', 'Best time to visit Char Dham'))}>
                    <span>{t('chat.suggestion2', 'Best time to visit Char Dham')}</span>
                  </div>
                  <div className="suggestion-card-fullscreen" onClick={() => setInput(t('chat.suggestion3', 'Weather in Rishikesh today'))}>
                    <span>{t('chat.suggestion3', 'Weather in Rishikesh today')}</span>
                  </div>
                  <div className="suggestion-card-fullscreen" onClick={() => setInput(t('chat.suggestion4', 'Plan a 7-day spiritual journey'))}>
                    <span>{t('chat.suggestion4', 'Plan a 7-day spiritual journey')}</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            /* Chat Messages */
            <div className="chatgpt-conversation-fullscreen">
              <AnimatePresence>
                {messages.map((message, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`message-wrapper-fullscreen ${message.role}`}
                  >
                    <div className="message-content-fullscreen">
                      <div className="message-avatar-fullscreen">
                        {message.role === 'user' ? (
                          <div className="user-avatar">👤</div>
                        ) : (
                          <div className="assistant-avatar">🕉️</div>
                        )}
                      </div>
                      <div className="message-bubble-fullscreen">
                        <div className="message-header-fullscreen">
                          <span className="message-sender">
                            {message.role === 'user' ? t('chat.you', 'You') : 'Deep-Shiva'}
                          </span>
                          <span className="message-time">
                            {message.timestamp ? new Date(message.timestamp).toLocaleTimeString() : ''}
                          </span>
                        </div>
                        <div className="message-text-fullscreen">
                          <ReactMarkdown 
                            className="chatgpt-markdown-fullscreen"
                            components={{
                              a: ({ href, children }) => (
                                <a 
                                  href={href} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="chatgpt-link-fullscreen"
                                >
                                  {children}
                                </a>
                              ),
                              p: ({ children }) => <p className="mb-3">{children}</p>,
                              ul: ({ children }) => <ul className="list-disc ml-4 mb-3">{children}</ul>,
                              ol: ({ children }) => <ol className="list-decimal ml-4 mb-3">{children}</ol>,
                              li: ({ children }) => <li className="mb-1">{children}</li>,
                              code: ({ children }) => <code className="chatgpt-code-fullscreen">{children}</code>,
                              pre: ({ children }) => <pre className="chatgpt-pre-fullscreen">{children}</pre>
                            }}
                          >
                            {message.content}
                          </ReactMarkdown>
                        </div>
                        {message.responseTime && (
                          <div className="message-footer-fullscreen">
                            <span className="response-time">
                              {t('chat.responseTime', 'Response time')}: {message.responseTime}
                            </span>
                            {message.isError && (
                              <span className="error-indicator">⚠️ {t('chat.error', 'Error')}</span>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="message-wrapper-fullscreen assistant"
                >
                  <div className="message-content-fullscreen">
                    <div className="message-avatar-fullscreen">🕉️</div>
                    <div className="message-text-fullscreen">
                      <div className="typing-indicator-fullscreen">
                        <Loader2 className="animate-spin text-saffron mr-2" size={18} />
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
        <div className="chatgpt-input-area-fullscreen">
          {isListening && (
            <div className="voice-indicator">
              <div className="voice-wave">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span className="voice-text">{t('chat.listening', 'Listening...')}</span>
            </div>
          )}
          <form onSubmit={handleSubmit} className="chatgpt-input-form-fullscreen">
            <div className="input-container-fullscreen">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={isListening ? t('chat.listeningPlaceholder', 'Speak now...') : t('chat.placeholder', 'Ask about temples, routes, weather...')}
                className="chatgpt-input-fullscreen"
                disabled={isLoading}
              />
              <div className="input-actions-fullscreen">
                {recognition && (
                  <button
                    type="button"
                    onClick={isListening ? stopVoiceInput : startVoiceInput}
                    className={`voice-button-fullscreen ${isListening ? 'listening' : ''}`}
                    title={isListening ? t('chat.stopVoice', 'Stop voice input') : t('chat.startVoice', 'Start voice input')}
                  >
                    {isListening ? <MicOff size={20} /> : <Mic size={20} />}
                  </button>
                )}
                <button
                  type="submit"
                  disabled={isLoading || !input.trim() || isListening}
                  className="send-button-fullscreen"
                  title={t('chat.send', 'Send message')}
                >
                  {isLoading ? <Loader2 className="animate-spin" size={20} /> : <Send size={20} />}
                </button>
              </div>
            </div>
          </form>
        </div>
      </motion.div>
    </div>
  )
}