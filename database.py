import os
import psycopg2

def connect_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DATABASE_HOST"),
            dbname=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            port=os.getenv("DATABASE_PORT", "5432"),  # ← Renderの場合はポートが必要
            sslmode='require'
        )
        return conn
    except Exception as e:
        print(f"❌ DB接続エラー: {e}")
        return None