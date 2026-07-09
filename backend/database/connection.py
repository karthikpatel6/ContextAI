from sqlalchemy.ext.asyncio import AsyncSession,create_async_engine,async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL","postgresql+asyncpg://postgres:password@localhost:5432/contextai")

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,
    max_overflow=20
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()    


async def create_tables():
    async with engine.begin() as conn:
        from models import user, chat, message
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        from models.user import User

        result = await db.execute(select(User).where(User.id == "ai-assistant"))
        ai_user = result.scalar_one_or_none()

        if not ai_user:
            ai_user = User(
                id="ai-assistant",
                username="ai_assistant",
                email="ai@whatsapp-ai.com",
                full_name="AI Assistant",
                hashed_password="not-a-real-password",
            )
            db.add(ai_user)
            await db.commit()
            print("✅ AI user created")