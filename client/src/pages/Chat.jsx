import { useState, useRef, useEffect } from 'react'
import { Send, Mic, Loader2 } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { motion, AnimatePresence } from 'framer-motion'

export default function Chat() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Namaste! I am Deep-Shiva, your guide to Uttarakhand. How can I help you plan your spiritual journey today?' }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

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
        body: JSON.stringify({ message: userMessage, user_id: 'demo-user' })
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
    <div className="max-w-4xl mx-auto h-[calc(100vh-180px)] flex flex-col">
      <div className="glass-card flex-1 overflow-hidden flex flex-col mb-3 shadow-2xl">
        <h2 className="text-xl font-bold gradient-text mb-3 pb-3 border-b border-white/20">Chat with Deep-Shiva</h2>
        
        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-3 mb-3 pr-2">
          <AnimatePresence>
            {messages.map((message, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-[80%] rounded-lg p-3 backdrop-blur-sm ${
                  message.role === 'user' 
                    ? 'bg-gradient-to-r from-saffron to-orange-500 text-white shadow-lg' 
                    : 'bg-white/80 text-gray-800 border border-white/20 shadow-md'
                }`}>
                  <ReactMarkdown className="prose prose-sm max-w-none">
                    {message.content}
                  </ReactMarkdown>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          
          {isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="bg-white/80 backdrop-blur-sm rounded-lg p-4 flex items-center gap-2 border border-white/20 shadow-md">
                <Loader2 className="animate-spin text-saffron" size={20} />
                <span className="text-gray-600">Deep-Shiva is thinking...</span>
              </div>
            </motion.div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="flex gap-2 pt-3 border-t">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about temples, routes, weather..."
            className="flex-1 px-3 py-2 border-2 border-gray-300 rounded-lg focus:outline-none focus:border-saffron"
            disabled={isLoading}
          />
          <button
            type="button"
            className="p-2 bg-forest text-white rounded-lg hover:bg-green-700 transition-colors"
            title="Voice input (coming soon)"
          >
            <Mic size={24} />
          </button>
          <button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="p-2 bg-saffron text-white rounded-lg hover:bg-orange-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={24} />
          </button>
        </form>
      </div>
    </div>
  )
}
