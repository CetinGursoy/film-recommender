import sqlite3
import os

# Database path
DB_PATH = "app/movies.db"

def list_users():
    if not os.path.exists(DB_PATH):
        print(f"❌ Veritabanı dosyası bulunamadı: {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, email, is_verified, is_admin FROM users")
        users = cursor.fetchall()
        
        print(f"\n{'='*60}")
        print(f"{'ID':<5} {'KULLANICI ADI':<20} {'E-POSTA':<30} {'ONAY':<5} {'ADMIN'}")
        print(f"{'-'*60}")
        
        for user in users:
            user_id, username, email, is_verified, is_admin = user
            verified_status = "✅" if is_verified else "❌"
            admin_status = "👑" if is_admin else "👤"
            print(f"{user_id:<5} {username:<20} {email:<30} {verified_status:<5} {admin_status}")
            
        print(f"{'='*60}\n")
        print(f"Toplam Kullanıcı: {len(users)}\n")
        
        conn.close()
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")

if __name__ == "__main__":
    list_users()
