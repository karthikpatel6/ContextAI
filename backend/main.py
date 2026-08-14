from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.connection import create_tables
from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.chats import router as chats_router
from ws.router import router as ws_router
from routers.ai import router as ai_router
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
load_dotenv()

# LangSmith observability
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "ContextAI")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(title="WhatsApp AI",lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost",
        "http://localhost:80",
        "https://context-ai-six.vercel.app",
        "https://contextai-backend-aoy4.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chats_router)
app.include_router(ws_router)
app.include_router(ai_router)


@app.get('/')
async def root():
    return {"message": "WhatsApp AI is Running"}

@app.get('/health')
async def health():
    return {"status": "healthy"}
