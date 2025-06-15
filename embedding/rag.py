import os
from langchain_openai import AzureChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import chromadb
from langsmith import traceable
from langchain_openai import AzureOpenAIEmbeddings
from dotenv import load_dotenv
from chromadb.config import Settings


# 環境変数の読み込み
load_dotenv()

# 環境変数の設定
# Azure OpenAIの設定
os.environ["AZURE_OPENAI_API_KEY"] = os.getenv("AZURE_OPENAI_API_KEY")
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZURE_OPENAI_ENDPOINT")
# Langsmith
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_TRACING"] = "true"

llm = AzureChatOpenAI(
    openai_api_version="2024-12-01-preview",
    model="gpt-4.1-mini",
    temperature=0,
    max_tokens=800,
    max_retries=2,
    streaming=False,
    openai_api_type="azure"
)

# 埋め込みモデルの設定
embeddings = AzureOpenAIEmbeddings(
    api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version = "2024-10-21",
    azure_endpoint =os.getenv("AZURE_EMBEDDING_ENDPOINT"),
    model="text-embedding-3-small"
)

# プロンプトテンプレートの設定
template = """以下のコンテキストを使用して、質問に答えてください。
コンテキストが質問に答えられない場合は、「申し訳ありませんが、その情報は提供できません」と答えてください。

コンテキスト: {context}

質問: {question}
"""

prompt = ChatPromptTemplate.from_template(template)

@traceable
def main():
    collection_name = "gcas_azure_guide_openai"
    client = chromadb.HttpClient(host='localhost', port=8000, settings=Settings(anonymized_telemetry=False))
    db = Chroma(client=client, embedding_function=embeddings, collection_name=collection_name)

    hypothetical_prompt = ChatPromptTemplate.from_template('''\
次の質問に回答する1文を作成してください｡

質問: {question}
''')
    hypothetical_chain = hypothetical_prompt | llm | StrOutputParser()
    
    retriever = db.as_retriever()
    
    chain = (
        {
            "question": RunnablePassthrough(),
            "context": hypothetical_chain | retriever
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    output = chain.invoke("GCASのAzureのユーザー管理⽅法について教えて")
    print(output)

if __name__ == "__main__":
    main()