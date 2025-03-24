from linebot.models import TextSendMessage
from database import connect_db
from config import YOUR_BOT_ID

# 自分の紹介コードを取得する関数
def get_user_referral_code(user_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT referral_code FROM users WHERE line_id = %s", (user_id,))
    referral_code = cur.fetchone()
    cur.close()
    conn.close()
    return referral_code[0] if referral_code else None

# 紹介URLを返信する処理
def send_referral_url(event, line_bot_api):
    user_id = event.source.user_id
    referral_code = get_user_referral_code(user_id)

    if referral_code:
        referral_url = f"https://line.me/R/ti/p/@558hsyof?referral={referral_code}"
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"🎁紹介URLはこちらです:\n{referral_url}\n\n友だちにシェアして特典をゲットしましょう！")
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="⚠️ 紹介コードが見つかりませんでした。")
        )

# メッセージイベント処理（テキストで特定キーワードが送られた時の処理）
def handle_message(event, line_bot_api):
    user_message = event.message.text

    if user_message in ["友だちを紹介する", "紹介URLを教えて"]:
        send_referral_url(event, line_bot_api)
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="申し訳ありませんが、対応できないメッセージです。")
        )