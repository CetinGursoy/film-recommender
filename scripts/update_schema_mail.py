
import sqlite3

DB_PATH = "app/movies.db"

def add_columns():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0")
        print("✅ Added is_verified column.")
    except Exception as e:
        print(f"⚠️ is_verified: {e}")

    try:
        c.execute("ALTER TABLE users ADD COLUMN verification_token TEXT")
        print("✅ Added verification_token column.")
    except Exception as e:
        print(f"⚠️ verification_token: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    add_columns()
