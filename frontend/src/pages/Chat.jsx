import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/axios'
import { useAuth } from '../context/AuthContext'
import Sidebar from '../components/Sidebar'
import ChatWindow from '../components/ChatWindow'
import MessageInput from '../components/MessageInput'
import AISuggestions from '../components/AISuggestions'
import './Chat.css'

export default function Chat() {
  const { user, token, logout } = useAuth()
  const navigate = useNavigate()
  const [chats, setChats] = useState([])
  const [selectedChat, setSelectedChat] = useState(null)
  const [messages, setMessages] = useState([])
  const [isTyping, setIsTyping] = useState(false)
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [suggestions, setSuggestions] = useState([])
  const [suggestionHealth, setSuggestionHealth] = useState('healthy')
  const [revivalMessage, setRevivalMessage] = useState(null)
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  const [inputMessage, setInputMessage] = useState('')
  const [typingUserId, setTypingUserId] = useState(null)
  const wsRef = useRef(null)

  useEffect(() => {
    if (!token) { navigate('/login'); return }
    fetchChats()
  }, [token])

  useEffect(() => {
  if (!selectedChat) return
  fetchMessages(selectedChat.id)
  connectWebSocket(selectedChat.id)
  
  return () => {
    if (wsRef.current) {
      wsRef.current.onclose = null
      wsRef.current.close()
    }
  }
}, [selectedChat])

  const fetchChats = async () => {
    try {
      const res = await api.get('/chats/')
      setChats(res.data)
    } catch (err) {
      if (err.response?.status === 401) logout()
    }
  }

  const fetchMessages = async (chatId) => {
    try {
      const res = await api.get(`/chats/${chatId}/messages`)
      setMessages(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const connectWebSocket = (chatId) => {
  if (wsRef.current) {
    wsRef.current.onclose = null  // prevent cleanup trigger
    wsRef.current.close()
  }
  
  const ws = new WebSocket(`ws://127.0.0.1:8000/ws/${chatId}?token=${token}`)

  ws.onopen = () => {
    console.log('WebSocket connected')
    wsRef.current = ws
  }

  ws.onmessage = (e) => {
    const data = JSON.parse(e.data)

    if (data.type === 'typing') {
      if (data.user_id !== user?.id) {
        setIsTyping(data.is_typing)
        setTypingUserId(data.is_typing ? data.user_id : null)
      }
      return
    }

    if (data.type === 'stream_chunk') {
      setMessages(prev => {
        const last = prev[prev.length - 1]
        if (last?.sender_id === 'ai-assistant') {
          return [...prev.slice(0, -1), { ...last, content: data.content }]
        }
        return [...prev, data]
      })
      return
    }

    if (data.sender_id) {
      setMessages(prev => [...prev, data])
    }
  }

  ws.onclose = () => console.log('WebSocket disconnected')
  ws.onerror = (e) => console.error('WebSocket error', e)
}

const sendMessage = (content) => {
  const ws = wsRef.current
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    console.error('WebSocket not open, state:', ws?.readyState)
    return
  }
  ws.send(JSON.stringify({ type: 'message', content }))
}
  const handleTyping = (isTypingNow) => {
    wsRef.current?.send(JSON.stringify({ type: 'typing', is_typing: isTypingNow }))
  }

  const handleSelectChat = (chat) => {
    setSelectedChat(chat)
    setMessages([])
    setShowSuggestions(false)
    setIsTyping(false)
    setTypingUserId(null)
  }

  const handleNewChat = (chat) => {
    setChats(prev => {
      const exists = prev.find(c => c.id === chat.id)
      if (exists) return prev
      return [chat, ...prev]
    })
    setSelectedChat(chat)
  }

  const fetchSuggestions = async () => {
    if (!selectedChat) return
    setShowSuggestions(true)
    setLoadingSuggestions(true)
    try {
      const res = await api.get(`/ai/suggest-replies?chat_id=${selectedChat.id}`)
      setSuggestions(res.data.suggestions)
      setSuggestionHealth(res.data.conversation_health)
      setRevivalMessage(res.data.revival_message)
    } catch (err) {
      console.error(err)
    } finally {
      setLoadingSuggestions(false)
    }
  }

  const handleSelectSuggestion = (text) => {
    sendMessage(text)
    setShowSuggestions(false)
  }

  return (
    <div className="chat-page">
      <Sidebar
        chats={chats}
        selectedChat={selectedChat}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
      />

      <div className="chat-main">
        {!selectedChat ? (
          <div className="no-chat-selected">
            <div className="no-chat-icon">✦</div>
            <h2>Welcome to ContextAI</h2>
            <p>Select a chat or search for a user to start messaging</p>
            <div className="feature-hints">
              <div className="hint">💬 Real-time messaging</div>
              <div className="hint">✦ @ai for AI assistance</div>
              <div className="hint">🤖 Smart reply suggestions</div>
            </div>
          </div>
        ) : (
          <>
            <div className="chat-header">
              <div className="chat-header-info">
                <div className="avatar">{selectedChat.id.charAt(0).toUpperCase()}</div>
                <div>
                  <p className="chat-header-name">Chat {selectedChat.id.slice(0, 8)}...</p>
                  <p className="chat-header-status">Active now</p>
                </div>
              </div>
              <button
                className="suggest-btn"
                onClick={fetchSuggestions}
                title="Get AI reply suggestions"
              >
                ✦ Suggest Reply
              </button>
            </div>

            <ChatWindow messages={messages} isTyping={isTyping} typingUserId={typingUserId} />

            {showSuggestions && (
              <AISuggestions
                suggestions={suggestions}
                health={suggestionHealth}
                revivalMessage={revivalMessage}
                onSelect={handleSelectSuggestion}
                onClose={() => setShowSuggestions(false)}
                loading={loadingSuggestions}
              />
            )}

            <MessageInput onSend={sendMessage} onTyping={handleTyping} />
          </>
        )}
      </div>
    </div>
  )
}
