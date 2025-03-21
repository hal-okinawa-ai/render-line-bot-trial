# message.py
from utils.referral import register_referral

def handle_message(event, line_bot_api):
    user_message = event.message.text
    user_id = event.source.user_id

    if user_message.startswith("紹介コード:"):
        referral_code = user_message.split(":")[1].strip()
        if register_referral(user_id, referral_code, line_bot_api):
            reply_text = f"✅ 紹介コード {referral_code} を登録しました！"
        else:
            reply_text = "❌ 無効な紹介コードです"
    else:
        reply_text = "❓ 紹介コードを入力する場合は「紹介コード:XXXXXX」と送信してください。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))