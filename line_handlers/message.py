from linebot.models import TextSendMessage
from utils.referral import register_referral


def handle_message(event, line_bot_api):
    user_message = event.message.text
    user_id = event.source.user_id

    if user_message.startswith("紹介コード:"):
        referral_code = user_message.split(":")[1].strip()
        if register_referral(user_id, referral_code):
            reply_text = f"✅ 紹介コード【{referral_code}】を登録しました！\n特典をお楽しみに！"
        else:
            reply_text = "❌ 無効な紹介コードです。再度ご確認ください。"
    else:
        reply_text = "💡 紹介コードを登録するには、「紹介コード: XXXXXX」と送信してください。"

    # メッセージ返信
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )