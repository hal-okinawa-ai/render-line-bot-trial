# utils/referral.py
from database import connect_db
from spreadsheet import update_spreadsheet
from utils.coupon import generate_coupon_code, send_coupon
from utils.profile import get_user_name
from utils.timezone import get_japan_time
from linebot.models import TextSendMessage

def register_referral(user_id, referral_code, line_bot_api):
    conn = connect_db()
    cur = conn.cursor()

    # 紹介コードを持つユーザー（紹介者）を特定
    cur.execute("SELECT line_id FROM users WHERE referral_code = %s", (referral_code,))
    inviter = cur.fetchone()

    if inviter:
        inviter_id = inviter[0]

        # 紹介されたユーザーのデータを更新
        cur.execute("UPDATE users SET referred_by = %s WHERE line_id = %s", (inviter_id, user_id))
        conn.commit()

        # 新規ユーザーのクーポンコード生成
        new_coupon_code = generate_coupon_code()

        # 紹介された人の名前と紹介者の名前を取得
        display_name = get_user_name(user_id, line_bot_api)           # 紹介された本人
        inviter_name = get_user_name(inviter_id, line_bot_api)        # 紹介者の名前

        # 日本時間取得
        japan_time = get_japan_time()

        # スプレッドシートに記録
        update_spreadsheet(user_id, referral_code, inviter_id, display_name, inviter_name, japan_time)

        # 紹介された本人にクーポンを送信
        send_coupon(user_id, new_coupon_code, line_bot_api)

        # 紹介者（inviter）にもお礼メッセージ送信
        thanks_message = f"{inviter_name}さん、紹介ありがとうございます！\n友だちがあなたの紹介コードを利用しました。"
        line_bot_api.push_message(inviter_id, TextSendMessage(text=thanks_message))

        cur.close()
        conn.close()
        return True

    cur.close()
    conn.close()
    return False

# ユーザーの紹介コードを取得
def get_user_referral_code(user_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT referral_code FROM users WHERE line_id = %s", (user_id,))
    result = cur.fetchone()

    cur.close()
    conn.close()

    return result[0] if result else None