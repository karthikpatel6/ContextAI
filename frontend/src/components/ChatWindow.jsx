import { useEffect, useRef } from 'react'
import { useAuth } from '../context/AuthContext'
import './ChatWindow.css'

export default function ChatWindow({ messages, isTyping, typingUserId }) {
  const { user } = useAuth()
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const formatTime = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  // Normalize id comparisons to avoid string/number mismatches
  const isMe = (senderId) => String(senderId) === String(user?.id)
  const isAI = (senderId) => String(senderId) === 'ai-assistant'
  const shouldShowTyping = Boolean(isTyping && typingUserId && typingUserId !== user?.id)

  return (
    <div className="chat-window">
      {messages.length === 0 && (
        <div className="chat-empty">
          <div className="chat-empty-icon">✦</div>
          <p>No messages yet</p>
          <span>Send a message or try <code>@ai ask me anything</code></span>
        </div>
      )}

      {messages.map((msg, i) => {
        const me = isMe(msg.sender_id)
        const ai = isAI(msg.sender_id)
        return (
          <div
            key={msg.id || i}
            className={`message-wrapper ${me ? 'me' : ai ? 'ai' : 'them'}`}
          >
            {ai && (
              <div className="ai-badge">✦ AI</div>
            )}
            <div className={`message-bubble ${me ? 'bubble-me' : ai ? 'bubble-ai' : 'bubble-them'}`}>
              <p className="message-content">{msg.content}</p>
              <span className="message-time">{formatTime(msg.created_at)}</span>
            </div>
          </div>
        )
      })}

      {shouldShowTyping && (
        <div className="message-wrapper them">
          <div className="message-bubble bubble-them typing-bubble">
            <span className="typing-dot" />
            <span className="typing-dot" />
            <span className="typing-dot" />
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  )
}
