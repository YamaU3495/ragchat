from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from chat import ChatManager
from containers import Container
import uuid
from typing import List
from db.chat.models import ChatMessage, SessionTitle
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

class EditMessageRequest(BaseModel):
    content: str
    user_id: str
    session_id: str
    no: int

class EditMessageResponse(BaseModel):
    content: str
    session_id: str
    no: int

class SessionTitleResponse(BaseModel):
    session_id: str
    title: str
    created_at: str
    updated_at: str

class SessionTitlesListResponse(BaseModel):
    user_id: str
    sessions: List[SessionTitleResponse]

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

@router.post("/chat/edit", response_model=EditMessageResponse)
async def edit_message(
    request: EditMessageRequest,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    指定されたNo以降の履歴を削除し、新しいメッセージを送信してレスポンスを取得する
    
    処理の流れ：
    1. ユーザーID、セッションID、No以降の履歴を削除
    2. メッセージ送信。AIのレスポンスのみを返却
    """
    try:
        ai_response = await chat_manager.edit_message_and_get_response(
            message=request.content,
            user_id=request.user_id,
            session_id=request.session_id,
            no=request.no
        )
        return EditMessageResponse(
            content=ai_response.content,
            session_id=request.session_id,
            no=ai_response.no
        )
    except Exception as e:
        logger.error(f"Error in edit_message endpoint for user_id={request.user_id}, session_id={request.session_id}, no={request.no}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/chat/sessions/titles/{user_id}", response_model=SessionTitlesListResponse)
async def get_user_session_titles(
    user_id: str,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    ユーザーのセッションタイトル一覧を取得する
    """
    try:
        session_titles = await chat_manager.chat_repository.get_session_titles(user_id)
        
        # SessionTitleをSessionTitleResponseに変換
        session_responses = []
        for session_title in session_titles:
            session_responses.append(SessionTitleResponse(
                session_id=session_title.session_id,
                title=session_title.title,
                created_at=session_title.created_at.isoformat(),
                updated_at=session_title.updated_at.isoformat()
            ))
        
        return SessionTitlesListResponse(
            user_id=user_id,
            sessions=session_responses
        )
    except Exception as e:
        logger.error(f"Error in get_user_session_titles endpoint for user_id={user_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/chat/sessions/titles/{user_id}/{session_id}")
async def delete_session_title(
    user_id: str,
    session_id: str,
    chat_manager: ChatManager = Depends(get_chat_manager)
):
    """
    指定したsession_idのセッションタイトルを削除する
    """
    try:
        await chat_manager.chat_repository.delete_session_title(user_id, session_id)
        return {"message": f"Session title for user_id={user_id}, session_id={session_id} deleted", "user_id": user_id, "session_id": session_id}
    except Exception as e:
        logger.error(f"Error in delete_session_title endpoint for user_id={user_id}, session_id={session_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) 