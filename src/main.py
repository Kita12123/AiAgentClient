"""
エントリーポイント
"""
from dotenv import load_dotenv

import services as sp

# .envファイルを読み込む
load_dotenv()

ai = sp.get_ai_service()

if (__name__ == "__main__"):
    res = ai.request_message("Hello!")
    print("回答1: " + res)
    res = ai.request_message(f"あなたが言ってることを和訳して")
    print("回答2: " + res)