from fastapi import FastAPI

app = FastAPI(title="WhatsApp AI")

@app.get('/')
async def root():
    return {"message": "WhatsApp AI is Running"}