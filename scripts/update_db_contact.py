import sqlite3
import os

DB_PATH = "app/movies.db"

def run_migration():
    if not os.path.exists(DB_PATH):
        print(f"❌ Veritabanı bulunamadı: {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("🔄 'reply' sütunu ekleniyor...")
        cursor.execute("ALTER TABLE contact_messages ADD COLUMN reply TEXT")
        print("✔ 'reply' eklendi.")
    except sqlite3.OperationalError as e:
        print(f"⚠ 'reply' sütunu zaten var olabilir: {e}")

    try:
        print("🔄 'replied_at' sütunu ekleniyor...")
        cursor.execute("ALTER TABLE contact_messages ADD COLUMN replied_at TIMESTAMP")
        print("✔ 'replied_at' eklendi.")
    except sqlite3.OperationalError as e:
        print(f"⚠ 'replied_at' sütunu zaten var olabilir: {e}")

    conn.commit()
    conn.close()
    print("✅ Migrasyon tamamlandı.")

if __name__ == "__main__":
    run_migration()
