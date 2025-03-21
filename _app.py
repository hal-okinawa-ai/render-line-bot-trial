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
SHEET_ID = os.getenv("SHEET_ID")
SHEET_NAME = os.getenv("SHEET_NAME", "紹介データ")

# LINE APIの設定
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Flaskアプリの設定
app = Flask(__name__)
app.config["DEBUG"] = True  # デバッグモード有効化

# Google Sheets 認証
def connect_sheet():
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive"]

    service_account_info = os.getenv("GOOGLE_SERVICE_ACCOUNT")

    if service_account_info is None:
        print("❌ 環境変数 GOOGLE_SERVICE_ACCOUNT が設定されていません")
        return None

    try:
        creds_dict = json.loads(service_account_info)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        print(f"🔍 SHEET_ID: {SHEET_ID}, SHEET_NAME: {SHEET_NAME}")  # デバッグ用
        sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
        return sheet
    except gspread.exceptions.WorksheetNotFound:
        print(f"❌ エラー: 指定されたシート '{SHEET_NAME}' が見つかりません。")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")

    return None

# スプレッドシートに紹介データを追加
def update_spreadsheet(user_id, referral_code, referred_by):
    sheet = connect_sheet()

    if sheet is None:
        print("❌ スプレッドシートの接続に失敗しました。データを記録できません。")
        return

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

def get_referred_users_from_sheet(user_id):
    referred_users = get_referred_users_from_sheet(user_id)
    sheet = connect_sheet()
    if sheet is None:
        return {"error": "Google Sheets connection failed"}

    try:
        records = sheet.get_all_records()
        referred_users = [row for row in records if row["紹介者"] == user_id]

        if not referred_users:
            return {"message": "No referred users found"}

        return referred_users

    except Exception as e:
        print(f"❌ Google Sheets 読み込みエラー: {e}")
        return {"error": f"Unexpected error: {str(e)}"}

def get_referred_users_from_google_sheet(user_id):
    referred_users = get_referred_users_from_sheet(user_id)

    return jsonify(referred_users)

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

# 紹介コードの生成
def generate_referral_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# 紹介コードの登録 & クーポン配布
def register_referral(user_id, referral_code):
    conn = connect_db()
    if conn is None:
        return False

    cur = conn.cursor()
    cur.execute("SELECT line_id FROM users WHERE referral_code = %s", (referral_code,))
    referred_by = cur.fetchone()

    if referred_by:
        referred_by_id = referred_by[0]
        cur.execute("UPDATE users SET referred_by = %s WHERE line_id = %s", (referred_by_id, user_id))
        conn.commit()
        update_spreadsheet(user_id, referral_code, referred_by_id)
        send_coupon(user_id)

        cur.execute("SELECT COUNT(*) FROM users WHERE referred_by = %s", (referred_by_id,))
        referral_count = cur.fetchone()[0]

        if referral_count >= 3:
            send_coupon(referred_by_id, inviter=True)

        cur.close()
        conn.close()
        return True
    else:
        cur.close()
        conn.close()
        return False

# クーポンを送る関数
def send_coupon(user_id, inviter=False):
    coupon_url = "https://your-coupon-page.com"
    message_text = f"🎁 おめでとうございます！クーポンをプレゼント！\n\n🔗 {coupon_url}"

    if inviter:
        message_text = f"🎉 3人以上の友だちを紹介しました！\n特別クーポンをプレゼントします！\n\n🔗 {coupon_url}"

    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=message_text))
        print(f"✅ クーポンを {user_id} に送信しました！")
    except Exception as e:
        print(f"❌ クーポン送信エラー: {e}")

# 友だち追加時の処理
@handler.add(FollowEvent)
def handle_follow(event):
    user_id = event.source.user_id
    referral_code = generate_referral_code()
    
    conn = connect_db()
    if conn is None:
        print("❌ データベース接続エラー（ユーザー登録失敗）")
        line_bot_api.push_message(user_id, TextSendMessage(text="🚨 エラーが発生しました。サポートにお問い合わせください。"))
        return

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (line_id, referral_code)
        VALUES (%s, %s)
        ON CONFLICT (line_id) DO NOTHING
    """, (user_id, referral_code))
    
    conn.commit()
    cur.close()
    conn.close()

    print(f"✅ ユーザー登録: {user_id} (紹介コード: {referral_code})")

    welcome_message = f"🎉 友だち追加ありがとうございます！\nあなたの紹介コード: {referral_code}\n\n紹介コードをシェアすると特典がもらえます！"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_message))

# ルートエンドポイント
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "LINE Bot is running!"})

# `favicon.ico` 404を防ぐ
@app.route("/favicon.ico")
def favicon():
    return "", 204

#  紹介された人を取得する
@app.route("/referred_users/<user_id>", methods=["GET"])
def get_referred_users(user_id):
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500

        cur = conn.cursor()
        cur.execute("SELECT line_id, referral_code, created_at FROM users WHERE referred_by = %s", (user_id,))
        referred_users = cur.fetchall()

        cur.close()
        conn.close()

        if not referred_users:
            return jsonify({"message": "No referred users found"}), 404

        # 取得したデータをJSON形式に整形
        result = [{"line_id": row[0], "referral_code": row[1], "created_at": row[2]} for row in referred_users]

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

# `/users` エンドポイント（登録されたユーザーを取得）
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

# Webhookエンドポイント
@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid Signature", 400

    return "OK", 200

# メッセージ受信時の処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    user_id = event.source.user_id

    print(f"📩 受信メッセージ: {user_message} (from {user_id})")

    if user_message.startswith("紹介コード:"):
        referral_code = user_message.split(":")[1].strip()
        print(f"🔍 紹介コード受信: {referral_code} (from {user_id})")

        if register_referral(user_id, referral_code):
            reply_text = f"✅ 紹介コード {referral_code} を登録しました！"
        else:
            reply_text = "❌ 無効な紹介コードです"

    else:
        reply_text = "❓ 紹介コードを入力する場合は「紹介コード:XXXXXX」と送信してください。"

    try:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        print(f"📩 返信メッセージ送信: {reply_text}")
    except Exception as e:
        print(f"❌ LINEメッセージ送信エラー: {e}")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))