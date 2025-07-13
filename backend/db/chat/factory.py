from typing import Optional,Literal
from .interface import IChatRepo
from .inmemory import InMemoryChatRepo
from .mongodb import MongoChatRepo
import os

class ChatRepositoryFactory:
    _instance: Optional[IChatRepo] = None

    @classmethod
    def create_database(
        cls,
        db_type: Literal["inmemory", "mongodb"] = "inmemory",
        **kwargs
    ) -> IChatRepo:
        """
        データベースインスタンスを作成する
        
        Args:
            db_type: データベースの種類 ("inmemory" or "mongodb")
            **kwargs: データベース固有のパラメータ
                - mongodbの場合: db_name, collection_name
                - inmemoryの場合: なし
                
        Returns:
            DatabaseInterface: データベースインスタンス
        """
        if cls._instance is None:
            if db_type == "inmemory":
                cls._instance = InMemoryChatRepo()
            elif db_type == "mongodb":
                host = kwargs.get("host", os.getenv("MONGODB_HOST", "localhost"))
                port = int(kwargs.get("port", os.getenv("MONGODB_PORT", "27017")))
                db_name = kwargs.get("db_name", "chatdb")
                collection_name = kwargs.get("collection_name", "messages")
                cls._instance = MongoChatRepo(host, port, db_name=db_name, collection_name=collection_name)
            else:
                raise ValueError(f"Unknown database type: {db_type}")
        return cls._instance