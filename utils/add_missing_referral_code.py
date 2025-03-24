from database import connect_db
from utils.referral_code import generate_referral_code

def add_referral_code(user_line_id):
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        new_referral_code = generate_referral_code()

        cur.execute("""
            UPDATE users SET referral_code = %s WHERE line_id = %s
        """, (new_referral_code, user_line_id))

        conn.commit()
        cur.close()
        conn.close()
        print("✅ 紹介コードを追加しました:", new_referral_code)
    else:
        print("❌ データベース接続に失敗しました")

if __name__ == "__main__":
    user_line_id = "崎山"  # LINEの実際のユーザーIDに置き換える
    add_referral_code(user_line_id)