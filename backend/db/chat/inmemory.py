from typing import List, Dict
from logging import getLogger
from .interface import IChatRepo

class InMemoryChatRepo(IChatRepo):
    def __init__(self):
        self.logger = getLogger("uvicorn.app")
        self._chat_messages: Dict[str, List[Dict[str, str]]] = {}

    async def save_chat_message(self, session_id: str, role: str, content: str) -> None:
        """チャットメッセージを保存する"""
        self.logger.info(f"Saving chat message for session {session_id}")
        if session_id not in self._chat_messages:
            self._chat_messages[session_id] = []
        self._chat_messages[session_id].append({
            "role": role,
            "content": content
        })
        self.logger.info(f"Saved chat message for session {session_id}")
        self.logger.info(f"Chat messages count: {len(self._chat_messages[session_id])}")

    async def get_chat_messages(self, session_id: str) -> List[Dict[str, str]]:
        """セッションIDに紐づくチャットメッセージを取得する"""
        self.logger.info(f"Getting chat messages for session {session_id}")
        self.logger.info(f"Chat messages all count: {len(self._chat_messages)}")
        return self._chat_messages.get(session_id, [])

    async def clear_chat_messages(self, session_id: str) -> None:
        """セッションIDに紐づくチャットメッセージを削除する"""
        if session_id in self._chat_messages:
            self._chat_messages[session_id] = [] 