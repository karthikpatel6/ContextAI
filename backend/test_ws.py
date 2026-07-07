import  asyncio
import websockets
import json

async def test():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI3ZjhiM2I4ZS0xMGRiLTQxZTMtYjJlNC01MDY4MzQ3M2Y1NmQiLCJleHAiOjE3ODM5MzYyMDZ9.zM0AiqxR97adAB6ljRErSepZhM8ejdQrqs8ncC7DEEA"
    chat_id = "fbafbc54-454d-4bd5-9fec-5ca9a7b63915"

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