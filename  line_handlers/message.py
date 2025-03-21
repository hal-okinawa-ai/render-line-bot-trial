from linebot.models import TextSendMessage
from config import LINE_ACCESS_TOKEN
from linebot import LineBotApi
from line_handlers.coupon import register_referral

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

def handle_message(event):
    user_id = event.source.user_id
    msg = event.message.text.strip()

    if msg.startswith("紹介コード:"):
        code = msg.split(":")[1].strip()
        if register_referral(user_id, code):
            reply = f"✅ 紹介コード {code} を登録しました！"
        else:
            reply = "❌ 無効な紹介コードです。"
    else:
        reply = "❓ 紹介コードを入力する場合は「紹介コード:ABC123」と送信してください。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply))