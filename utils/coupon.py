# utils/coupon.py
import random
import string
from linebot.models import TextSendMessage

# クーポンコードを生成する処理
def generate_coupon_code(length=8):
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# クーポンコードを送信する処理
def send_coupon(user_id, coupon_code, line_bot_api):
    message = f"🎁 ご登録ありがとうございます！\nクーポンコードはこちらです。\n\n【{coupon_code}】"
    line_bot_api.push_message(user_id, TextSendMessage(text=message))