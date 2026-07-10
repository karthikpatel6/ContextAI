from fastapi import APIRouter, Depends, HTTPException
from models.user import User
from schemas.user import UserResponse
from core.dependencies import get_current_user
from sqlalchemy import or_, and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db

router = APIRouter(prefix="/users",tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)

@router.get("/search")
async def search_users(
    q: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if len(q) < 2:
        raise HTTPException(status_code=400, detail="Query too short")
     
    result = await db.execute(
        select(User).where(
            and_(
                or_(
                    User.username.ilike(f"%{q}%"),
                    User.full_name.ilike(f"%{q}%"),
                ),
                User.id != current_user.id,
            )
        ).limit(10)
    )
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]