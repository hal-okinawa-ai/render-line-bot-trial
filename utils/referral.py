from database import connect_db
from spreadsheet import update_spreadsheet
from line_handlers.profile import get_user_name
from line_handlers.coupon import send_coupon

def register_referral(user_id, referral_code):
    conn = connect_db()
    cur = conn.cursor()

    # 紹介者を取得
    cur.execute("SELECT line_id FROM users WHERE referral_code = %s", (referral_code,))
    referred_by = cur.fetchone()

    if referred_by:
        referred_by_id = referred_by[0]

        # 紹介された人の紹介者を登録（まだ未登録の場合のみ）
        cur.execute("UPDATE users SET referred_by = %s WHERE line_id = %s AND referred_by IS NULL", (referred_by_id, user_id))
        conn.commit()

        # 本人と紹介者の名前を取得
        display_name = get_user_name(user_id)
        inviter_name = get_user_name(referred_by_id)

        # 必ず新規行としてスプレッドシートを更新（重複回避なし）
        update_spreadsheet(user_id, referral_code, referred_by_id, display_name, inviter_name)

        # 紹介された本人にクーポンを送信
        send_coupon(user_id)

        # 紹介者の人数をカウント
        cur.execute("SELECT COUNT(*) FROM users WHERE referred_by = %s", (referred_by_id,))
        referral_count = cur.fetchone()[0]

        # 1人以上紹介した時点でクーポンを送信
        if referral_count >= 1:
            send_coupon(referred_by_id, inviter=True)

        cur.close()
        conn.close()
        return True

    cur.close()
    conn.close()
    return False