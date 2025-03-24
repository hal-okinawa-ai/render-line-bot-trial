import psycopg2
import os
from dotenv import load_dotenv
from utils.referral_code import generate_referral_code

# .envファイルから環境変数を読み込む
load_dotenv()

def connect_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            port=os.getenv("DATABASE_PORT", 5432)
        )
        return conn
    except Exception as e:
        print(f"❌ DB接続エラー: {e}")
        return None

def add_missing_referral_codes():
    conn = connect_db()
    if conn is None:
        return

    cur = conn.cursor()

    # referral_codeがNULLまたは空のユーザーを抽出
    cur.execute("SELECT line_id FROM users WHERE referral_code IS NULL OR referral_code = '';")
    users = cur.fetchall()

    # referral_codeを追加
    for user in users:
        line_id = user[0]
        referral_code = generate_referral_code()
        cur.execute(
            "UPDATE users SET referral_code = %s WHERE line_id = %s;",
            (referral_code, line_id)
        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ referral_codeをすべてのユーザーに追加しました。")

if __name__ == "__main__":
    add_missing_referral_codes()