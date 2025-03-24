from database import connect_db
from utils.referral_code import generate_referral_code

# ユーザーのreferral_codeが無い場合に追加する処理
def add_missing_referral_code(user_line_id):
    conn = connect_db()
    cur = conn.cursor()

    # referral_codeが存在するかを確認
    cur.execute("SELECT referral_code FROM users WHERE line_id = %s", (user_line_id,))
    existing_code = cur.fetchone()

    # referral_codeが未登録なら新規発行して追加
    if existing_code is None or existing_code[0] is None:
        referral_code = generate_referral_code()
        cur.execute("""
            UPDATE users
            SET referral_code = %s
            WHERE line_id = %s
        """, (referral_code, user_line_id))
        conn.commit()
        print(f"✅ ユーザー {user_line_id} に紹介コードを追加しました: {referral_code}")
    else:
        print(f"ℹ️ ユーザー {user_line_id} には既に紹介コードがあります: {existing_code[0]}")

    cur.close()
    conn.close()

# 実行確認用コード（直接実行する場合のみ）
if __name__ == "__main__":
    test_user_id = "ここに確認したいユーザーのLINE_IDを入れる"
    add_missing_referral_code(test_user_id)