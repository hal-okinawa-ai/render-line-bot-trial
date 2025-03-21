from linebot.models import TextSendMessage
from config import YOUR_BOT_ID
from .coupon import generate_coupon_code, send_coupon
from database import connect_db
from utils.referral_code import generate_referral_code
from .profile import get_user_name
from spreadsheet import update_spreadsheet


def handle_follow(event, line_bot_api):
    user_id = event.source.user_id
    referral_code = generate_referral_code()
    display_name = get_user_name(user_id)

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

    # スプレッドシートに新規ユーザーを追加
    update_spreadsheet(user_id, referral_code, None, display_name, None)

    welcome_message = (
        f"ご登録ありがとうございます！\n\n"
        f"クーポンコードはこちらです！\n\n"
        f"【{coupon_code}】"
    )

    # welcome_message = (
    #     f"🎉 {display_name}さん、友だち追加ありがとうございます！\n\n"
    #     f"あなたの紹介コード: 【{referral_code}】\n"
    #     f"このコードを友だちにシェアして特典をゲットしましょう！\n\n"
    #     f"🎁 特典クーポンコード: 【{coupon_code}】"
    # )

    # メッセージ送信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome_message)
    )

    # クーポン送信
    send_coupon(user_id, coupon_code)