import  asyncio
import websockets
import json

async def test():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NzZkOTI5OC1jZjhmLTQyMGItYjQ2Zi05Mzg4NTcyYjNiNGUiLCJleHAiOjE3ODQzNzQyMTB9.rQrDYUKBNdh6a5PtwR1hi7Qr3rFK4iOAKXUUliIgBzs"
    chat_id = "a12bb13c-f26c-4b66-8db0-1f5c021723ff"

    uri = f"ws://127.0.0.1:8000/ws/{chat_id}?token={token}"

    async with websockets.connect(uri) as ws:
        print("Connected!")

        await ws.send(json.dumps({"content": "@ai what is the latest news in AI today?"}))
        print("Message sent!")

        response1 = await ws.recv()
        print("Broadcast:", response1)

        response2 = await ws.recv()
        print("AI Response:", response2)

asyncio.run(test())