from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from database.connection import Base
import uuid 
# import enum

class ChatMember(Base):
    __tablename__ = "chat_members"
    id: Mapped[str] = mapped_column(String,primary_key=True,default=lambda: str(uuid.uuid4()))
    chat_id: Mapped[str] = mapped_column(String,ForeignKey("chats.id"),nullable=False)
    user_id: Mapped[str] = mapped_column(String,ForeignKey("users.id"),nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean,default=False)
    joined_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True),server_default=func.now())


class Chat(Base):
    __tablename__ = "chats"
    id: Mapped[str] = mapped_column(String,primary_key=True,default=lambda: str(uuid.uuid4()))
    created_by: Mapped[str] = mapped_column(String,ForeignKey("users.id"))
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True),server_default=func.now())
