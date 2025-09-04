import re
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def create_title_generation_chain(llm):
    """
    LLMを使ったタイトル生成チェーンを作成する
    
    Args:
        llm: 使用するLLMインスタンス
    
    Returns:
        タイトル生成チェーン
    """
    prompt = ChatPromptTemplate.from_template("""
以下のメッセージから、15文字以内の簡潔で分かりやすいタイトルを生成してください。
タイトルは会話の内容を端的に表現し、日本語で記述してください。

メッセージ: {message}

タイトル:
""")
    
    return prompt | llm | StrOutputParser()

def generate_title_from_message_with_llm(message: str, title_chain) -> str:
    """
    LLMを使ってメッセージから15文字以内のタイトルを生成する
    
    Args:
        message: 元のメッセージ
        title_chain: タイトル生成チェーン
    
    Returns:
        生成されたタイトル
    """
    if not message or not message.strip():
        return "新しい会話"
    
    try:
        # LLMでタイトルを生成
        title = title_chain.invoke({"message": message})
        
        # 生成されたタイトルをクリーンアップ
        cleaned_title = re.sub(r'\s+', ' ', title.strip())
        
        # 15文字を超える場合は切り取り
        if len(cleaned_title) > 15:
            cleaned_title = cleaned_title[:15]
            # 最後の単語が途中で切れないように調整
            last_space = cleaned_title.rfind(' ')
            if last_space > 10:  # 10文字以上残る場合のみ
                cleaned_title = cleaned_title[:last_space]
            cleaned_title += "..."
        
        return cleaned_title if cleaned_title else "新しい会話"
        
    except Exception as e:
        # LLM生成に失敗した場合はフォールバック
        print(f"LLM title generation failed: {e}")
        return generate_title_fallback(message)

def generate_title_fallback(message: str, max_length: int = 15) -> str:
    """
    フォールバック用のタイトル生成（LLMが使えない場合）
    
    Args:
        message: 元のメッセージ
        max_length: 最大文字数（デフォルト15）
    
    Returns:
        生成されたタイトル
    """
    if not message or not message.strip():
        return "新しい会話"
    
    # 改行や複数のスペースを単一のスペースに置換
    cleaned_message = re.sub(r'\s+', ' ', message.strip())
    
    # 文字数制限を適用
    if len(cleaned_message) <= max_length:
        return cleaned_message
    
    # 最大文字数で切り取り、最後の単語が途中で切れないように調整
    truncated = cleaned_message[:max_length]
    
    # 最後のスペースの位置を探して、そこまでで切り取り
    last_space = truncated.rfind(' ')
    if last_space > max_length // 2:  # 半分以上が残る場合のみ
        truncated = truncated[:last_space]
    
    # 末尾に「...」を追加（文字数制限内で）
    if len(truncated) + 3 <= max_length:
        truncated += "..."
    
    return truncated
