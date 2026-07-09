from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from database.connection import get_db
from models.chat import Chat, ChatMember
from models.user import User
from core.dependencies import get_current_user
from schemas.user import ChatResponse, CreateDirectChat
from schemas.chat import MessageResponse

router = APIRouter(prefix="/chats",tags=["Chats"])

@router.post("/direct",response_model=ChatResponse)
async def create_direct_chat(
    payload: CreateDirectChat,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == payload.target_user_id))
    target_user = result.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=404,detail="User not found")
    
    chat = Chat(created_by=current_user.id)
    db.add(chat)
    await db.flush()

    member1 = ChatMember(chat_id=chat.id, user_id=current_user.id, is_admin=True)
    member2 = ChatMember(chat_id=chat.id,user_id=target_user.id)
    db.add(member1)
    db.add(member2)

    await db.commit()
    await db.refresh(chat)
    return ChatResponse.model_validate(chat)

@router.get("/", response_model=list[ChatResponse])
async def get_my_chats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Chat)
        .join(ChatMember, Chat.id == ChatMember.chat_id)
        .where(ChatMember.user_id == current_user.id)
        .order_by(Chat.created_at.desc())
    )
    chats = result.scalars().all()
    return [ChatResponse.model_validate(c) for c in chats]


@router.get("/{chat_id}/messages", response_model=list[MessageResponse])
async def get_messages(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ChatMember)
        .where(
            and_(ChatMember.chat_id == chat_id, ChatMember.user_id == current_user.id)
        )
    )

    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not a member of this chat")
    
    from models.message import Message
    result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id)
        .order_by(Message.created_at.asc())
        .limit(50)
    )
    messages = result.scalars().all()
    return [MessageResponse.model_validate(m) for m in messages]
    

