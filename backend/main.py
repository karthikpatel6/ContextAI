from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.connection import create_tables
from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.chats import router as chats_router
from websocket.router import router as ws_router
from routers.ai import router as ai_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(title="WhatsApp AI",lifespan=lifespan)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(chats_router)
app.include_router(ws_router)
app.include_router(ai_router)

@app.get('/')
async def root():
    return {"message": "WhatsApp AI is Running"}

