from fastapi import APIRouter, Depends
from models.user import User
from schemas.user import UserResponse
from core.dependencies import get_current_user

router = APIRouter(prefix="/users",tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
