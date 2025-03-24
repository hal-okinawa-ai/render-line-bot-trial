from linebot.models import TextSendMessage
from line_handlers.profile import get_user_name
from line_handlers.coupon import generate_coupon_code, send_coupon
from database import connect_db
from spreadsheet import update_spreadsheet
from utils.timezone import get_japan_time

def register_referral(user_id, referral_code, line_bot_api):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT line_id FROM users WHERE referral_code = %s", (referral_code,))
    referred_by = cur.fetchone()

    if referred_by:
        referred_by_id = referred_by[0]

        display_name = get_user_name(user_id, line_bot_api)
        inviter_name = get_user_name(referred_by_id, line_bot_api)

        coupon_code = generate_coupon_code()
        now_japan_time = get_japan_time()

        cur.execute("""
            UPDATE users SET referred_by = %s, coupon_code = %s WHERE line_id = %s
        """, (referred_by_id, coupon_code, user_id))
        conn.commit()

        update_spreadsheet(user_id, referral_code, referred_by_id, display_name, inviter_name, now_japan_time)

        # Bさんにクーポン送信
        send_coupon(line_bot_api, user_id, coupon_code)

        # Aさんに通知を送る
        line_bot_api.push_message(
            referred_by_id,
            TextSendMessage(text=f"🎉 {display_name}さんがあなたの招待コードで友だち追加しました！ご紹介ありがとうございます！")
        )

        cur.close()
        conn.close()
        return True

    cur.close()
    conn.close()
    return False