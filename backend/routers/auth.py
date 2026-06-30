from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.connection import get_db
from models.user import User
from schemas.user import UserRegister
from core.security import hash_password

router  = APIRouter(prefix="/auth",tags=["Authentication"])

@router.post("/register")
async def register(payload: UserRegister,db : AsyncSession = Depends(get_db)):
    # for username validation
    result = await db.execute(select(User).where(User.username == payload.username))
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400,detail="Username already taken")
    # for email validation
    result = await db.execute(select(User).where(User.email == payload.email))
    existing_email = result.scalar_one_or_none()
    if existing_email:
        raise HTTPException(status_code=400,detail="Email Already Registered")
    
    user = User(
        username = payload.username,
        email = payload.email,
        full_name = payload.full_name,
        hashed_password = hash_password(payload.password)
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
