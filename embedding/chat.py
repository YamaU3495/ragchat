from langchain_openai import AzureChatOpenAI
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import os
from settings import Settings

def create_azure_chain():
    """
    Azure OpenAI Serviceを使用するLangChainのチェーンを作成する関数
    
    Returns:
        AzureChatOpenAI: LangChainのAzure OpenAIインスタンス
    """
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    
    # 環境変数からAPIキーとエンドポイントを取得
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set")
    os.environ["AZURE_OPENAI_API_KEY"] = api_key
    
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    if not endpoint:
        raise ValueError("AZURE_OPENAI_ENDPOINT environment variable is not set")
    os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint
    
    llm = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt4-deployment"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview"),
        temperature=float(os.getenv("AZURE_OPENAI_TEMPERATURE", "0.5")),
        max_tokens=None,
        timeout=None,
        max_retries=2,
        callback_manager=callback_manager
    )
    
    return llm

def main():
    print("Azure OpenAIチャットを開始します。終了するには 'quit' と入力してください。")
    
    # LangChainのチェーンを作成
    llm = create_azure_chain()
    
    while True:
        user_input = input("\n質問を入力してください: ")
        
        if user_input.lower() == 'quit':
            print("チャットを終了します。")
            break
        
        try:
            # 応答を生成
            messages = [
                ("system", "You are a helpful assistant."),
                ("human", user_input)
            ]
            response = llm.invoke(messages)
            print("\n", response.content)
        except Exception as e:
            print(f"\nエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()
