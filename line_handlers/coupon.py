from linebot import LineBotApi
from linebot.models import TextSendMessage
from config import LINE_ACCESS_TOKEN

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

def send_coupon(user_id, inviter=False):
    coupon_url = "https://your-coupon-page.com"
    message_text = f"🎁 おめでとうございます！クーポンをプレゼント！\n\n🔗 {coupon_url}"

    if inviter:
        message_text = f"🎉 3人以上の友だちを紹介しました！\n特別クーポンをプレゼントします！\n\n🔗 {coupon_url}"

    try:
        line_bot_api.push_message(user_id, TextSendMessage(text=message_text))
        print(f"✅ クーポンを {user_id} に送信しました！")
    except Exception as e:
        print(f"❌ クーポン送信エラー: {e}")