from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from chat import ChatManager
from containers import Container
import uuid
from typing import List, Dict

router = APIRouter()

def get_chat_manager(container: Container = Depends(lambda: Container())) -> ChatManager:
    return ChatManager(container)

class Message(BaseModel):
    content: str
    session_id: str | None = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessage]
    session_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: Message,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    Send a message to the chat and get a response.
    If session_id is not provided, a new one will be generated.
    """
    try:
        # Generate new session_id if not provided
        session_id = message.session_id or str(uuid.uuid4())
        
        response = await chat_manager.get_response(
            message=message.content,
            session_id=session_id
        )
        
        return ChatResponse(
            response=response,
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/chat/clear")
async def clear_chat(
    session_id: str,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    Clear the chat history for the specified session.
    """
    chat_manager.clear_memory(session_id=session_id)
    return {"message": "Chat history cleared", "session_id": session_id}

@router.get("/chat/history/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    session_id: str,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    Get the chat history for the specified session.
    """
    try:
        messages = await chat_manager.chat_repository.get_chat_messages(session_id)
        return ChatHistoryResponse(
            messages=[ChatMessage(**msg) for msg in messages],
            session_id=session_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 