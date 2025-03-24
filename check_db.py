import psycopg2

def connect_db():
    try:
        conn = psycopg2.connect(
            host="dpg-cvd2lgjv2p9s73cautgg-a.singapore-postgres.render.com",
            database="linebot_db_tj6p",
            user="linebot_db_tj6p_user",
            password="anRdxl1sxjmg142KcXxlVzW9p5cqxvrt",
            port=5432,
            sslmode='require'
        )
        return conn
    except Exception as e:
        print(f"❌ DB接続エラー: {e}")
        return None

def show_users():
    conn = connect_db()
    if not conn:
        print("データベース接続に失敗しました")
        return

    cur = conn.cursor()
    cur.execute("""
        SELECT line_id, referral_code, coupon_code, referred_by FROM users;
    """)
    users = cur.fetchall()

    print("✅ ユーザー情報:")
    for user in users:
        print(f"line_id: {user[0]}, referral_code: {user[1]}, coupon_code: {user[2]}, referred_by: {user[3]}")

    cur.close()
    conn.close()

if __name__ == "__main__":
    show_users()