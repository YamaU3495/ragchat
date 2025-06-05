from typing import List, Dict
from logging import getLogger
from pymongo import MongoClient
from .interface import IChatRepo
from .models import ChatMessage

class MongoChatRepo(IChatRepo):
    def __init__(self, host_name: str, port_num: int, db_name: str = "chatdb", collection_name: str = "messages"):
        self.logger = getLogger("uvicorn.app")
        self.client = MongoClient(
            host = host_name,
            port = port_num
        )
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    async def save_chat_message(self, session_id: str, message: ChatMessage) -> None:
        """チャットメッセージを保存する"""
        self.logger.info(f"Saving chat message for session {session_id}")
        # noを自動付与
        next_no = self.collection.count_documents({"session_id": session_id}) + 1
        self.collection.insert_one({
            "session_id": session_id,
            "no": next_no,
            "role": message.role,
            "content": message.content
        })
        count = self.collection.count_documents({"session_id": session_id})
        self.logger.info(f"Saved chat message for session {session_id}")
        self.logger.info(f"Chat messages count: {count}")

    async def get_chat_messages(self, session_id: str) -> List[ChatMessage]:
        """セッションIDに紐づくチャットメッセージを取得する"""
        self.logger.info(f"Getting chat messages for session {session_id}")
        all_count = self.collection.count_documents({})
        self.logger.info(f"Chat messages all count: {all_count}")
        cursor = self.collection.find({"session_id": session_id}, {"_id": 0, "no": 1, "role": 1, "content": 1}).sort("no", 1)
        messages = [ChatMessage(**msg) for msg in cursor]
        return messages

    async def clear_chat_messages(self, session_id: str) -> None:
        """セッションIDに紐づくチャットメッセージを削除する"""
        self.collection.delete_many({"session_id": session_id})

    async def delete_chat_message_by_no(self, session_id: str, no: int) -> None:
        """指定されたnoのメッセージを削除する"""
        self.collection.delete_one({"session_id": session_id, "no": no}) 