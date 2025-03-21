from database import connect_db
from utils.common import generate_referral_code
from line_handlers.profile import get_user_name
from linebot.models import TextSendMessage
from linebot import LineBotApi
from config import LINE_ACCESS_TOKEN

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

def handle_follow(event):
    user_id = event.source.user_id
    referral_code = generate_referral_code()
    display_name = get_user_name(user_id)  # 名前を取得

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (line_id, referral_code, display_name)
        VALUES (%s, %s, %s)
        ON CONFLICT (line_id) DO NOTHING
    """, (user_id, referral_code, display_name))

    conn.commit()
    cur.close()
    conn.close()

    welcome_message = f"🎉 {display_name} さん、友だち追加ありがとうございます！\nあなたの紹介コード: {referral_code}"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_message))