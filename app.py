import os
import json
import psycopg2
import gspread
from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent
import random
import string
from oauth2client.service_account import ServiceAccountCredentials

# 環境変数から設定を取得
DATABASE_URL = os.getenv("DATABASE_URL")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
SHEET_ID = os.getenv("SHEET_ID")  # GoogleスプレッドシートのID
SHEET_NAME = "紹介データ"

# LINE APIの設定
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Flaskアプリの設定
app = Flask(__name__)
app.config["DEBUG"] = True  # デバッグモード有効化

# Google Sheets 認証
def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]
    
    # 環境変数から JSON をロード
    service_account_info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT"))
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)

    client = gspread.authorize(creds)
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    return sheet

# スプレッドシートに紹介データを追加
def update_spreadsheet(user_id, referral_code, referred_by):
    sheet = connect_sheet()
    referred_count = len(sheet.findall(referred_by))
    sheet.append_row([user_id, referral_code, referred_by, referred_count])
    print(f"✅ {user_id} をスプレッドシートに記録しました！")

# データベース接続
def connect_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except Exception as e:
        print(f"❌ データベース接続エラー: {e}")
        return None

# 初回実行時にデータベースを初期化
def init_db():
    conn = connect_db()
    if conn is None:
        print("❌ データベース接続エラー")
        return

    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            line_id TEXT UNIQUE,
            referral_code TEXT,
            referred_by TEXT,
            coupon_sent BOOLEAN DEFAULT FALSE,
            inviter_coupon_sent BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ ユーザーテーブル作成完了")

# Webhookエンドポイント（LINE メッセージ処理）
@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid Signature", 400

    return "OK", 200

# ルートエンドポイント（動作確認用）
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "LINE Bot is running!"})

# `favicon.ico` が `404` になるのを防ぐ
@app.route("/favicon.ico")
def favicon():
    return "", 204  # HTTP 204 No Content を返す

# データベース内のユーザー一覧を取得（デバッグ用）
@app.route("/users", methods=["GET"])
def get_users():
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500

        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()

        cur.close()
        conn.close()

        if not users:
            return jsonify({"message": "No users found"}), 404

        return jsonify(users)

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))