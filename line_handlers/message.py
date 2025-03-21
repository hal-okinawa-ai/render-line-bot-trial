from database import connect_db
from spreadsheet import update_spreadsheet
from line_handlers.profile import get_user_name
from line_handlers.coupon import send_coupon

def register_referral(user_id, referral_code):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT line_id FROM users WHERE referral_code = %s", (referral_code,))
    referred_by = cur.fetchone()

    if referred_by:
        referred_by_id = referred_by[0]
        cur.execute("UPDATE users SET referred_by = %s WHERE line_id = %s", (referred_by_id, user_id))
        conn.commit()

        display_name = get_user_name(user_id)
        update_spreadsheet(user_id, referral_code, referred_by_id, display_name)  # ←名前追加

        send_coupon(user_id)

        cur.execute("SELECT COUNT(*) FROM users WHERE referred_by = %s", (referred_by_id,))
        referral_count = cur.fetchone()[0]

        if referral_count >= 3:
            send_coupon(referred_by_id, inviter=True)

        cur.close()
        conn.close()
        return True

    cur.close()
    conn.close()
    return False