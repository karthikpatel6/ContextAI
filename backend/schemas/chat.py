from pydantic import BaseModel
from datetime import datetime

class CreateDirectChat(BaseModel):
    target_user_id: str

class ChatResponse(BaseModel):
    id: str
    created_by: str
    created_at: datetime
    model_config = {"from_attributes": True}

class MessageResponse(BaseModel):
    id: str
    chat_id: str
    sender_id: str
    content: str
    is_ai_command: bool
    created_at: datetime
    model_config = {"from_attributes": True}