from database import connect_db
from utils.coupon import send_coupon
from utils.profile import get_user_name
from spreadsheet import update_spreadsheet

def register_referral(user_id, referral_code, line_bot_api):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT line_id FROM users WHERE referral_code = %s", (referral_code,))
    referred_by = cur.fetchone()

    if referred_by:
        referred_by_id = referred_by[0]

        cur.execute("UPDATE users SET referred_by = %s WHERE line_id = %s", (referred_by_id, user_id))
        conn.commit()

        display_name = get_user_name(user_id, line_bot_api)
        inviter_name = get_user_name(referred_by_id, line_bot_api)

        update_spreadsheet(user_id, referral_code, referred_by_id, display_name, inviter_name)

        coupon_code = "NEWUSER123"  # ここで新規ユーザー向けクーポンコードを生成する処理に置き換えてください。
        send_coupon(user_id, coupon_code)

        # 紹介者への通知
        line_bot_api.push_message(
            referred_by_id,
            TextSendMessage(text=f"{inviter_name}さん、ご友人が登録しました！ありがとうございます😊")
        )

        cur.close()
        conn.close()
        return True

    cur.close()
    conn.close()
    return False

# ↓↓↓ 以下を追加する ↓↓↓

def get_user_referral_code(user_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT referral_code FROM users WHERE line_id = %s", (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()

    if result:
        return result[0]
    else:
        return None