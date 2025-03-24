import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    try:
        return psycopg2.connect(
            host=os.getenv("DATABASE_HOST"),
            dbname=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            sslmode='require'
        )
    except Exception as e:
        print(f"❌ DB接続エラー: {e}")
        return None

def init_db():
    conn = connect_db()
    if conn is None:
        print("❌ データベースの初期化に失敗しました。")
        return

    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                line_id TEXT PRIMARY KEY,
                referral_code TEXT UNIQUE,
                display_name TEXT,
                coupon_code TEXT,
                referred_by TEXT
            )
        """)
        conn.commit()
        print("✅ データベースを初期化しました。")
    except Exception as e:
        print(f"❌ データベース初期化エラー: {e}")
    finally:
        cur.close()
        conn.close()