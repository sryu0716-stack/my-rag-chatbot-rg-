import os
import sys
import google.generativeai as genai
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# Azure AI Search の設定
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")

# Google Generative AI の設定
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not all([AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_ADMIN_KEY, AZURE_SEARCH_INDEX_NAME, GOOGLE_API_KEY]):
    print("必要な環境変数が設定されていません。")
    sys.exit(1)

def search_documents(query):
    """Azure AI Searchでドキュメントを検索する"""
    credential = AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
    search_client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX_NAME,
        credential=credential
    )
    results = search_client.search(search_text=query)
    # 検索結果の関連ドキュメントを結合
    context = ""
    for result in results:
        context += result['content'] + "\n"
    return context

def generate_answer(query, context):
    """検索結果に基づいてGeminiで回答を生成する"""
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    prompt = f"""
    あなたは、提供された情報に基づいて質問に答えるAIアシスタントです。
    以下の情報が与えられています：
    ---
    {context}
    ---
    上記の情報を使い、以下の質問に簡潔に答えてください。
    質問: {query}
    """
    response = model.generate_content(prompt)
    return response.text

def main():
    """チャットボットのメイン関数"""
    print("チャットボットを開始します。終了するには 'exit' または 'quit' と入力してください。")
    while True:
        user_input = input("あなた: ")
        if user_input.lower() in ['exit', 'quit']:
            print("チャットボットを終了します。")
            break
        
        # ドキュメントを検索
        context = search_documents(user_input)
        
        if context:
            # 検索結果に基づいて回答を生成
            answer = generate_answer(user_input, context)
            print(f"チャットボット: {answer}")
        else:
            print("チャットボット: 申し訳ありません、関連する情報を見つけることができませんでした。")

if __name__ == "__main__":
    main()