import random
import string
from linebot.models import TextSendMessage

def generate_coupon_code(length=8):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def send_coupon(line_bot_api, user_id, coupon_code, inviter=False):

    message_text = f"ご登録ありがとうございます！\nクーポンコードはこちらです！\n\n{coupon_code}"

    # coupon_url = "https://your-coupon-page.com"
    # message_text = f"🎁 おめでとうございます！クーポンコードをプレゼントします！\n\n🔗 {coupon_url}\n\nクーポンコード: {coupon_code}"

    if inviter:
        message_text = f"🎉 お友達の紹介ありがとうございます！特別クーポンをプレゼントします！\n\n🔗 {coupon_url}\n\nクーポンコード: {coupon_code}"

    line_bot_api.push_message(user_id, TextSendMessage(text=message_text))