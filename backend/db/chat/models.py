from pydantic import BaseModel

class ChatMessage(BaseModel):
    no: int
    role: str
    content: str 