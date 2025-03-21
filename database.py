import psycopg2
from config import DATABASE_URL

def connect_db():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"❌ DB接続エラー: {e}")
        return None

def init_db():
    conn = connect_db()
    if conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                line_id TEXT UNIQUE,
                referral_code TEXT,
                referred_by TEXT,
                display_name TEXT,
                coupon_sent BOOLEAN DEFAULT FALSE,
                inviter_coupon_sent BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("✅ DB初期化完了")