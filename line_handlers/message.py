# message.py（完成版）

from database import connect_db
from spreadsheet import update_spreadsheet
from line_handlers.profile import get_user_name
from line_handlers.coupon import send_coupon
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot import LineBotApi
from config import LINE_ACCESS_TOKEN

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

# handle_message関数を追加
def handle_message(event):
    user_message = event.message.text
    user_id = event.source.user_id

    if user_message.startswith("紹介コード:"):
        referral_code = user_message.split(":")[1].strip()
        if register_referral(user_id, referral_code):
            reply_text = f"✅ 紹介コード {referral_code} を登録しました！"
        else:
            reply_text = "❌ 無効な紹介コードです"
    else:
        reply_text = "❓ 紹介コードを入力する場合は「紹介コード:XXXXXX」と送信してください。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

# 既存のregister_referral関数（既にアップロードしたコード）
def register_referral(user_id, referral_code):
    conn = connect_db()
    if conn is None:
        print("❌ データベース接続エラー")
        return False

    try:
        cur = conn.cursor()
        cur.execute("SELECT line_id FROM users WHERE referral_code = %s", (referral_code,))
        referred_by = cur.fetchone()

        if referred_by:
            referred_by_id = referred_by[0]

            cur.execute("UPDATE users SET referred_by = %s WHERE line_id = %s", (referred_by_id, user_id))
            conn.commit()

            display_name = get_user_name(user_id)            # 紹介された本人
            inviter_name = get_user_name(referred_by_id)     # 紹介者

            update_spreadsheet(user_id, referral_code, referred_by_id, display_name, inviter_name)
            send_coupon(user_id)

            cur.execute("SELECT COUNT(*) FROM users WHERE referred_by = %s", (referred_by_id,))
            referral_count = cur.fetchone()[0]

            if referral_count >= 3:
                send_coupon(referred_by_id, inviter=True)

            return True

    except Exception as e:
        print(f"❌ 紹介処理エラー: {e}")
        return False

    finally:
        cur.close()
        conn.close()

    return False