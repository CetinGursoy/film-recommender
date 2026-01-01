import sqlite3
import os

DB_PATH = "app/movies.db"

def update_db():
    if not os.path.exists(DB_PATH):
        print(f"Hata: {DB_PATH} bulunamadı.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print("🔄 is_spoiler sütunu ekleniyor...")
    try:
        c.execute("ALTER TABLE reviews ADD COLUMN is_spoiler BOOLEAN DEFAULT 0")
        print("✔ is_spoiler eklendi.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
             print("ℹ️ is_spoiler zaten var, atlanıyor.")
        else:
            print(f"❌ Hata: {e}")

    conn.commit()
    conn.close()
    print("✅ Migrasyon tamamlandı.")

if __name__ == "__main__":
    update_db()
