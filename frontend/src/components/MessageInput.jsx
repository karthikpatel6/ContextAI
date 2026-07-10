import { useState } from 'react'
import './MessageInput.css'

export default function MessageInput({ onSend, onTyping }) {
  const [message, setMessage] = useState('')

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleSend = () => {
    if (!message.trim()) return
    onSend(message.trim())
    setMessage('')
    onTyping(false)
  }

  const handleChange = (e) => {
    const nextValue = e.target.value
    setMessage(nextValue)
    onTyping(nextValue.length > 0)
  }

  const isAiCommand = message.startsWith('@ai')

  return (
    <div className="message-input-container">
      {isAiCommand && (
        <div className="ai-command-hint">
          ✦ AI command — press Enter to ask
        </div>
      )}
      <div className="message-input-box">
        <textarea
          className={`message-textarea ${isAiCommand ? 'ai-mode' : ''}`}
          placeholder="Type a message... or @ai to ask anything"
          value={message}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          rows={1}
        />
        <button
          className={`send-btn ${message.trim() ? 'active' : ''}`}
          onClick={handleSend}
          disabled={!message.trim()}
        >
          ↑
        </button>
      </div>
    </div>
  )
}
