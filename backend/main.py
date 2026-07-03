from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.connection import create_tables
from routers.auth import router as auth_router
from routers.users import router as users_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(title="WhatsApp AI",lifespan=lifespan)

app.include_router(auth_router)
app.include_router(users_router)

@app.get('/')
async def root():
    return {"message": "WhatsApp AI is Running"}

