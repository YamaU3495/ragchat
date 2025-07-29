from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from .interface import IChatRepo
from .models import ChatMessage
import os
from typing import Optional, List, Dict, Any

class CosmosDBClient(IChatRepo):
    def __init__(self):
        # 環境変数から接続情報を取得
        self.endpoint = os.getenv("COSMOS_ENDPOINT")
        self.key = os.getenv("COSMOS_KEY")
        self.database_name = os.getenv("COSMOS_DATABASE_NAME", "chatdb")
        self.container_name = os.getenv("COSMOS_CONTAINER_NAME", "chats")
        
        # Cosmos DBクライアントの初期化
        self.client = CosmosClient(self.endpoint, self.key)
        self.database = self.client.get_database_client(self.database_name)
        self.container = self.database.get_container_client(self.container_name)

    # IChatRepoインターフェースの実装（まだ実装されていないメソッド）
    async def save_chat_message(self, user_id: str, session_id: str, message: ChatMessage) -> ChatMessage:
        """チャットメッセージを保存し、no割り当て済みのChatMessageを返す"""
        # TODO: 実装が必要
        raise NotImplementedError("This method needs to be implemented")

    async def get_chat_messages(self, user_id: str, session_id: str) -> List[ChatMessage]:
        """セッションIDに紐づくチャットメッセージを取得する"""
        # TODO: 実装が必要
        raise NotImplementedError("This method needs to be implemented")

    async def clear_chat_messages(self, user_id: str, session_id: str) -> None:
        """指定したsession_idの全メッセージを削除する"""
        # TODO: 実装が必要
        raise NotImplementedError("This method needs to be implemented")

    async def delete_chat_message_by_no(self, user_id: str, session_id: str, no: int) -> None:
        """指定されたnoのメッセージを削除する"""
        # TODO: 実装が必要
        raise NotImplementedError("This method needs to be implemented")

    async def get_session_ids(self, user_id: str) -> List[str]:
        """user_idに紐づくすべてのsession_idを取得する"""
        # TODO: 実装が必要
        raise NotImplementedError("This method needs to be implemented")

    def create_chat(self, chat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        チャットデータをCosmos DBに保存する
        
        Args:
            chat_data (Dict[str, Any]): 保存するチャットデータ
            
        Returns:
            Dict[str, Any]: 保存されたチャットデータ
        """
        return self.container.create_item(body=chat_data)

    def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """
        指定されたIDのチャットデータを取得する
        
        Args:
            chat_id (str): 取得するチャットのID
            
        Returns:
            Optional[Dict[str, Any]]: チャットデータ。存在しない場合はNone
        """
        try:
            return self.container.read_item(item=chat_id, partition_key=chat_id)
        except CosmosResourceNotFoundError:
            return None

    def update_chat(self, chat_id: str, chat_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        チャットデータを更新する
        
        Args:
            chat_id (str): 更新するチャットのID
            chat_data (Dict[str, Any]): 更新するチャットデータ
            
        Returns:
            Dict[str, Any]: 更新されたチャットデータ
        """
        return self.container.upsert_item(body=chat_data)

    def delete_chat(self, chat_id: str) -> None:
        """
        チャットデータを削除する
        
        Args:
            chat_id (str): 削除するチャットのID
        """
        self.container.delete_item(item=chat_id, partition_key=chat_id)

    def query_chats(self, query: str, parameters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        クエリを実行してチャットデータを取得する
        
        Args:
            query (str): 実行するクエリ
            parameters (Optional[List[Dict[str, Any]]]): クエリパラメータ
            
        Returns:
            List[Dict[str, Any]]: クエリ結果のリスト
        """
        if parameters:
            return list(self.container.query_items(query=query, parameters=parameters))
        return list(self.container.query_items(query=query))

    def get_all_chats(self) -> List[Dict[str, Any]]:
        """
        すべてのチャットデータを取得する
        
        Returns:
            List[Dict[str, Any]]: チャットデータのリスト
        """
        query = "SELECT * FROM c"
        return list(self.container.query_items(query=query)) 