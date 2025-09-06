import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# Flaskアプリケーションの初期化
app = Flask(__name__)

# Azure AI Search の設定
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")

# OpenAI API の設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = "gpt-3.5-turbo" # 好きなモデル名に変更してください

def search_documents(query):
    """Azure AI Searchでドキュメントを検索する"""
    credential = AzureKeyCredential(AZURE_SEARCH_ADMIN_KEY)
    search_client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX_NAME,
        credential=credential
    )
    results = search_client.search(search_text=query)
    context = ""
    for result in results:
        context += result['content'] + "\n"
    return context

def generate_answer(query, context):
    """検索結果に基づいてOpenAIで回答を生成する"""
    client = OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"""
    あなたは、提供された情報に基づいて質問に答えるAIアシスタントです。
    以下の情報が与えられています：
    ---
    {context}
    ---
    上記の情報を使い、以下の質問に簡潔に答えてください。
    質問: {query}
    """
    response = client.chat.completions.create(
        model=OPENAI_MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

@app.route("/")
def index():
    """チャットインターフェースを表示する"""
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    """チャットの応答を処理する"""
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"response": "メッセージがありません。"})
    
    # ドキュメントを検索
    context = search_documents(user_input)
    
    if context:
        # 検索結果に基づいて回答を生成
        answer = generate_answer(user_input, context)
        return jsonify({"response": answer})
    else:
        return jsonify({"response": "申し訳ありません、関連する情報を見つけることができませんでした。"})

if __name__ == "__main__":
    app.run(debug=True)