from typing import List, Dict
from logging import getLogger
from .interface import IChatRepo
from .models import ChatMessage

class InMemoryChatRepo(IChatRepo):
    def __init__(self):
        self.logger = getLogger("uvicorn.app")
        # user_id -> session_id -> messages の構造に変更
        self._chat_messages: Dict[str, Dict[str, List[ChatMessage]]] = {}

    async def save_chat_message(self, user_id: str, session_id: str, message: ChatMessage) -> ChatMessage:
        """チャットメッセージを保存し、no割り当て済みのChatMessageを返す"""
        self.logger.info(f"Saving chat message for user {user_id}, session {session_id}")
        if user_id not in self._chat_messages:
            self._chat_messages[user_id] = {}
        if session_id not in self._chat_messages[user_id]:
            self._chat_messages[user_id][session_id] = []
        # noを自動付与
        next_no = len(self._chat_messages[user_id][session_id]) + 1
        message_with_no = ChatMessage(no=next_no, role=message.role, content=message.content)
        self._chat_messages[user_id][session_id].append(message_with_no)
        self.logger.info(f"Saved chat message for user {user_id}, session {session_id}")
        self.logger.info(f"Chat messages count: {len(self._chat_messages[user_id][session_id])}")
        return message_with_no

    async def get_chat_messages(self, user_id: str, session_id: str) -> List[ChatMessage]:
        """セッションIDに紐づくチャットメッセージを取得する"""
        self.logger.info(f"Getting chat messages for user {user_id}, session {session_id}")
        total_sessions = sum(len(sessions) for sessions in self._chat_messages.values())
        self.logger.info(f"Chat messages all count: {total_sessions}")
        if user_id in self._chat_messages and session_id in self._chat_messages[user_id]:
            return self._chat_messages[user_id][session_id]
        return []

    async def clear_chat_messages(self, user_id: str, session_id: str) -> None:
        """指定したsession_idの全メッセージを削除する"""
        if user_id in self._chat_messages and session_id in self._chat_messages[user_id]:
            self._chat_messages[user_id][session_id] = []

    async def delete_chat_message_by_no(self, user_id: str, session_id: str, no: int) -> None:
        """指定されたnoのメッセージを削除する"""
        if user_id in self._chat_messages and session_id in self._chat_messages[user_id]:
            self._chat_messages[user_id][session_id] = [msg for msg in self._chat_messages[user_id][session_id] if msg.no != no] 