import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DATABASE_HOST"),
            database=os.getenv("DATABASE_NAME"),
            user=os.getenv("DATABASE_USER"),
            password=os.getenv("DATABASE_PASSWORD"),
            port=os.getenv("DATABASE_PORT")
        )
        return conn
    except Exception as e:
        print(f"❌ DB接続エラー: {e}")
        return None