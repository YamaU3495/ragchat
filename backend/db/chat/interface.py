from typing import List
from abc import ABC, abstractmethod
from .models import ChatMessage

class IChatRepo(ABC):
    @abstractmethod
    async def save_chat_message(self, session_id: str, message: ChatMessage) -> ChatMessage:
        """Save a chat message for a given session and return the message with assigned no"""
        pass

    @abstractmethod
    async def get_chat_messages(self, session_id: str) -> List[ChatMessage]:
        """Get all chat messages for a given session"""
        pass

    @abstractmethod
    async def clear_chat_messages(self, session_id: str) -> None:
        """Clear all chat messages for a given session"""
        pass

    @abstractmethod
    async def delete_chat_message_by_no(self, session_id: str, no: int) -> None:
        """Delete a chat message by its no for a given session"""
        pass 