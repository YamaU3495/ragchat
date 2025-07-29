from typing import List
from abc import ABC, abstractmethod
from .models import ChatMessage

class IChatRepo(ABC):
    @abstractmethod
    async def save_chat_message(self, user_id: str, session_id: str, message: ChatMessage) -> ChatMessage:
        """Save a chat message for a given session and return the message with assigned no"""
        pass

    @abstractmethod
    async def get_chat_messages(self, user_id: str, session_id: str) -> List[ChatMessage]:
        """Get all chat messages for a given session"""
        pass

    @abstractmethod
    async def clear_chat_messages(self, user_id: str, session_id: str) -> None:
        """指定したsession_idの全メッセージを削除する"""
        pass

    @abstractmethod
    async def delete_chat_message_by_no(self, user_id: str, session_id: str, no: int) -> None:
        """Delete a chat message by its no for a given session"""
        pass

    @abstractmethod
    async def get_session_ids(self, user_id: str) -> List[str]:
        """Get all session IDs for a given user"""
        pass 