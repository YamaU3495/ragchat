from typing import List, Dict
from logging import getLogger
from pymongo import MongoClient
from .interface import IChatRepo
from .models import ChatMessage, SessionTitle
from datetime import datetime
import os

class MongoChatRepo(IChatRepo):
    def __init__(self, host_name: str, port_num: int, db_name: str = "chatdb", collection_name: str = "messages"):
        self.logger = getLogger("uvicorn.app")
        
        # 環境変数から認証情報を取得
        username = os.getenv("MONGODB_USER")
        password = os.getenv("MONGODB_PASSWORD")
        
        if username and password:
            # 認証情報がある場合はURIを使用
            uri = f"mongodb://{username}:{password}@{host_name}:{port_num}/admin"
            self.client = MongoClient(uri)
        else:
            # 認証情報がない場合は従来通り
            self.client = MongoClient(host=host_name, port=port_num)
        
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.session_titles_collection = self.db["session_titles"]

    async def save_chat_message(self, user_id: str, session_id: str, message: ChatMessage) -> ChatMessage:
        """チャットメッセージを保存し、no割り当て済みのChatMessageを返す"""
        self.logger.info(f"Saving chat message for user {user_id}, session {session_id}")
        try:
            # noを自動付与
            next_no = self.collection.count_documents({"user_id": user_id, "session_id": session_id}) + 1
            self.collection.insert_one({
                "user_id": user_id,
                "session_id": session_id,
                "no": next_no,
                "role": message.role,
                "content": message.content
            })
            count = self.collection.count_documents({"user_id": user_id, "session_id": session_id})
            self.logger.info(f"Saved chat message for user {user_id}, session {session_id}")
            self.logger.info(f"Chat messages count: {count}")
            return ChatMessage(no=next_no, role=message.role, content=message.content)
        except Exception as e:
            self.logger.error(f"Error saving chat message for user_id={user_id}, session_id={session_id}, role={message.role}: {str(e)}", exc_info=True)
            raise

    async def get_chat_messages(self, user_id: str, session_id: str) -> List[ChatMessage]:
        """セッションIDに紐づくチャットメッセージを取得する"""
        self.logger.info(f"Getting chat messages for user {user_id}, session {session_id}")
        try:
            all_count = self.collection.count_documents({})
            self.logger.info(f"Chat messages all count: {all_count}")
            cursor = self.collection.find({"user_id": user_id, "session_id": session_id}, {"_id": 0, "no": 1, "role": 1, "content": 1}).sort("no", 1)
            messages = [ChatMessage(**msg) for msg in cursor]
            return messages
        except Exception as e:
            self.logger.error(f"Error getting chat messages for user_id={user_id}, session_id={session_id}: {str(e)}", exc_info=True)
            raise

    async def clear_chat_messages(self, user_id: str, session_id: str) -> None:
        """指定したsession_idの全メッセージを削除する"""
        try:
            result = self.collection.delete_many({"user_id": user_id, "session_id": session_id})
            self.logger.info(f"Cleared {result.deleted_count} messages for user_id={user_id}, session_id={session_id}")
        except Exception as e:
            self.logger.error(f"Error clearing chat messages for user_id={user_id}, session_id={session_id}: {str(e)}", exc_info=True)
            raise

    async def delete_chat_message_by_no(self, user_id: str, session_id: str, no: int) -> None:
        """指定されたnoのメッセージを削除する"""
        try:
            result = self.collection.delete_one({"user_id": user_id, "session_id": session_id, "no": no})
            if result.deleted_count == 0:
                self.logger.warning(f"No message found to delete for user_id={user_id}, session_id={session_id}, no={no}")
            else:
                self.logger.info(f"Deleted message no={no} for user_id={user_id}, session_id={session_id}")
        except Exception as e:
            self.logger.error(f"Error deleting chat message for user_id={user_id}, session_id={session_id}, no={no}: {str(e)}", exc_info=True)
            raise

    async def get_session_ids(self, user_id: str) -> List[str]:
        """user_idに紐づくすべてのsession_idを取得する"""
        self.logger.info(f"Getting session IDs for user {user_id}")
        try:
            # user_idでフィルタして、重複のないsession_idを取得
            session_ids = self.collection.distinct("session_id", {"user_id": user_id})
            self.logger.info(f"Found {len(session_ids)} sessions for user {user_id}")
            return session_ids
        except Exception as e:
            self.logger.error(f"Error getting session IDs for user_id={user_id}: {str(e)}", exc_info=True)
            raise

    async def delete_messages_from_no(self, user_id: str, session_id: str, no: int) -> None:
        """指定されたno以降のメッセージを削除する"""
        try:
            result = self.collection.delete_many({
                "user_id": user_id, 
                "session_id": session_id, 
                "no": {"$gte": no}
            })
            self.logger.info(f"Deleted {result.deleted_count} messages from no={no} for user_id={user_id}, session_id={session_id}")
        except Exception as e:
            self.logger.error(f"Error deleting messages from no={no} for user_id={user_id}, session_id={session_id}: {str(e)}", exc_info=True)
            raise

    async def save_session_title(self, user_id: str, session_id: str, title: str) -> SessionTitle:
        """セッションタイトルを保存する"""
        self.logger.info(f"Saving session title for user {user_id}, session {session_id}")
        try:
            now = datetime.utcnow()
            session_title = SessionTitle(
                user_id=user_id,
                session_id=session_id,
                title=title,
                created_at=now,
                updated_at=now
            )
            
            # 既存のタイトルがあるかチェック
            existing = self.session_titles_collection.find_one({
                "user_id": user_id,
                "session_id": session_id
            })
            
            if existing:
                # 既存のタイトルを更新
                self.session_titles_collection.update_one(
                    {"user_id": user_id, "session_id": session_id},
                    {"$set": {"title": title, "updated_at": now}}
                )
                session_title.updated_at = now
            else:
                # 新しいタイトルを挿入
                self.session_titles_collection.insert_one(session_title.dict())
            
            self.logger.info(f"Saved session title for user {user_id}, session {session_id}")
            return session_title
        except Exception as e:
            self.logger.error(f"Error saving session title for user_id={user_id}, session_id={session_id}: {str(e)}", exc_info=True)
            raise

    async def get_session_titles(self, user_id: str) -> List[SessionTitle]:
        """ユーザーのセッションタイトル一覧を取得する"""
        self.logger.info(f"Getting session titles for user {user_id}")
        try:
            cursor = self.session_titles_collection.find(
                {"user_id": user_id}, 
                {"_id": 0}
            ).sort("updated_at", -1)  # 更新日時の降順でソート
            
            session_titles = []
            for doc in cursor:
                session_titles.append(SessionTitle(**doc))
            
            self.logger.info(f"Found {len(session_titles)} session titles for user {user_id}")
            return session_titles
        except Exception as e:
            self.logger.error(f"Error getting session titles for user_id={user_id}: {str(e)}", exc_info=True)
            raise

    async def update_session_title(self, user_id: str, session_id: str, title: str) -> SessionTitle:
        """セッションタイトルを更新する"""
        self.logger.info(f"Updating session title for user {user_id}, session {session_id}")
        try:
            now = datetime.utcnow()
            
            # 既存のタイトルを更新
            result = self.session_titles_collection.update_one(
                {"user_id": user_id, "session_id": session_id},
                {"$set": {"title": title, "updated_at": now}}
            )
            
            if result.matched_count == 0:
                # タイトルが存在しない場合は新規作成
                return await self.save_session_title(user_id, session_id, title)
            
            # 更新されたタイトルを取得
            updated_doc = self.session_titles_collection.find_one({
                "user_id": user_id,
                "session_id": session_id
            })
            
            session_title = SessionTitle(**updated_doc)
            self.logger.info(f"Updated session title for user {user_id}, session {session_id}")
            return session_title
        except Exception as e:
            self.logger.error(f"Error updating session title for user_id={user_id}, session_id={session_id}: {str(e)}", exc_info=True)
            raise 