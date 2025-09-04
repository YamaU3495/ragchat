from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ChatMessage(BaseModel):
    no: int
    role: str
    content: str

class SessionTitle(BaseModel):
    user_id: str
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime 