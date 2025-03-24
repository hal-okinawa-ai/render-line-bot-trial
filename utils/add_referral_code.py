from database import connect_db
from utils.referral_code import generate_referral_code

def add_referral_code(user_id):
    referral_code = generate_referral_code()

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users SET referral_code = %s WHERE line_id = %s
    """, (referral_code, user_id))

    conn.commit()
    cur.close()
    conn.close()

    return referral_code

# 例: 特定ユーザーに付与する場合
user_id = 'あなたのLINEユーザーID'
code = add_referral_code(user_id)
print(f'新しく設定された紹介コード: {code}')