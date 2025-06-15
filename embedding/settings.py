import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from langchain_openai import AzureOpenAIEmbeddings
import chromadb
from chromadb.config import Settings as ChromaSettings

load_dotenv()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str = ""
    TAVILY_API_KEY: str
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "agent-book"

    # for Application
    openai_smart_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"
    anthropic_smart_model: str = "claude-3-5-sonnet-20240620"
    temperature: float = 0.0
    default_reflection_db_path: str = "tmp/reflection_db.json"

    def __init__(self, **values):
        super().__init__(**values)
        self._set_env_variables()

    def _set_env_variables(self):
        for key in self.__annotations__.keys():
            if key.isupper():
                os.environ[key] = getattr(self, key)


def get_embedding():
    """
    AzureOpenAIEmbeddingsの共通インスタンスを返す
    """
    return AzureOpenAIEmbeddings(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        azure_endpoint=os.getenv("AZURE_EMBEDDING_ENDPOINT"),
        model=os.getenv("AZURE_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    )


def get_chroma_client(port=None):
    """
    ChromaDB HttpClientの共通インスタンスを返す
    """
    host = os.getenv("CHROMADB_HOST", "localhost")
    port = port if port is not None else int(os.getenv("CHROMADB_PORT", "8001"))
    return chromadb.HttpClient(host=host, port=port, settings=ChromaSettings(anonymized_telemetry=False))


def get_collection(client, collection_name=None, metadata=None):
    """
    コレクションを取得または作成する
    """
    if collection_name is None:
        collection_name = os.getenv("CHROMADB_COLLECTION_NAME", "gcas_azure_guide_nomic-embed-text")
    if metadata is None:
        # metadataはJSON文字列で環境変数から取得できるようにする
        import json
        metadata_str = os.getenv("CHROMADB_COLLECTION_METADATA", '{"url": "https://guide.gcas.cloud.go.jp/azure/"}')
        try:
            metadata = json.loads(metadata_str)
        except Exception:
            metadata = {"url": "https://guide.gcas.cloud.go.jp/azure/"}
    return client.get_or_create_collection(collection_name, metadata=metadata)
