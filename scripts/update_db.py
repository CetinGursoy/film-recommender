import sqlite3
import datetime


DB_PATH = "app/movies.db"

def update_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        
        print("Updating users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP")
        
        now = datetime.datetime.utcnow()
        cursor.execute("UPDATE users SET created_at = ?", (now,))
        print("Success: users table updated.")
    except sqlite3.OperationalError as e:
        print(f"Skipped users: {e}")

    try:
        
        print("Updating reviews table...")
        cursor.execute("ALTER TABLE reviews ADD COLUMN created_at TIMESTAMP")
        now = datetime.datetime.utcnow()
        cursor.execute("UPDATE reviews SET created_at = ?", (now,))
        print("Success: reviews table updated.")
    except sqlite3.OperationalError as e:
        print(f"Skipped reviews: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_db()
