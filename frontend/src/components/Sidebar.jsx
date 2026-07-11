import { useState } from 'react'
import api from '../api/axios'
import { useAuth } from '../context/AuthContext'
import './Sidebar.css'

export default function Sidebar({ chats, selectedChat, onSelectChat, onNewChat }) {
  const { user, logout } = useAuth()
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])

  const handleSearch = async (e) => {
    const q = e.target.value
    setSearchQuery(q)
    if (q.length < 2) {
      setSearchResults([])
      return
    }
    try {
      const res = await api.get(`/users/search?q=${q}`)
      setSearchResults(res.data)
    } catch (err) {
      console.error(err)
    }
  }

  const startChat = async (targetUser) => {
    try {
      const res = await api.post('/chats/direct', { target_user_id: targetUser.id })
      const chatWithContact = { ...res.data, contact: targetUser }
      onNewChat(chatWithContact)
      setSearchQuery('')
      setSearchResults([])
    } catch (err) {
      console.error(err)
    }
  }

  const getInitial = (name) => name?.charAt(0).toUpperCase() || '?'

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-user">
          <div className="avatar">{getInitial(user?.full_name)}</div>
          <div className="sidebar-user-info">
            <span className="sidebar-username">{user?.full_name}</span>
            <span className="sidebar-handle">@{user?.username}</span>
          </div>
        </div>
        <button className="logout-btn" onClick={logout} title="Logout">⏻</button>
      </div>

      <div className="sidebar-search">
        <input
          type="text"
          placeholder="Search users to chat..."
          value={searchQuery}
          onChange={handleSearch}
        />
      </div>

      {searchResults.length > 0 && (
        <div className="search-results">
          <p className="search-label">Start a new chat</p>
          {searchResults.map(u => (
            <div key={u.id} className="search-result-item" onClick={() => startChat(u)}>
              <div className="avatar avatar-sm">{getInitial(u.full_name)}</div>
              <div>
                <p className="result-name">{u.full_name}</p>
                <p className="result-handle">@{u.username}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      <div className="chat-list">
        <p className="chat-list-label">Recent Chats</p>
        {chats.length === 0 && (
          <div className="empty-chats">
            <p>No chats yet</p>
            <span>Search for a user to start chatting</span>
          </div>
        )}
        {chats.map(chat => (
          <div
            key={chat.id}
            className={`chat-item ${selectedChat?.id === chat.id ? 'active' : ''}`}
            onClick={() => onSelectChat(chat)}
          >
            <div className="avatar">
              {getInitial(chat.contact?.full_name || 'C')}
            </div>
            <div className="chat-item-info">
              <p className="chat-item-name">
                {chat.contact?.full_name || `Chat ${chat.id.slice(0, 8)}...`}
              </p>
              <p className="chat-item-preview">
                @{chat.contact?.username || 'unknown'}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}