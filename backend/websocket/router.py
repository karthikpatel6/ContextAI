from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websocket.manager import manager
from jose import jwt, JWTError
from models.message import Message
from database.connection import AsyncSessionLocal
from sqlalchemy import select
from models.user import User
from core.security import SECRET_KEY, ALGORITHM
from agents.at_ai_agent import run_agent, run_agent_stream

router = APIRouter()

async def get_user_from_token(token: str) -> User | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
    except JWTError:
        return None

@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str, token: str):
    user = await get_user_from_token(token)
    if not user:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await manager.connect(websocket, chat_id, user.id)

    try:
        while True:
            data = await websocket.receive_json()

            # handle typing events
            if data.get("type") == "typing":
                await manager.broadcast(chat_id, {
                    "type": "typing",
                    "user_id": user.id,
                    "is_typing": data.get("is_typing", False),
                })
                continue

            # get content
            content = data.get("content", "").strip()
            if not content:
                continue

            # save message to DB
            async with AsyncSessionLocal() as db:
                message = Message(
                    chat_id=chat_id,
                    sender_id=user.id,
                    content=content,
                    is_ai_command=content.startswith("@ai")
                )
                db.add(message)
                await db.commit()
                await db.refresh(message)

            # broadcast to chat
            await manager.broadcast(chat_id, {
                "sender_id": user.id,
                "username": user.username,
                "content": message.content,
                "created_at": message.created_at.isoformat() if message.created_at else None,
            })

            # handle @ai command
            if message.is_ai_command:
                query = content[3:].strip()

                needs_search = any(kw in query.lower() for kw in [
                    "search", "news", "weather", "latest", "current",
                    "today", "find", "who is", "what is"
                ])

                if needs_search:
                    ai_response = await run_agent(query)
                    await manager.broadcast(chat_id, {
                        "sender_id": "ai-assistant",
                        "username": "AI Assistant",
                        "content": ai_response,
                        "created_at": None,
                    })
                else:
                    streamed = ""

                    async def stream_callback(token: str):
                        nonlocal streamed
                        streamed += token
                        await manager.broadcast(chat_id, {
                            "type": "stream_chunk",
                            "sender_id": "ai-assistant",
                            "username": "AI Assistant",
                            "content": streamed,
                            "created_at": None,
                        })

                    ai_response = await run_agent_stream(query, stream_callback)

                async with AsyncSessionLocal() as db:
                    ai_message = Message(
                        chat_id=chat_id,
                        sender_id="ai-assistant",
                        content=ai_response,
                        is_ai_command=False,
                    )
                    db.add(ai_message)
                    await db.commit()

    except WebSocketDisconnect:
        manager.disconnect(websocket, chat_id)