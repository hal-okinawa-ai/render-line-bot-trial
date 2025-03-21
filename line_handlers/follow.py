from linebot.models import TextSendMessage
from config import LINE_ACCESS_TOKEN
from .coupon import generate_coupon_code, send_coupon
from database import connect_db
from utils.referral_code import generate_referral_code
from .profile import get_user_name
from spreadsheet import update_spreadsheet
from linebot import LineBotApi

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

def handle_follow(event):
    user_id = event.source.user_id
    display_name = get_user_name(user_id)
    referral_code = generate_referral_code()
    coupon_code = generate_coupon_code()

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (line_id, referral_code, display_name, coupon_code)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (line_id) DO UPDATE SET display_name = EXCLUDED.display_name
    """, (user_id, referral_code, display_name, coupon_code))

    conn.commit()
    cur.close()
    conn.close()

    # スプレッドシート更新
    update_spreadsheet(user_id, referral_code, None, display_name, None, None)

    # 新規ユーザーへのメッセージ
    welcome_message = (
        f"ご登録ありがとうございます！\n\n"
        f"クーポンコードはこちらです！\n\n"
        f"【{coupon_code}】"
    )

    # この返信処理が必要です
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome_message)
    )

    # クーポンをLINEでも送信
    send_coupon(user_id, coupon_code)