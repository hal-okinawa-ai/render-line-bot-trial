from database import connect_db
from utils.referral_code import generate_referral_code

def add_referral_code(user_line_id):
    conn = connect_db()
    cur = conn.cursor()

    # referral_codeを生成
    referral_code = generate_referral_code()

    # データベースに追加
    cur.execute("""
        UPDATE users SET referral_code = %s WHERE line_id = %s
    """, (referral_code, user_line_id))

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ ユーザー {user_line_id} に紹介コード【{referral_code}】を追加しました。")

# ここにユーザーIDを指定
user_line_id = '崎山'
add_referral_code(user_line_id)