# follow.py
from linebot.models import FollowEvent, TextSendMessage
from linebot import LineBotApi
from config import LINE_ACCESS_TOKEN
from database import connect_db
from utils.referral_code import generate_referral_code
from .profile import get_user_name

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

def handle_follow(event: FollowEvent):
    user_id = event.source.user_id
    display_name = get_user_name(user_id)
    referral_code = generate_referral_code()

    conn = connect_db()
    if conn is None:
        print("❌ DB接続エラー")
        return

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (line_id, referral_code, display_name)
        VALUES (%s, %s, %s)
        ON CONFLICT (line_id) DO NOTHING
    """, (user_id, referral_code, display_name))

    conn.commit()
    cur.close()
    conn.close()

    # 招待URLを作成（実際のあなたのBotのIDに置き換えてください）
    invite_url = f"https://line.me/R/ti/p/@558hsyof?referral_code={referral_code}"

    # メッセージに招待用URLを追加
    welcome_message = (
        f"🎉 {display_name}さん、友だち追加ありがとうございます！\n\n"
        f"🔗 あなた専用の紹介URLはこちらです👇\n{invite_url}\n\n"
        "友だちにシェアして特典をゲットしましょう！"
    )

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_message))