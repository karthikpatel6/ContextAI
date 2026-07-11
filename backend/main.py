from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.connection import create_tables
from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.chats import router as chats_router
from websocket.router import router as ws_router
from routers.ai import router as ai_router
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(title="WhatsApp AI",lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost",       # Docker nginx (port 80)
        "http://localhost:80",    # Docker nginx explicit port
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

