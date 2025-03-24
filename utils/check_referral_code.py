from database import connect_db

def check_referral_code(line_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT referral_code FROM users WHERE line_id = %s", (line_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else None

if __name__ == "__main__":
    user_line_id = '崎山'  # 確認したいユーザーのLINE ID
    referral_code = check_referral_code(user_line_id)
    print(referral_code)