from typing import List, Dict
from logging import getLogger
from .interface import IChatRepo
from .models import ChatMessage, SessionTitle
from datetime import datetime

class InMemoryChatRepo(IChatRepo):
    def __init__(self):
        self.logger = getLogger("uvicorn.app")
        # user_id -> session_id -> messages の構造に変更
        self._chat_messages: Dict[str, Dict[str, List[ChatMessage]]] = {}
        # user_id -> session_id -> SessionTitle の構造
        self._session_titles: Dict[str, Dict[str, SessionTitle]] = {}

    async def save_chat_message(self, user_id: str, session_id: str, message: ChatMessage) -> ChatMessage:
        """チャットメッセージを保存し、no割り当て済みのChatMessageを返す"""
        self.logger.info(f"Saving chat message for user {user_id}, session {session_id}")
        try:
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
        except Exception as e:
            self.logger.error(f"Error saving chat message for user_id={user_id}, session_id={session_id}, role={message.role}: {str(e)}", exc_info=True)
            raise

    async def get_chat_messages(self, user_id: str, session_id: str) -> List[ChatMessage]:
        """セッションIDに紐づくチャットメッセージを取得する"""
        self.logger.info(f"Getting chat messages for user {user_id}, session {session_id}")
        try:
            total_sessions = sum(len(sessions) for sessions in self._chat_messages.values())
            self.logger.info(f"Chat messages all count: {total_sessions}")
            if user_id in self._chat_messages and session_id in self._chat_messages[user_id]:
                return self._chat_messages[user_id][session_id]
            return []
        except Exception as e:
            self.logger.error(f"Error getting chat messages for user_id={user_id}, session_id={session_id}: {str(e)}", exc_info=True)
            raise

    async def clear_chat_messages(self, user_id: str, session_id: str) -> None:
        """指定したsession_idの全メッセージを削除する"""
        try:
            if user_id in self._chat_messages and session_id in self._chat_messages[user_id]:
                message_count = len(self._chat_messages[user_id][session_id])
                self._chat_messages[user_id][session_id] = []
                self.logger.info(f"Cleared {message_count} messages for user_id={user_id}, session_id={session_id}")
            else:
                self.logger.info(f"No messages to clear for user_id={user_id}, session_id={session_id}")
        except Exception as e:
            self.logger.error(f"Error clearing chat messages for user_id={user_id}, session_id={session_id}: {str(e)}", exc_info=True)
            raise

    async def delete_chat_message_by_no(self, user_id: str, session_id: str, no: int) -> None:
        """指定されたnoのメッセージを削除する"""
        try:
            if user_id in self._chat_messages and session_id in self._chat_messages[user_id]:
                original_count = len(self._chat_messages[user_id][session_id])
                self._chat_messages[user_id][session_id] = [msg for msg in self._chat_messages[user_id][session_id] if msg.no != no]
                new_count = len(self._chat_messages[user_id][session_id])
                if original_count == new_count:
                    self.logger.warning(f"No message found to delete for user_id={user_id}, session_id={session_id}, no={no}")
                else:
                    self.logger.info(f"Deleted message no={no} for user_id={user_id}, session_id={session_id}")
            else:
                self.logger.warning(f"No messages found for user_id={user_id}, session_id={session_id}")
        except Exception as e:
            self.logger.error(f"Error deleting chat message for user_id={user_id}, session_id={session_id}, no={no}: {str(e)}", exc_info=True)
            raise

    async def get_session_ids(self, user_id: str) -> List[str]:
        """user_idに紐づくすべてのsession_idを取得する"""
        self.logger.info(f"Getting session IDs for user {user_id}")
        try:
            if user_id in self._chat_messages:
                session_ids = list(self._chat_messages[user_id].keys())
                self.logger.info(f"Found {len(session_ids)} sessions for user {user_id}")
                return session_ids
            return []
        except Exception as e:
            self.logger.error(f"Error getting session IDs for user_id={user_id}: {str(e)}", exc_info=True)
            raise

    async def delete_messages_from_no(self, user_id: str, session_id: str, no: int) -> None:
        """指定されたno以降のメッセージを削除する"""
        try:
            if user_id in self._chat_messages and session_id in self._chat_messages[user_id]:
                original_count = len(self._chat_messages[user_id][session_id])
                self._chat_messages[user_id][session_id] = [msg for msg in self._chat_messages[user_id][session_id] if msg.no < no]
                new_count = len(self._chat_messages[user_id][session_id])
                deleted_count = original_count - new_count
                self.logger.info(f"Deleted {deleted_count} messages from no={no} for user_id={user_id}, session_id={session_id}")
            else:
                self.logger.warning(f"No messages found for user_id={user_id}, session_id={session_id}")
        except Exception as e:
            self.logger.error(f"Error deleting messages from no={no} for user_id={user_id}, session_id={session_id}: {str(e)}", exc_info=True)
            raise

    async def save_session_title(self, user_id: str, session_id: str, title: str) -> SessionTitle:
        """セッションタイトルを保存する"""
        self.logger.info(f"Saving session title for user {user_id}, session {session_id}")
        try:
            now = datetime.utcnow()
            
            if user_id not in self._session_titles:
                self._session_titles[user_id] = {}
            
            # 既存のタイトルがあるかチェック
            if session_id in self._session_titles[user_id]:
                # 既存のタイトルを更新
                existing_title = self._session_titles[user_id][session_id]
                existing_title.title = title
                existing_title.updated_at = now
                session_title = existing_title
            else:
                # 新しいタイトルを作成
                session_title = SessionTitle(
                    user_id=user_id,
                    session_id=session_id,
                    title=title,
                    created_at=now,
                    updated_at=now
                )
                self._session_titles[user_id][session_id] = session_title
            
            self.logger.info(f"Saved session title for user {user_id}, session {session_id}")
            return session_title
        except Exception as e:
            self.logger.error(f"Error saving session title for user_id={user_id}, session_id={session_id}: {str(e)}", exc_info=True)
            raise

    async def get_session_titles(self, user_id: str) -> List[SessionTitle]:
        """ユーザーのセッションタイトル一覧を取得する"""
        self.logger.info(f"Getting session titles for user {user_id}")
        try:
            if user_id in self._session_titles:
                session_titles = list(self._session_titles[user_id].values())
                # 更新日時の降順でソート
                session_titles.sort(key=lambda x: x.updated_at, reverse=True)
                self.logger.info(f"Found {len(session_titles)} session titles for user {user_id}")
                return session_titles
            return []
        except Exception as e:
            self.logger.error(f"Error getting session titles for user_id={user_id}: {str(e)}", exc_info=True)
            raise

    async def update_session_title(self, user_id: str, session_id: str, title: str) -> SessionTitle:
        """セッションタイトルを更新する"""
        self.logger.info(f"Updating session title for user {user_id}, session {session_id}")
        try:
            if user_id in self._session_titles and session_id in self._session_titles[user_id]:
                # 既存のタイトルを更新
                existing_title = self._session_titles[user_id][session_id]
                existing_title.title = title
                existing_title.updated_at = datetime.utcnow()
                self.logger.info(f"Updated session title for user {user_id}, session {session_id}")
                return existing_title
            else:
                # タイトルが存在しない場合は新規作成
                return await self.save_session_title(user_id, session_id, title)
        except Exception as e:
            self.logger.error(f"Error updating session title for user_id={user_id}, session_id={session_id}: {str(e)}", exc_info=True)
            raise

    async def delete_session_title(self, user_id: str, session_id: str) -> None:
        """セッションタイトルを削除する"""
        self.logger.info(f"Deleting session title for user {user_id}, session {session_id}")
        try:
            if user_id in self._session_titles and session_id in self._session_titles[user_id]:
                del self._session_titles[user_id][session_id]
                self.logger.info(f"Deleted session title for user_id={user_id}, session_id={session_id}")
            else:
                self.logger.warning(f"No session title found to delete for user_id={user_id}, session_id={session_id}")
        except Exception as e:
            self.logger.error(f"Error deleting session title for user_id={user_id}, session_id={session_id}: {str(e)}", exc_info=True)
            raise 