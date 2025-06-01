from typing import Optional,Literal
from .interface import IChatRepo
from .inmemory import InMemoryChatRepo

class ChatRepositoryFactory:
    _instance: Optional[IChatRepo] = None

    @classmethod
    def create_database(
        cls,
        db_type: Literal["inmemory"] = "inmemory",
        **kwargs
    ) -> IChatRepo:
        """
        データベースインスタンスを作成する
        
        Args:
            db_type: データベースの種類 ("inmemory")
            **kwargs: データベース固有のパラメータ
                - hogeの場合: db_path (str)
                
        Returns:
            DatabaseInterface: データベースインスタンス
        """
        if cls._instance is None:
            if db_type == "inmemory":
                cls._instance = InMemoryChatRepo()
            else:
                raise ValueError(f"Unknown database type: {db_type}")
        return cls._instance