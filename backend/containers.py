import chromadb
from dependency_injector import containers, providers
from langchain_chroma import Chroma
import os
from db.chat.factory import ChatRepositoryFactory
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings,AzureChatOpenAI

class Container(containers.DeclarativeContainer):
    # 環境変数の読み込み
    load_dotenv()

    # 環境変数から設定ファイルを選択
    config_file = os.getenv("CONFIG_FILE", "config.yml")
    # config_fileの存在チェック
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"設定ファイルが見つかりません: {config_file}")
    
    # 設定ファイルを読み込む
    config = providers.Configuration(yaml_files=[config_file])

    # Embeddings provider
    # embeddings_kwargs = {
    #     "model": config.chroma.embeddings_model
    # }
    # if hasattr(config.llm, "base_url"):
    #     embeddings_kwargs["base_url"] = config.llm.base_url

    # embeddings = providers.Singleton(
    #     OllamaEmbeddings,
    #     **embeddings_kwargs
    # )
    embeddings = providers.Singleton(
        AzureOpenAIEmbeddings,
        api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
        api_version = "2024-10-21",
        azure_endpoint =os.getenv("AZURE_EMBEDDING_ENDPOINT"),
        model="text-embedding-3-small"
    )

    # ChromaDB client provider
    client = providers.Singleton(
        chromadb.HttpClient,
        host=config.chroma.host,
        port=config.chroma.port
    )

    chroma_db = providers.Singleton(
        Chroma,
        collection_name=config.chroma.collection_name,
        embedding_function=embeddings,
        client=client
    )

    # チャット履歴用のリポジトリ（Factory Pattern）
    chat_repository = providers.Singleton(
        ChatRepositoryFactory.create_database,
        db_type=os.getenv("DB_TYPE", "inmemory")
    )

    # LLMプロバイダー
    # llm_kwargs = {
    #     "model": config.llm.model,
    #     "max_tokens": config.llm.max_tokens,
    #     "temperature": config.llm.temperature,
    #     "top_p": config.llm.top_p
    # }
    # if hasattr(config.llm, "base_url"):
    #     llm_kwargs["base_url"] = config.llm.base_url

    # llm = providers.Singleton(
    #     ChatOllama,
    #     **llm_kwargs
    # )

    llm = providers.Singleton(
        AzureChatOpenAI,
        openai_api_version="2024-12-01-preview",
        model="gpt-4.1-mini",
        temperature=0,
        max_tokens=800,
        max_retries=2,
        streaming=False,
        openai_api_type="azure"
    )
