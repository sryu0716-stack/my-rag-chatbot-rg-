import os
import google.generativeai as genai
import streamlit as st
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
#from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
#load_dotenv()

# Azure AI Search の設定
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_ADMIN_KEY = os.getenv("AZURE_SEARCH_ADMIN_KEY")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")

# Google Generative AI の設定
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

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

# StreamlitのUIを構築
st.title("RAG チャットボット")

# チャット履歴を保持
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去のチャット履歴を表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ユーザーからの入力を受け付ける
if prompt := st.chat_input("質問を入力してください..."):
    # ユーザーのメッセージを履歴に追加
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            context = search_documents(prompt)
            if context:
                answer = generate_answer(prompt, context)
                st.markdown(answer)
            else:
                st.markdown("申し訳ありません、関連する情報を見つけることができませんでした。")
        st.session_state.messages.append({"role": "assistant", "content": answer})