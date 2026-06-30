from sqlalchemy import String, Boolean, DateTime,Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from database.connection import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(225), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(100),nullable=False)
    hashed_password : Mapped[str] = mapped_column(String,nullable=False)
    avatar_url : Mapped[str | None] = mapped_column(String,nullable=True)
    bio : Mapped[str | None] = mapped_column(Text,nullable=True)
    is_online : Mapped[bool] = mapped_column(Boolean,default=False)
    last_seen : Mapped[DateTime | None] = mapped_column(DateTime(timezone=True),nullable=True)
    created_at : Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
