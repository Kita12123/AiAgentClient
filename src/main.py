"""
エントリーポイント
"""
from dotenv import load_dotenv

import services as sp
from flaskr.app import app

# .envファイルを読み込む
load_dotenv()

ai = sp.get_ai_service()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)