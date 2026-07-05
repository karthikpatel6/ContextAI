from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websocket.manager import manager
from jose import jwt, JWTError
from models.message import Message
from database.connection import AsyncSessionLocal
from sqlalchemy import select
from models.user import User
from core.security import SECRET_KEY,ALGORITHM

router = APIRouter()

async def get_user_from_token(token: str) -> User | None:
    """Authenticate WebSocket connection via token in query param."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
    except JWTError:
        return None

@router.websocket("/ws/{chat_id}")
async def worksocket_endpoint(websocket: WebSocket, chat_id: str,token: str):
    user = await get_user_from_token(token)
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return
    
    await manager.connect(websocket, chat_id, user.id)

    try:
        while True:
            data = await websocket.receive_json()
            async with AsyncSessionLocal() as db:
                message = Message(
                    chat_id=chat_id,
                    sender_id=user.id,
                    content=data.get("content"),
                    is_ai_command=data.get("content", "").startswith("@ai")
                )
                db.add(message)
                await db.commit()
                await db.refresh(message)
            
            await manager.broadcast(chat_id,{
                "sender_id": user.id,
                "username": user.username,
                "content": message.content,
                "created_at": message.created_at.isoformat() if message.created_at else None,
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_id)
        pass
    
