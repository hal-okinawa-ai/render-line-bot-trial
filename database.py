import os
import psycopg2

def connect_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DATABASE_HOST"),
            dbname=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            port=os.getenv("DATABASE_PORT", "5432"),
            sslmode='require'
        )
        return conn
    except Exception as e:
        print(f"❌ DB接続エラー: {e}")
        return None

# このinit_db関数を追加
def init_db():
    conn = connect_db()
    if conn is None:
        print("❌ データベース初期化エラー")
        return

    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        line_id TEXT PRIMARY KEY,
        referral_code TEXT UNIQUE,
        display_name TEXT,
        coupon_code TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ DB初期化完了")