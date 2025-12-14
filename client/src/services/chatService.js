/**
 * Chat Service - Manages all chat-related API calls to the backend
 * Handles chat sessions, messages, and communication with the backend
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

/**
 * Create a new chat session using the enhanced async endpoint
 * @param {string} userId - The user ID
 * @param {string} language - The current language
 * @returns {Promise<Object>} Response with chat_id and session info
 */
export const createNewChatSession = async (userId, language) => {
  const startTime = Date.now();
  
  try {
    console.log('🆕 Creating new chat session (async):', { 
      userId, 
      language,
      endpoint: '/api/v1/chat/new-session'
    });
    
    const response = await fetch(`${API_BASE_URL}/chat/new-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        user_id: userId,
        language: language 
      })
    });
    
    const responseTime = Date.now() - startTime;
    
    console.log('� NeEw session response:', {
      status: response.status,
      statusText: response.statusText,
      responseTime: `${responseTime}ms`,
      headers: {
        'x-request-id': response.headers.get('x-request-id'),
        'x-response-time': response.headers.get('x-response-time')
      }
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ New session error:', {
        status: response.status,
        statusText: response.statusText,
        errorBody: errorText
      });
      throw new Error(`Failed to create chat session: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    
    console.log('✅ New chat session created successfully:', {
      chatId: data.chat_id,
      sessionId: data.session_id,
      title: data.title,
      processingTime: data.processing_time_ms + 'ms',
      totalTime: `${responseTime}ms`
    });
    
    return data;
  } catch (error) {
    const responseTime = Date.now() - startTime;
    console.error('🚨 Error creating new chat session:', {
      error: error.message,
      responseTime: `${responseTime}ms`,
      endpoint: '/api/v1/chat/new-session'
    });
    throw error;
  }
};

/**
 * Send a chat message using the enhanced async endpoint
 * @param {string} message - The user message
 * @param {string} userId - The user ID
 * @param {string} language - The current language
 * @param {boolean} isNewChat - Whether this is a new chat
 * @returns {Promise<Object>} Response with AI reply and metadata
 */
export const sendChatMessage = async (message, userId, language, isNewChat = false, chatId = null) => {
  const startTime = Date.now();
  
  try {
    console.log('💬 Sending message to async endpoint:', { 
      message: message.substring(0, 50) + '...', 
      userId, 
      language, 
      isNewChat,
      chatId,
      endpoint: '/api/v1/chat/query'
    });
    
    const requestBody = { 
      message: message, 
      user_id: userId,
      language: language,
      is_new_chat: isNewChat
    };
    
    // Add chat_id if provided (ensure it's a string)
    if (chatId) {
      requestBody.chat_id = String(chatId);
    }
    
    const response = await fetch(`${API_BASE_URL}/chat/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody)
    });
    
    const responseTime = Date.now() - startTime;
    
    console.log('📊 Response received:', {
      status: response.status,
      statusText: response.statusText,
      responseTime: `${responseTime}ms`,
      headers: {
        'content-type': response.headers.get('content-type'),
        'x-request-id': response.headers.get('x-request-id'),
        'x-response-time': response.headers.get('x-response-time')
      }
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ API Error Response:', {
        status: response.status,
        statusText: response.statusText,
        errorBody: errorText
      });
      throw new Error(`Failed to send message: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    
    console.log('✅ Message sent successfully:', {
      messageId: data.message_id,
      chatId: data.chat_id,
      requestedChatId: chatId,
      processingTime: data.processing_time_seconds + 's',
      modelUsed: data.model_used,
      responseLength: data.response?.length || 0,
      contextUsed: data.context_used,
      totalTime: `${responseTime}ms`,
      isNewChat: isNewChat,
      userId: userId
    });
    
    return data;
  } catch (error) {
    const responseTime = Date.now() - startTime;
    console.error('🚨 Error sending message:', {
      error: error.message,
      responseTime: `${responseTime}ms`,
      endpoint: '/api/v1/chat/query'
    });
    throw error;
  }
};

/**
 * Load chat sessions for a user
 * @param {string} userId - The user ID
 * @param {number} limit - Maximum number of sessions to load
 * @returns {Promise<Object>} Response with chat sessions
 */
export const loadChatSessions = async (userId, limit = 20) => {
  try {
    console.log('📂 Loading chat sessions for user:', userId, 'limit:', limit);
    
    const response = await fetch(`${API_BASE_URL}/chat/sessions/${userId}?limit=${limit}`);
    
    if (!response.ok) {
      throw new Error(`Failed to load chat sessions: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('✅ Chat sessions loaded:', data.sessions?.length || 0, 'sessions');
    return data;
  } catch (error) {
    console.error('🚨 Error loading chat sessions:', error);
    throw error;
  }
};

/**
 * Load messages for a specific chat
 * @param {string} chatId - The chat ID
 * @param {string} userId - The user ID
 * @param {number} limit - Maximum number of messages to load
 * @returns {Promise<Object>} Response with chat messages
 */
export const loadChatMessages = async (chatId, userId, limit = 100) => {
  try {
    console.log('📨 Loading messages for chat:', chatId, 'user:', userId, 'limit:', limit);
    
    const response = await fetch(`${API_BASE_URL}/chat/messages/${chatId}?user_id=${userId}&limit=${limit}`);
    
    if (!response.ok) {
      throw new Error(`Failed to load chat messages: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('✅ Chat messages loaded:', data.messages?.length || 0, 'messages');
    return data;
  } catch (error) {
    console.error('🚨 Error loading chat messages:', error);
    throw error;
  }
};

/**
 * Format backend chat sessions for frontend use
 * @param {Array} sessions - Raw sessions from backend
 * @returns {Array} Formatted chat sessions
 */
export const formatChatSessions = (sessions) => {
  if (!sessions || !Array.isArray(sessions)) {
    return [];
  }
  
  return sessions.map(session => {
    console.log('💾 Processing session from DB:', {
      session_id: session.session_id,
      chat_id: session.chat_id,
      title: session.title,
      message_count: session.message_count,
      chat_type: session.chat_type,
      last_activity: session.last_activity
    });
    
    return {
      id: session.chat_id, // Use actual database chat_id as the primary ID
      session_id: session.session_id, // Keep session_id separate
      title: session.title || 'Untitled Chat',
      messages: [], // We'll load messages when needed
      timestamp: session.last_activity,
      chat_type: session.chat_type || 'general',
      message_count: session.message_count || 0,
      chat_id: session.chat_id, // Store the actual chat ID for reference
      user_rating: session.user_rating,
      tags: session.tags || [],
      is_favorite: session.is_favorite || false,
      created_at: session.created_at,
      chat_metadata: session.chat_metadata || {}
    };
  });
};

/**
 * Format backend messages for frontend use
 * @param {Array} messages - Raw messages from backend
 * @returns {Array} Formatted messages
 */
export const formatChatMessages = (messages) => {
  if (!messages || !Array.isArray(messages)) {
    return [];
  }
  
  return messages.map(msg => ({
    role: msg.role,
    content: msg.content,
    timestamp: msg.timestamp,
    responseTime: msg.response_time,
    message_id: msg.message_id,
    ai_model: msg.ai_model,
    tokens_used: msg.tokens_used,
    confidence_score: msg.confidence_score,
    context_data: msg.context_data
  }));
};

/**
 * Check database status and performance
 * @returns {Promise<Object>} Database status and performance metrics
 */
export const checkDatabaseStatus = async () => {
  const startTime = Date.now();
  
  try {
    console.log('🔍 Checking database status...');
    
    const response = await fetch(`${API_BASE_URL}/chat/database-status`);
    const responseTime = Date.now() - startTime;
    
    console.log('📊 Database status response:', {
      status: response.status,
      responseTime: `${responseTime}ms`
    });
    
    if (!response.ok) {
      throw new Error(`Database status check failed: ${response.status}`);
    }
    
    const data = await response.json();
    
    console.log('✅ Database status:', {
      status: data.status,
      asyncDbStatus: data.async_database?.status,
      connectionTime: data.async_database?.connection_time_ms + 'ms',
      performanceRating: data.async_database?.performance_rating
    });
    
    return data;
  } catch (error) {
    const responseTime = Date.now() - startTime;
    console.error('🚨 Database status check failed:', {
      error: error.message,
      responseTime: `${responseTime}ms`
    });
    throw error;
  }
};

// Export default object with all functions
export default {
  createNewChatSession,
  sendChatMessage,
  loadChatSessions,
  loadChatMessages,
  formatChatSessions,
  formatChatMessages,
  checkDatabaseStatus
};