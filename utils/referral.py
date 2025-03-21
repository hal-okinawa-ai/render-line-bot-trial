from utils.referral_code import generate_referral_code
from database import connect_db
from spreadsheet import update_spreadsheet
from line_handlers.profile import get_user_name
from line_handlers.coupon import send_coupon
from linebot import LineBotApi
from config import LINE_ACCESS_TOKEN, YOUR_BOT_ID
from linebot.models import TextSendMessage

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

def register_referral(user_id, referral_code):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT line_id FROM users WHERE referral_code = %s", (referral_code,))
    referred_by = cur.fetchone()

    if referred_by:
        referred_by_id = referred_by[0]

        cur.execute("UPDATE users SET referred_by = %s WHERE line_id = %s", (referred_by_id, user_id))

        # 名前取得
        display_name = get_user_name(user_id)
        inviter_name = get_user_name(referred_by_id)

        # 新しい招待コード発行
        new_referral_code = generate_referral_code()
        cur.execute("UPDATE users SET referral_code = %s WHERE line_id = %s", (new_referral_code, user_id))
        conn.commit()

        # スプレッドシート更新（名前含む）
        update_spreadsheet(user_id, referral_code, referred_by_id, display_name, inviter_name)

        # 紹介された人への招待URLを送信
        invite_url = f"https://line.me/R/ti/p/@{YOUR_BOT_ID}?referral_code={new_referral_code}"

        message_text = (
            f"🎁 {display_name}さん、登録ありがとうございます！クーポンをお届けします！\n\n"
            f"✅ あなたの招待コード：{new_referral_code}\n\n"
            f"友だちに共有すると追加特典がもらえます！\n"
            f"🔗 招待URL: {invite_url}"
        )
        line_bot_api.push_message(user_id, TextSendMessage(text=message_text))

        # クーポン送信
        send_coupon(user_id)

        cur.execute("SELECT COUNT(*) FROM users WHERE referred_by = %s", (referred_by_id,))
        referral_count = cur.fetchone()[0]

        # 紹介者に特別クーポン（3人以上）
        if referral_count >= 3:
            send_coupon(referred_by_id, inviter=True)

        cur.close()
        conn.close()
        return True

    cur.close()
    conn.close()
    return False