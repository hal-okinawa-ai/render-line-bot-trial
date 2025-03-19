import os
import psycopg2
from flask import Flask, request, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, FollowEvent
import random
import string

# 環境変数から設定を取得
DATABASE_URL = os.getenv("DATABASE_URL")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# LINE APIの設定
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Flaskアプリの設定
app = Flask(__name__)
app.config["DEBUG"] = True  # デバッグモード有効化

# ルートエンドポイント（動作確認用）
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "LINE Bot is running!"})

# Webhookエンドポイント
@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid Signature", 400

    return "OK", 200

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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ ユーザーテーブル作成完了")

# 紹介コードの生成
def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# ユーザーをデータベースに保存
def save_user(line_id, referral_code, referred_by=None):
    conn = connect_db()
    if conn is None:
        print("❌ データベース接続エラー")
        return
    
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (line_id, referral_code, referred_by)
        VALUES (%s, %s, %s)
        ON CONFLICT (line_id) DO NOTHING
    """, (line_id, referral_code, referred_by))
    
    conn.commit()
    print(f"✅ {line_id} を登録しました（紹介コード: {referral_code}）")
    cur.close()
    conn.close()

# 紹介コードの登録
def register_referral(user_id, referral_code):
    conn = connect_db()
    if conn is None:
        return False

    cur = conn.cursor()
    cur.execute("SELECT line_id FROM users WHERE referral_code = %s", (referral_code,))
    referred_by = cur.fetchone()

    if referred_by:
        cur.execute("UPDATE users SET referred_by = %s WHERE line_id = %s", (referred_by[0], user_id))
        conn.commit()
        cur.close()
        conn.close()
        return True
    else:
        cur.close()
        conn.close()
        return False

# 友だち追加時の処理
@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    referral_code = generate_referral_code()

    # ユーザーをDBに保存
    save_user(user_id, referral_code)

    # メッセージを送信
    welcome_message = f"🎉 友だち追加ありがとうございます！\nあなたの紹介コード: {referral_code}\n\n紹介コードをシェアすると特典がもらえます！"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_message))

# メッセージ受信時の処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    user_id = event.source.user_id

    if user_message.startswith("紹介コード:"):
        referral_code = user_message.split(":")[1].strip()
        
        if register_referral(user_id, referral_code):
            reply_text = "✅ 紹介コードを登録しました！"
        else:
            reply_text = "❌ 無効な紹介コードです"

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
    else:
        reply_text = "❓ 紹介コードを入力する場合は「紹介コード:XXXXXX」と送信してください。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

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

# サーバー起動
if __name__ == "__main__":
    init_db()  # 初回実行時にデータベースを初期化
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))