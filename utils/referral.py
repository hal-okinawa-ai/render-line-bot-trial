from database import connect_db
from spreadsheet import update_spreadsheet
from line_handlers.profile import get_user_name
from line_handlers.coupon import send_coupon, generate_coupon_code
from utils.timezone import get_japan_time

def register_referral(user_id, referral_code):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT line_id FROM users WHERE referral_code = %s", (referral_code,))
    referred_by = cur.fetchone()

    if referred_by:
        referred_by_id = referred_by[0]

        # 紹介者情報を更新
        cur.execute("UPDATE users SET referred_by = %s WHERE line_id = %s", (referred_by_id, user_id))
        conn.commit()

        # 名前取得
        display_name = get_user_name(user_id)              # 紹介された本人
        inviter_name = get_user_name(referred_by_id)       # 紹介者

        # スプレッドシート更新
        update_spreadsheet(
            user_id, referral_code, referred_by_id, display_name, inviter_name, get_japan_time()
        )

        # クーポンコード生成して紹介された本人に送信
        coupon_code = generate_coupon_code()
        send_coupon(user_id, coupon_code)

        # 紹介者にも送信（1人紹介でOKの場合）
        send_coupon(referred_by_id, generate_coupon_code())

        cur.close()
        conn.close()
        return True

    cur.close()
    conn.close()
    return False