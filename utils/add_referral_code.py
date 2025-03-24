from database import connect_db
from utils.referral_code import generate_referral_code

def add_missing_referral_codes():
    conn = connect_db()
    cur = conn.cursor()

    # referral_codeが登録されていないユーザーを取得
    cur.execute("SELECT line_id FROM users WHERE referral_code IS NULL OR referral_code = ''")
    users_without_referral = cur.fetchall()

    for user in users_without_referral:
        line_id = user[0]
        new_referral_code = generate_referral_code()

        cur.execute(
            "UPDATE users SET referral_code = %s WHERE line_id = %s",
            (new_referral_code, line_id)
        )
        print(f"✅ {line_id}に新しい紹介コード{new_referral_code}を追加しました")

    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    add_missing_referral_codes()