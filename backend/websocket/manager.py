from fastapi import WebSocket
from collections import defaultdict

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = defaultdict(list)

    async def connect(self, websocket: WebSocket, chat_id: str, user_id: str):
        await websocket.accept()
        self.active_connections[chat_id].append((websocket, user_id))

    def disconnect(self, websocket: WebSocket, chat_id: str):
        self.active_connections[chat_id] = [
            (ws, uid) for ws, uid in self.active_connections[chat_id]
            if ws != websocket
        ]

    async def broadcast(self, chat_id: str, message: dict):
        
        for ws, uid in self.active_connections[chat_id]:
            await ws.send_json(message)

manager = ConnectionManager()