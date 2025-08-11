from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from chat import ChatManager
from containers import Container
import uuid
from typing import List
from db.chat.models import ChatMessage
from logging import getLogger

router = APIRouter()

# ロガーの初期化
logger = getLogger("uvicorn.app")

def get_chat_manager(container: Container = Depends(lambda: Container())) -> ChatManager:
    return ChatManager(container)

class Message(BaseModel):
    content: str
    user_id: str
    session_id: str | None = None

class ChatResponse(ChatMessage):
    session_id: str
    request_no: int

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessage]
    session_id: str

class SessionListResponse(BaseModel):
    session_ids: List[str]
    user_id: str

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
        session_id = message.session_id or str(uuid.uuid4())
        last_msgs = await chat_manager.get_response(
            message=message.content,
            user_id=message.user_id,
            session_id=session_id
        )
        return ChatResponse(
            session_id=session_id,
            request_no=last_msgs[0].no,
            no=last_msgs[-1].no,
            role=last_msgs[-1].role,
            content=last_msgs[-1].content,
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint for user_id={message.user_id}, session_id={session_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/chat/sessions/{user_id}", response_model=SessionListResponse)
async def get_user_sessions(
    user_id: str,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    Get all session IDs for the specified user.
    """
    try:
        session_ids = await chat_manager.chat_repository.get_session_ids(user_id)
        return SessionListResponse(
            session_ids=session_ids,
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Error in get_user_sessions endpoint for user_id={user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/chat/clear")
async def clear_chat(
    user_id: str,
    session_id: str,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    Clear the chat history for the specified session.
    """
    try:
        await chat_manager.clear_memory(user_id=user_id, session_id=session_id)
        return {"message": "Chat history cleared", "user_id": user_id, "session_id": session_id}
    except Exception as e:
        logger.error(f"Error in clear_chat endpoint for user_id={user_id}, session_id={session_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/chat/history/{user_id}/{session_id}", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: str,
    session_id: str,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    Get the chat history for the specified session.
    """
    try:
        messages = await chat_manager.chat_repository.get_chat_messages(user_id, session_id)
        return ChatHistoryResponse(
            messages=messages,
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Error in get_chat_history endpoint for user_id={user_id}, session_id={session_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/chat/message/{user_id}/{session_id}/{no}")
async def delete_chat_message(
    user_id: str,
    session_id: str,
    no: int,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    指定したnoのメッセージを削除する
    """
    try:
        await chat_manager.chat_repository.delete_chat_message_by_no(user_id, session_id, no)
        return {"message": f"Message no={no} deleted", "user_id": user_id, "session_id": session_id}
    except Exception as e:
        logger.error(f"Error in delete_chat_message endpoint for user_id={user_id}, session_id={session_id}, no={no}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/chat/messages/{user_id}/{session_id}")
async def delete_all_chat_messages(
    user_id: str,
    session_id: str,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    指定したsession_idの全メッセージを削除する
    """
    try:
        await chat_manager.chat_repository.clear_chat_messages(user_id, session_id)
        return {"message": f"All messages for user_id={user_id}, session_id={session_id} deleted", "user_id": user_id, "session_id": session_id}
    except Exception as e:
        logger.error(f"Error in delete_all_chat_messages endpoint for user_id={user_id}, session_id={session_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 