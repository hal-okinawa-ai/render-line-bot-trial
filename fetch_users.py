import psycopg2
import os

DATABASE_URL = os.getenv("DATABASE_URL")

def fetch_users():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("SELECT * FROM users;")
    users = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return users

if __name__ == "__main__":
    users = fetch_users()
    for user in users:
        print(user)