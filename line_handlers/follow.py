from linebot.models import TextSendMessage
from linebot import LineBotApi
from config import LINE_ACCESS_TOKEN
from utils.referral_code import generate_referral_code
from line_handlers.coupon import generate_coupon_code, send_coupon
from database import connect_db
from spreadsheet import update_spreadsheet
from line_handlers.profile import get_user_name
from utils.timezone import get_japan_time

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

def handle_follow(event):
    user_id = event.source.user_id
    referral_code = generate_referral_code()
    coupon_code = generate_coupon_code()
    display_name = get_user_name(user_id)
    now_japan_time = get_japan_time()

    # DBへユーザー情報を保存
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (line_id, referral_code, coupon_code, display_name)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (line_id) DO UPDATE SET display_name = EXCLUDED.display_name, coupon_code = EXCLUDED.coupon_code
    """, (user_id, referral_code, coupon_code, display_name))

    conn.commit()
    cur.close()
    conn.close()

    # スプレッドシートにも記録
    update_spreadsheet(user_id, referral_code, None, display_name, None, now_japan_time)

    welcome_message = (
        f"🎉{display_name}さん、友だち追加ありがとうございます！\n\n"
        f"【あなたの紹介コード】\n{referral_code}\n\n"
        f"🎁【特典クーポンコード】\n{coupon_code}\n\n"
        f"紹介コードを友だちにシェアして特典をゲットしましょう！"
    )

    # LINEでウェルカムメッセージを返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome_message)
    )

    # クーポンコードを送信
    send_coupon(user_id, coupon_code)