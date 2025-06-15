import os
from langchain_openai import AzureChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import chromadb
from langsmith import traceable
from langchain_openai import AzureOpenAIEmbeddings
from settings import get_embedding, get_chroma_client, get_collection


llm = AzureChatOpenAI(
    openai_api_version="2024-12-01-preview",
    model="gpt-4.1-mini",
    temperature=0,
    max_tokens=800,
    max_retries=2,
    streaming=False,
    openai_api_type="azure"
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
    client = get_chroma_client()  # settings.pyのデフォルト（環境変数）を利用
    db = Chroma(client=client, embedding_function=get_embedding(), collection_name=None)  # collection_nameもデフォルト

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