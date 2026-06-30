from fastapi import FastAPI
from contextlib import asynccontextmanager
from database.connection import create_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield

app = FastAPI(title="WhatsApp AI",lifespan=lifespan)

@app.get('/')
async def root():
    return {"message": "WhatsApp AI is Running"}

