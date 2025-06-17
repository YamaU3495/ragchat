import logging
import os

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import chromadb
from langchain_openai import AzureOpenAIEmbeddings
from chromadb.config import Settings

from config import Config

# Load configuration
cfg = Config()

# If MCP_SERVER_PORT is set (e.g., in test environments) and FASTMCP_PORT is not,
# ensure FASTMCP_PORT (used by FastMCP) defaults to MCP_SERVER_PORT.
# This allows overriding the port for testing purposes.
if cfg.mcp_server_port and not cfg.fastmcp_port:
    os.environ.setdefault("FASTMCP_PORT", cfg.mcp_server_port)
elif cfg.fastmcp_port:  # If FASTMCP_PORT is explicitly set, ensure it's used.
    os.environ["FASTMCP_PORT"] = cfg.fastmcp_port


# Create an MCP server instance.
# The server name "Demo" will be used in logging.
server: FastMCP = FastMCP("Demo",host=cfg.fastmcp_host)

# Configure logging.
# The log level is sourced from the Config object.
# Logging is configured after server instance creation to use the server's name.
logging.basicConfig(
    level=cfg.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(server.name)

# Load environment variables from .env file
load_dotenv()
chroma_settings = Settings(
    anonymized_telemetry=False
)
client = chromadb.HttpClient(
    host=os.getenv("CHROMA_HOST", "localhost"),
    port=os.getenv("CHROMA_PORT", "8001"),
    settings=chroma_settings
)
collection_name = os.getenv("CHROMA_COLLECTION_NAME", "gcas_azure_guide_openai")
collection = client.get_or_create_collection(collection_name, metadata={
    "url": "https://guide.gcas.cloud.go.jp/azure/"
})
print(f"Collection count: {collection.count()}")

embeddings = AzureOpenAIEmbeddings(
    api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version = os.getenv("AZURE_EMBEDDING_API_VERSION"),
    azure_endpoint =os.getenv("AZURE_EMBEDDING_ENDPOINT"),
    model=os.getenv("AZURE_EMBEDDING_MODEL")
)

@server.tool()
def search(query: str) -> str:
    """
    ベクトルデータベース（ChromaDB）から、与えられたクエリに最も関連するドキュメントを検索します。

    主な用途:
    - ガイドやナレッジベースから特定の技術情報や手順、FAQを検索したい場合
    - ユーザーからの自然言語の質問に対して、関連する公式ドキュメントや解説を返したい場合
    - RAG（Retrieval-Augmented Generation）用途で、外部知識をLLMに与えたい場合

    返却内容:
    - クエリに対して類似度の高いドキュメント本文（複数件）
    - それぞれのドキュメントのメタデータ（タイトル、URL、見出しなど）
    - 距離（類似度スコア）

    例:
        search("GCASのユーザー管理方法")
        → GCAS公式ガイドの該当ページ本文や、関連する手順・注意点などが返る

    Args:
        query (str): 検索したい内容（日本語・英語どちらも可）
    Returns:
        str: 検索結果のドキュメント本文やメタデータ
    """
    query_embedding = embeddings.embed_query(query)
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=5,
        include=["documents", "metadatas", "distances"]
    )
    if not results["documents"][0]:
        logger.error(f"No results found for query: {query}")
        return
    
    return results['documents'][0]

# Define a 'greeting' resource.
# This resource takes a 'name' from the URI (e.g., greeting://World)
# and returns a personalized greeting string.
@server.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting."""
    logger.debug(f"Resource 'greeting://{name}' accessed")
    greeting = f"Hello, {name}!"
    logger.debug(f"Resource 'greeting://{name}' result: {greeting}")
    return greeting


def main() -> None:
    """Console script entry point for running the MCP server."""
    # Determine the transport mechanism from the MCP_TRANSPORT environment variable,
    # defaulting to "streamable-http".
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    logger.info(
        f"Starting server '{server.name}' with transport '{transport}' using FastMCP.run()"
    )
    # The port is determined by the FASTMCP_PORT environment variable (defaulting to 8000 by FastMCP)
    # or MCP_SERVER_PORT if FASTMCP_PORT is not set (handled at the beginning of the script).
    server.run(transport=transport)


if __name__ == "__main__":
    main()