from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from database.connection import Base
import uuid

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(String,primary_key=True,default=lambda: str(uuid.uuid4()))
    chat_id: Mapped[str] = mapped_column(String,ForeignKey("chats.id"))
    sender_id: Mapped[str] = mapped_column(String,ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text,nullable=False)
    is_ai_command: Mapped[bool] = mapped_column(Boolean,default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True),server_default=func.now(),index=True)
