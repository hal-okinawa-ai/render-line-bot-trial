from linebot.models import TextSendMessage
from config import LINE_ACCESS_TOKEN
from linebot import LineBotApi
from database import connect_db
from spreadsheet import update_spreadsheet

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

def send_coupon(user_id, coupon_type="welcome"):
    if coupon_type == "welcome":
        msg = "🎁 友だち追加ありがとう！クーポンをプレゼント！"
    elif coupon_type == "referred":
        msg = "🎁 紹介ありがとう！特別クーポンをプレゼント！"
    elif coupon_type == "inviter":
        msg = "🎉 3人紹介達成！紹介者向け特典クーポンをどうぞ！"
    else:
        msg = "🎁 クーポンをプレゼント！"

    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=msg))
    except Exception as e:
        print(f"❌ クーポン送信失敗: {e}")

def register_referral(user_id, referral_code):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT line_id FROM users WHERE referral_code = %s", (referral_code,))
    referred_by = cur.fetchone()
    if referred_by:
        referred_by_id = referred_by[0]
        cur.execute("UPDATE users SET referred_by = %s WHERE line_id = %s", (referred_by_id, user_id))
        conn.commit()
        update_spreadsheet(user_id, referral_code, referred_by_id)
        send_coupon(user_id, "referred")

        # 紹介者特典
        cur.execute("SELECT COUNT(*) FROM users WHERE referred_by = %s", (referred_by_id,))
        count = cur.fetchone()[0]
        if count >= 3:
            send_coupon(referred_by_id, "inviter")

        cur.close()
        conn.close()
        return True
    cur.close()
    conn.close()
    return False