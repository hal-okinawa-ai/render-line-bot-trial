from linebot.models import TextSendMessage
from coupon import generate_coupon_code, send_coupon
from database import connect_db
from utils.referral_code import generate_referral_code
from linebot import LineBotApi
from config import LINE_ACCESS_TOKEN
from datetime import datetime, timezone, timedelta

line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)

def handle_follow(event):
    user_id = event.source.user_id
    profile = line_bot_api.get_profile(user_id)
    display_name = profile.display_name

    # 紹介コードとクーポンコードの生成
    referral_code = generate_referral_code()
    coupon_code = generate_coupon_code()

    # 日本時間の取得
    japan_time = datetime.now(timezone(timedelta(hours=9)))

    # データベースにユーザー情報を保存
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (line_id, display_name, referral_code, coupon_code, created_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (line_id) DO NOTHING
    """, (user_id, display_name, referral_code, coupon_code, japan_time))

    conn.commit()
    cur.close()
    conn.close()

    print(f"✅ ユーザー登録完了: {display_name} ({user_id}), 紹介コード: {referral_code}, クーポンコード: {coupon_code}")

    # ウェルカムメッセージとクーポン送信
    welcome_message = (
        f"🎉 友だち追加ありがとうございます、{display_name}さん！\n\n"
        f"あなたの紹介コード: 【{referral_code}】\n"
        f"お友達を紹介すると特典があります！\n\n"
        f"🎁 クーポンコード：【{coupon_code}】をプレゼント！\n"
        "🔗 https://your-coupon-page.com"
    )

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=welcome_message))