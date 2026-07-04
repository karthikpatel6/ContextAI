from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserRegister(BaseModel):
    username : str
    email : EmailStr
    full_name : str
    password : str
    
class UserResponse(BaseModel):
    id: str
    username : str
    email : EmailStr
    full_name : str
    avatar_url: str | None
    bio : str | None
    is_online : bool
    last_seen : datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}

class UserLogin(BaseModel):
    username : str
    password : str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class CreateDirectChat(BaseModel):
    target_user_id: str

class ChatResponse(BaseModel):
    id: str
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}
    
