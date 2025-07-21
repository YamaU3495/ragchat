import uuid
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from pydantic import BaseModel, Field
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from containers import Container
from typing import List, Dict
from langsmith import traceable
from logging import getLogger
from db.chat.models import ChatMessage

class DatabaseHistory(BaseChatMessageHistory):
    def __init__(self, messages: List[BaseMessage] = None):
        super().__init__()
        self._messages = messages or []
    
    @property
    def messages(self) -> List[BaseMessage]:
        """Get all messages"""
        return self._messages
    
    def add_messages(self, messages: list[BaseMessage]) -> None:
        """Add a list of messages to the store"""
        self._messages.extend(messages)

    def clear(self) -> None:
        """Clear all messages"""
        self._messages = []

class ChatManager:
    def __init__(self, container: Container):
        self.logger = getLogger("uvicorn.app")
        self.chat_repository = container.chat_repository()
        
        hypothetical_prompt = ChatPromptTemplate.from_template('''\
        次の質問に回答する1文を作成してください｡

        質問: {input}
        ''')
        hypothetical_chain = hypothetical_prompt | container.llm() | StrOutputParser()
        
        # プロンプトテンプレートの設定
        prompt = ChatPromptTemplate.from_messages([
           ("system", """
あなたは親切で丁寧な日本語アシスタントです。
以下のガイドラインに従って回答してください：

1. 与えられたコンテキスト情報に基づいて、正確な情報を提供してください
2. 回答の最後には、使用した情報源を明記してください
3. 外部検索結果が質問内容に沿っていた場合は参考にしてください。

外部検索結果:
'''
{rag_context}
'''
"""
            ),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])

        # RAG用のベクトルデータベース設定
        retriever = container.chroma_db().as_retriever()

        # チェーンの設定
        self.chain = (
            {
                "rag_context":  hypothetical_chain | retriever,
                "input": lambda x: x["input"],
                "history": lambda x: x["history"]
            }
            | prompt
            | container.llm()
        )

    async def _load_messages(self, user_id: str, session_id: str) -> List[BaseMessage]:
        """Load messages from database for a session"""
        db_messages = await self.chat_repository.get_chat_messages(user_id, session_id)
        messages = []
        for msg in db_messages:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
        return messages

    async def _save_messages(self, user_id: str, session_id: str, messages: List[BaseMessage]) -> List[ChatMessage]:
        """Save messages to database for a session"""
        self.logger.info(f"Saving messages for user {user_id}, session {session_id}")
        self.logger.info(f"Messages count: {len(messages)}")
        saved_messages = []
        for message in messages:
            if isinstance(message, HumanMessage):
                saved_messages.append(await self.chat_repository.save_chat_message(user_id, session_id, ChatMessage(no=0, role="user", content=message.content)))
            elif isinstance(message, AIMessage):
                saved_messages.append(await self.chat_repository.save_chat_message(user_id, session_id, ChatMessage(no=0, role="assistant", content=message.content)))
        return saved_messages

    @traceable
    async def get_response(self, message: str, user_id: str, session_id: str) -> List[ChatMessage]:
        """
        Get a response from the LLM based on the input message.
        Returns:
            ChatMessage: The latest assistant message (with no, role, content)
        """
        if message == "":
            raise ValueError("message is empty")
        if user_id == "":
            raise ValueError("user_id is empty")
        if session_id == "":
            raise ValueError("session_id is empty")

        # メッセージ履歴を取得
        history = DatabaseHistory()
        # DBからメッセージを読み込む
        self.logger.info(f"Loading messages for db with user_id: {user_id}, session_id: {session_id}")
        messages = await self._load_messages(user_id, session_id)
        history.add_messages(messages)
        self.logger.info(f"Loaded {len(messages)} messages")

        def get_memory(_):
            return history
        chain_with_history = RunnableWithMessageHistory(
            self.chain,
            get_memory,
            input_messages_key="input",
            history_messages_key="history"
        )
        self.logger.info(f"Invoking chain with history with user_id: {user_id}, session_id: {session_id}")
        response = chain_with_history.invoke(
            {"input": message},
            config={"configurable": {"session_id": session_id}}
        )
        self.logger.info(f"History messages count: {len(history.messages)}")
        # メッセージをDBに保存
        current_messages = DatabaseHistory()
        current_messages.add_messages([
            HumanMessage(content=message), 
            AIMessage(content=response.content)
        ])
        return await self._save_messages(user_id, session_id, current_messages.messages)

    async def clear_memory(self, user_id: str, session_id: str = "default"):
        """
        Clear the conversation memory for a specific session.
        
        Args:
            user_id (str): User identifier
            session_id (str, optional): Session identifier
        """
        await self.chat_repository.clear_chat_messages(user_id, session_id)