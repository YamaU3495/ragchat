import time
import os
from langchain_community.document_loaders import WebBaseLoader
from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup
import html2text
from langchain_text_splitters import CharacterTextSplitter, MarkdownHeaderTextSplitter, TextSplitter, TokenTextSplitter
import chromadb
from langchain_chroma import Chroma
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv
from chromadb.config import Settings
from settings import get_embedding, get_chroma_client, get_collection


class WebPageMetadata(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    last_modified: Optional[datetime] = None
    content: str
    headers: Optional[dict] = None

class WebPageContent(BaseModel):
    metadata: WebPageMetadata
    html_content: str

class CustomWebLoader(WebBaseLoader):
    def __init__(self, wait_selector="main", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wait_selector = wait_selector

    async def _load(self, urls):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            documents = []
            
            for url in urls:
                await page.goto(url)
                await asyncio.sleep(3)
                await page.wait_for_selector(self.wait_selector, timeout=10000)
                
                # ページのメタデータを取得
                title = await page.title()
                description = await page.evaluate('''() => {
                    const meta = document.querySelector('meta[name="description"]');
                    return meta ? meta.content : null;
                }''')
                
                # 最終更新日を取得
                last_modified = await page.evaluate('''() => {
                    const meta = document.querySelector('meta[property="article:modified_time"]');
                    return meta ? meta.content : null;
                }''')
                
                # ヘッダー情報を取得
                headers = await page.evaluate('''() => {
                    const headers = {};
                    document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(header => {
                        headers[header.tagName] = header.textContent;
                    });
                    return headers;
                }''')
                
                content = await page.content()
                
                # WebPageContentオブジェクトを作成
                page_content = WebPageContent(
                    metadata=WebPageMetadata(
                        url=url,
                        title=title,
                        description=description,
                        last_modified=datetime.fromisoformat(last_modified) if last_modified else None,
                        content=content,
                        headers=headers
                    ),
                    html_content=content
                )
                
                documents.append(page_content)

            await browser.close()
            return documents

def extract_main_content(html_content):
    """Extract main content from HTML and convert to Markdown"""
    soup = BeautifulSoup(html_content, 'html.parser')
    main_content = soup.find('main')
    if main_content:
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        return h.handle(str(main_content))
    return ""

def create_documents(web_pages: List[WebPageContent]):
    """Create documents with main content converted to Markdown and split by headers"""
    documents = []
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2")
    ]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    for web_page in web_pages:
        markdown_content = extract_main_content(web_page.html_content)
        #マークダウンをファイルとして出力(ファイル名はタイトルからWindowsのパスに利用できないものを除去)
        invalid_chars = str.maketrans('', '', '\\/:*?"<>|')
        file_name = web_page.metadata.title.translate(invalid_chars)
        with open(f"./output/{file_name}.md", "w", encoding="utf-8") as f:
            f.write(markdown_content)
        # Markdownをヘッダーに基づいて分割
        split_docs = text_splitter.split_documents(markdown_splitter.split_text(markdown_content))
        # 各分割されたドキュメントにメタデータを追加
        for doc in split_docs:
            doc.metadata.update({
                'source': web_page.metadata.url,
                'url': web_page.metadata.url,
                'title': web_page.metadata.title or "No title",
                'description': web_page.metadata.description or "No description",
                'last_modified': web_page.metadata.last_modified.isoformat() if web_page.metadata.last_modified else "",
                'headers': str(web_page.metadata.headers) if web_page.metadata.headers else "{}"
            })
            documents.append(doc)
    
    return documents

# 使用例
async def get_gcas_pages():
    urls = [
      "https://guide.gcas.cloud.go.jp/azure/description-of-project-structure/",
      "https://guide.gcas.cloud.go.jp/azure/how-to-manage-users",
      "https://guide.gcas.cloud.go.jp/azure/how-to-ask-helpdesk",
      "https://guide.gcas.cloud.go.jp/azure/how-to-connect-network",
      "https://guide.gcas.cloud.go.jp/azure/apply-delivery-pipeline",
      "https://guide.gcas.cloud.go.jp/azure/implementing-quantitative-measurement",
      "https://guide.gcas.cloud.go.jp/azure/description-of-preventive-controls",
      "https://guide.gcas.cloud.go.jp/azure/description-of-detective-controls",
      "https://guide.gcas.cloud.go.jp/azure/tips-on-regulatory-compliance",
      "https://guide.gcas.cloud.go.jp/azure/cost-optimization",
      "https://guide.gcas.cloud.go.jp/azure/how-to-migrate-system",
      "https://guide.gcas.cloud.go.jp/azure/know-how-replatform-migrate-system",
      "https://guide.gcas.cloud.go.jp/azure/know-how-replatform-migrate-db",
      "https://guide.gcas.cloud.go.jp/azure/know-how-replatform-object-storage",
      "https://guide.gcas.cloud.go.jp/azure/know-how-replatform-migrate-operation-and-maintenance",
      "https://guide.gcas.cloud.go.jp/azure/how-to-link-systems",
      "https://guide.gcas.cloud.go.jp/azure/how-to-operate-cloud-service",
      "https://guide.gcas.cloud.go.jp/azure/security-tech",
      "https://guide.gcas.cloud.go.jp/azure/sso-transition"
    ]

    loader = CustomWebLoader()
    web_pages = await loader._load(urls)
    documents = create_documents(web_pages)
    
    return documents

def store_documents_in_chroma(documents, collection_name: str, embeddings_model: chromadb.Embeddings):
    """
    Store documents in ChromaDB with specified embedding model and collection name.
    
    Args:
        documents: List of documents to store
        collection_name: Name of the ChromaDB collection
        embeddings_model: Type of embedding model to use ("openai" or "ollama")
    """
    client = chromadb.HttpClient(host='localhost', port=8001, settings=Settings(anonymized_telemetry=False))
    
    # Delete existing collection if it exists
    try:
        client.delete_collection(collection_name)
    except:
        pass

    # バッチサイズと待機時間の設定
    BATCH_SIZE = 2  # 一度に処理するドキュメント数
    WAIT_TIME = 2   # バッチ間の待機時間（秒）

    # ドキュメントをバッチに分割
    for i in range(0, len(documents), BATCH_SIZE):
        batch = documents[i:i + BATCH_SIZE]
        
        # バッチのドキュメントを保存
        db = Chroma.from_documents(
            batch,
            embeddings_model,
            collection_name=collection_name,
            client=client,
            collection_metadata={"url": "https://guide.gcas.cloud.go.jp/azure/"}
        )
        
        # バッチ間で待機
        if i + BATCH_SIZE < len(documents):
            print(f"Processed {i + len(batch)}/{len(documents)} documents. Waiting {WAIT_TIME} seconds...")
            time.sleep(WAIT_TIME)
    
    # 最終的な確認
    collection = client.get_collection(name=collection_name)
    print(f"Added {len(documents)} documents to ChromaDB collection '{collection_name}'")
    print(f"Collection count: {collection.count()}")
    
    return collection

if __name__ == "__main__":
    documents = asyncio.run(get_gcas_pages())  # デフォルトでファイルから読み込む
    # settings.pyで自動的に環境変数がセットされるため不要

    openai_collection = store_documents_in_chroma(
        documents,
        collection_name=os.getenv("CHROMADB_COLLECTION_NAME", "gcas_azure_guide_openai"),
        embeddings_model=get_embedding()
    )