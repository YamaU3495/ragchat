from langchain_ollama import OllamaEmbeddings
import chromadb
import numpy as np
from langchain_openai import OpenAIEmbeddings

client = chromadb.HttpClient(host='localhost', port=8000)
collection_name = "gcas_azure_guide_nomic-embed-text"
collection = client.get_or_create_collection(collection_name, metadata={
    "url": "https://guide.gcas.cloud.go.jp/azure/"
})

# コレクションの情報を表示
print(f"Collection count: {collection.count()}")

# 検索クエリの埋め込みを生成
query = "ユーザー管理方法"
query_embedding = embeddings.embed_query(query)
print(f"Query embedding shape: {np.array(query_embedding).shape}")

# 検索を実行
results = collection.query(
    query_embeddings=query_embedding,
    n_results=10,
    include=["documents", "metadatas", "distances"]
)

# 結果の詳細を表示
print(f"\nNumber of results: {len(results['documents'][0])}")

if not results["documents"][0]:
    print("ヒットしませんでした")
else:
    for i in range(len(results["documents"][0])):
        print(f"\nResult {i+1}:")
        print(f"Content: {results['documents'][0][i][:200]}...")  # 最初の200文字のみ表示
        print(f"Metadata: {results['metadatas'][0][i]}")
        print(f"Distance: {results['distances'][0][i] if 'distances' in results else 'N/A'}")
        print("-"*100)