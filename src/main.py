"""
エントリーポイント
"""
from dotenv import load_dotenv

import services as sp

# .envファイルを読み込む
load_dotenv()

if (__name__ == "__main__"):
    ai = sp.get_ai_service()
    res = ai.reqMsg("Hello!")
    print("回答1: " + res)
    res = ai.reqMsg(f"あなたが言ってることを和訳して")
    print("回答2: " + res)