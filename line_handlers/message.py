from linebot.models import TextSendMessage
from utils.referral import register_referral
from .profile import get_user_name

def handle_message(event, line_bot_api):
    user_id = event.source.user_id

    if user_id is None:
        print("❌ user_idがNoneのため終了します。")
        return

    user_message = event.message.text.strip()

    if user_message.startswith("紹介コード:"):
        referral_code = user_message.split(":")[1].strip()

        if register_referral(user_id, referral_code):
            reply_text = f"✅ 紹介コード「{referral_code}」を登録しました！"
        else:
            reply_text = "❌ 無効な紹介コードです。"

    else:
        reply_text = "❓ 紹介コードを入力する場合は「紹介コード:XXXXXX」と送信してください。"

    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
    except Exception as e:
        print(f"❌ メッセージ送信エラー: {e}")