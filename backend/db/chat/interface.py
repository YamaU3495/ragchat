from typing import List, Dict
from abc import ABC, abstractmethod

class IChatRepo(ABC):
    @abstractmethod
    async def save_chat_message(self, session_id: str, role: str, content: str) -> None:
        """Save a chat message for a given session"""
        pass

    @abstractmethod
    async def get_chat_messages(self, session_id: str) -> List[Dict[str, str]]:
        """Get all chat messages for a given session"""
        pass

    @abstractmethod
    async def clear_chat_messages(self, session_id: str) -> None:
        """Clear all chat messages for a given session"""
        pass 