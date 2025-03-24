from database import connect_db
from linebot.models import TextSendMessage
from utils.referral_code import generate_referral_code
from utils.coupon import generate_coupon_code, send_coupon
from utils.profile import get_user_name

def handle_follow(event, line_bot_api):
    user_id = event.source.user_id
    referral_code = generate_referral_code()
    coupon_code = generate_coupon_code()
    display_name = get_user_name(user_id, line_bot_api)

    conn = connect_db()
    cur = conn.cursor()

    # DBに保存
    cur.execute("""
        INSERT INTO users (line_id, referral_code, coupon_code)
        VALUES (%s, %s, %s)
        ON CONFLICT (line_id) DO NOTHING
    """, (user_id, referral_code, coupon_code))

    conn.commit()
    cur.close()
    conn.close()

    # クーポン送信処理
    send_coupon(user_id, coupon_code, line_bot_api)

    welcome_message = f"🎉 {display_name}さん、友だち追加ありがとうございます！\n\nあなたのクーポンコードは【{coupon_code}】です。\n友達紹介URLを知りたい場合は「紹介URLを教えて」と送信してください。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=welcome_message)
    )


# from database import connect_db
# from utils.referral_code import generate_referral_code
# from utils.coupon import generate_coupon_code, send_coupon
# from utils.profile import get_user_name
# from spreadsheet import update_spreadsheet
# from linebot.models import TextSendMessage

# def handle_follow(event, line_bot_api):
#     user_id = event.source.user_id
#     display_name = get_user_name(user_id, line_bot_api)

#     referral_code = generate_referral_code()
#     coupon_code = generate_coupon_code()

#     conn = connect_db()
#     cur = conn.cursor()
#     cur.execute("""
#         INSERT INTO users (line_id, referral_code, display_name, coupon_code)
#         VALUES (%s, %s, %s, %s)
#         ON CONFLICT (line_id) DO UPDATE
#         SET referral_code = EXCLUDED.referral_code,
#             display_name = EXCLUDED.display_name,
#             coupon_code = EXCLUDED.coupon_code;
#     """, (user_id, referral_code, display_name, coupon_code))
#     conn.commit()
#     cur.close()
#     conn.close()

#     # スプレッドシート更新（新規ユーザー）
#     update_spreadsheet(user_id, referral_code, None, display_name, None)

#     # 新規ユーザーへメッセージ
#     welcome_message = f"🎉 {display_name}さん、ご登録ありがとうございます！\n\n" \
#                       f"🎁 クーポンコードはこちらです:【{coupon_code}】\n" \
#                       f"あなたの紹介URLはこちら:\n" \
#                       f"https://line.me/R/ti/p/@your_bot_id?referral={referral_code}\n\n" \
#                       f"友だちにシェアして特典をゲットしましょう！"

#     line_bot_api.reply_message(
#         event.reply_token,
#         TextSendMessage(text=welcome_message)
#     )

#     send_coupon(user_id, coupon_code)