from linebot.models import TextSendMessage
from database import connect_db
from utils.referral_code import generate_referral_code
from line_handlers.coupon import generate_coupon_code, send_coupon
from line_handlers.profile import get_user_name
from spreadsheet import update_spreadsheet
from utils.timezone import get_japan_time

def handle_follow(event, line_bot_api):
    user_id = event.source.user_id
    display_name = get_user_name(user_id, line_bot_api)
    referral_code = generate_referral_code()
    coupon_code = generate_coupon_code()

    # クエリパラメータから紹介コードを取得（BさんがAさんから紹介された場合）
    referred_by_code = event.source.params.get('referral', None) if hasattr(event.source, 'params') else None

    # データベース保存
    conn = connect_db()
    cur = conn.cursor()

    referred_by_id = None
    if referred_by_code:
        cur.execute("SELECT line_id FROM users WHERE referral_code = %s", (referred_by_code,))
        referred = cur.fetchone()
        referred_by_id = referred[0] if referred else None

    cur.execute("""
        INSERT INTO users (line_id, referral_code, display_name, coupon_code, referred_by)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (line_id) DO UPDATE SET display_name=EXCLUDED.display_name
    """, (user_id, referral_code, display_name, coupon_code, referred_by_id))
    conn.commit()
    cur.close()
    conn.close()

    now_japan_time = get_japan_time()

    # スプレッドシートにも保存
    update_spreadsheet(user_id, referral_code, referred_by_id, display_name, None, now_japan_time)

    # Bさんに自動メッセージ（クーポン送信）
    welcome_message = (
        f"🎉 ご登録ありがとうございます、{display_name}さん！\n\n"
        f"クーポンコードはこちらです。\n"
        f"【{coupon_code}】"
    )

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome_message)
    )

    # 紹介した人（Aさん）に感謝メッセージ送信
    if referred_by_id:
        thank_you_message = f"✨ {display_name}さんがあなたの紹介で友だち追加しました！ありがとうございます！"
        line_bot_api.push_message(
            referred_by_id,
            TextSendMessage(text=thank_you_message)
        )