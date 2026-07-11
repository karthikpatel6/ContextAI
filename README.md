# ContextAI — WhatsApp-like Chat App with Embedded AI Agents

A production-grade real-time chat application with embedded AI capabilities, built with FastAPI, LangGraph, WebSockets, PostgreSQL, and React.

## ✨ Features

### 💬 Real-time Chat
- WebSocket-based messaging with instant delivery
- Online/offline status and typing indicators
- Message history with PostgreSQL persistence
- User search and direct chat creation

### 🤖 AI Features
- **`@ai` command** — mention `@ai` in any chat to trigger the AI agent
  - `@ai what's the latest news in AI?` → web search via Tavily
  - `@ai send email to x@gmail.com saying...` → Gmail automation
  - Streaming responses — text appears word by word in real time
- **Reply Suggestions** — click "Suggest Reply" to get 3 AI-generated contextual replies
- **Conversation Health Detection** — detects dying conversations and suggests revival messages

### 🏗️ Technical Highlights
- Multi-tool LangGraph agent with web search and email tools
- Streaming LLM responses via WebSocket
- JWT authentication with bcrypt password hashing
- Async PostgreSQL with SQLAlchemy
- Dockerized with 3 containers (postgres, backend, frontend)

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python 3.12 |
| Real-time | WebSockets |
| Database | PostgreSQL + SQLAlchemy (async) |
| Auth | JWT + bcrypt |
| AI Agent | LangGraph + LangChain |
| LLM | Groq (qwen3.6-27b) |
| Web Search | Tavily |
| Frontend | React + Vite |
| Container | Docker + Docker Compose |

## 🚀 Quick Start

### Prerequisites
- Docker + Docker Compose
- Groq API key (free at console.groq.com)
- Tavily API key (free at app.tavily.com)
- Gmail App Password (for email tool)

### Setup

```bash
git clone https://github.com/yourusername/ContextAI
cd ContextAI
cp backend/.env.example backend/.env
# Fill in your API keys in backend/.env
docker-compose up --build
```

Open `http://localhost` in your browser.

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login, get JWT token |
| GET | `/users/search?q=` | Search users |
| POST | `/chats/direct` | Create direct chat |
| GET | `/chats/` | Get my chats |
| GET | `/chats/{id}/messages` | Get message history |
| POST | `/ai/suggest-replies` | Get AI reply suggestions |
| WS | `/ws/{chat_id}?token=` | WebSocket connection |

## 🔌 WebSocket Events

```json
// Send message
{ "type": "message", "content": "Hello!" }

// Send @ai command
{ "type": "message", "content": "@ai search for latest AI news" }

// Typing indicator
{ "type": "typing", "is_typing": true }
```

## 🗂️ Project Structure