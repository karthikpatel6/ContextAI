from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from database.connection import get_db
from models.message import Message
from models.chat import ChatMember
from models.user import User
from core.dependencies import get_current_user
from agents.reply_suggester import suggest_replies

router = APIRouter(prefix="/ai", tags=["AI Features"])

@router.get("/suggest-replies")
async def get_reply_suggestions(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    
    result = await db.execute(
        select(ChatMember).where(
            and_(
                ChatMember.chat_id == chat_id,
                ChatMember.user_id == current_user.id,
            )
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not a member of this chat")
    
    result = await db.execute(
        select(User)
        .join(ChatMember, User.id == ChatMember.user_id)
        .where(
            and_(
                ChatMember.chat_id == chat_id,
                User.id != current_user.id,
            )
        )
    )
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc())
        .limit(20)
    )

    messages = list(reversed(result.scalars().all()))

    suggestions = await suggest_replies(messages, contact.username)

    return suggestions