from linebot.models import TextSendMessage  # ←追加
from utils.referral import register_referral

def handle_message(event, line_bot_api):
    user_id = event.source.user_id
    referral_code = event.message.text.strip()

    # user_idの値を確認
    print(f"✅ user_id: {user_id}, referral_code: {referral_code}")

    if user_id:
        if register_referral(user_id, referral_code, line_bot_api):
            reply_text = "紹介コードが登録されました！"
        else:
            reply_text = "紹介コードが無効です。"
    else:
        reply_text = "ユーザーIDを取得できませんでした。再度お試しください。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))