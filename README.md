# ContextAI — WhatsApp-like Chat App with Embedded AI Agents

[![CI](https://github.com/karthikpatel6/ContextAI/actions/workflows/ci.yml/badge.svg)](https://github.com/karthikpatel6/ContextAI/actions/workflows/ci.yml)
[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://context-ai-six.vercel.app)

> Built as a portfolio project demonstrating production-grade agentic AI engineering — LangGraph orchestration, real-time WebSockets, and full-stack deployment.

A production-grade real-time chat application with embedded AI capabilities, built with FastAPI, LangGraph, WebSockets, PostgreSQL, and React.

🔗 **Live Demo:** [context-ai-six.vercel.app](https://context-ai-six.vercel.app)

---

## ✨ Features

### 💬 Real-time Chat
- WebSocket-based messaging with instant delivery
- Typing indicators and online/offline status
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
- LangSmith observability for all LLM traces
- Deployed on Render + Vercel + Supabase

---

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
| Observability | LangSmith |
| Deployment | Render + Vercel + Supabase |

---

## 🚀 Quick Start

### Prerequisites
- Docker + Docker Compose
- Groq API key (free at [console.groq.com](https://console.groq.com))
- Tavily API key (free at [app.tavily.com](https://app.tavily.com))
- Gmail App Password (for email tool)

### Setup

```bash
git clone https://github.com/karthikpatel6/ContextAI
cd ContextAI
cp backend/.env.example backend/.env
# Fill in your API keys in backend/.env
docker-compose up --build
```

Open `http://localhost` in your browser.

---

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

---

## 🔌 WebSocket Events

```json
// Send message
{ "type": "message", "content": "Hello!" }

// Send @ai command
{ "type": "message", "content": "@ai search for latest AI news" }

// Typing indicator
{ "type": "typing", "is_typing": true }
```

---

## 🗂️ Project Structure

```
ContextAI/
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   ├── routers/                   # auth, users, chats, ai
│   ├── ws/                        # WebSocket connection manager + router
│   ├── agents/                    # LangGraph agents
│   │   ├── at_ai_agent.py         # @ai command agent
│   │   └── reply_suggester.py     # Reply suggestion agent
│   ├── models/                    # SQLAlchemy models
│   ├── schemas/                   # Pydantic schemas
│   ├── core/                      # security, dependencies
│   └── database/                  # DB connection + session
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── src/
│       ├── api/                   # Axios client
│       ├── context/               # Auth context
│       ├── pages/                 # Login, Register, Chat
│       └── components/            # Sidebar, ChatWindow, etc.
├── docker-compose.yml
├── .gitignore
└── README.md
```

---

## 🌐 Deployment

| Service | Platform |
|---------|----------|
| Frontend | Vercel |
| Backend | Render |
| Database | Supabase (PostgreSQL) |

---

## 📸 Screenshots

> *Add screenshots or demo GIF here*

---

## 🔮 Roadmap

- [ ] Sentiment analysis agent
- [ ] Long-term RAG memory over chat history
- [ ] Group chat support
- [ ] Google Calendar integration
- [ ] Dedicated AI Chat mode
