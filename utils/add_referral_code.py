from database import connect_db
from utils.referral_code import generate_referral_code

def add_missing_referral_codes():
    conn = connect_db()
    if not conn:
        print("データベース接続に失敗しました")
        return

    cur = conn.cursor()
    cur.execute("SELECT line_id FROM users WHERE referral_code IS NULL OR referral_code = '';")
    users_without_code = cur.fetchall()

    if not users_without_code:
        print("紹介コードがないユーザーはいませんでした")
        return

    for (line_id,) in users_without_code:
        referral_code = generate_referral_code()
        cur.execute("UPDATE users SET referral_code = %s WHERE line_id = %s;", (referral_code, line_id))
        print(f"{line_id} に紹介コード {referral_code} を追加しました")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    add_missing_referral_codes()