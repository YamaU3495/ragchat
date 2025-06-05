from typing import List, Dict
from logging import getLogger
from .interface import IChatRepo
from .models import ChatMessage

class InMemoryChatRepo(IChatRepo):
    def __init__(self):
        self.logger = getLogger("uvicorn.app")
        self._chat_messages: Dict[str, List[ChatMessage]] = {}

    async def save_chat_message(self, session_id: str, message: ChatMessage) -> None:
        """チャットメッセージを保存する"""
        self.logger.info(f"Saving chat message for session {session_id}")
        if session_id not in self._chat_messages:
            self._chat_messages[session_id] = []
        # noを自動付与
        next_no = len(self._chat_messages[session_id]) + 1
        message_with_no = ChatMessage(no=next_no, role=message.role, content=message.content)
        self._chat_messages[session_id].append(message_with_no)
        self.logger.info(f"Saved chat message for session {session_id}")
        self.logger.info(f"Chat messages count: {len(self._chat_messages[session_id])}")

    async def get_chat_messages(self, session_id: str) -> List[ChatMessage]:
        """セッションIDに紐づくチャットメッセージを取得する"""
        self.logger.info(f"Getting chat messages for session {session_id}")
        self.logger.info(f"Chat messages all count: {len(self._chat_messages)}")
        return self._chat_messages.get(session_id, [])

    async def clear_chat_messages(self, session_id: str) -> None:
        """セッションIDに紐づくチャットメッセージを削除する"""
        if session_id in self._chat_messages:
            self._chat_messages[session_id] = []

    async def delete_chat_message_by_no(self, session_id: str, no: int) -> None:
        """指定されたnoのメッセージを削除する"""
        if session_id in self._chat_messages:
            self._chat_messages[session_id] = [msg for msg in self._chat_messages[session_id] if msg.no != no] 