
import requests
import sqlite3
import os

# Get key from .env manually or hardcode strictly for this fix script to avoid dependency
TMDB_API_KEY = "685991a80391238c318290e42a163178"

def fix_languages():
    db_path = os.path.join(os.path.dirname(__file__), "../app/movies.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Find movies with missing language
    cursor.execute("SELECT id, tmdb_id, title FROM movies WHERE original_language IS NULL OR original_language = ''")
    movies = cursor.fetchall()
    
    print(f"🔍 {len(movies)} filmde dil bilgisi eksik. Düzeltiliyor...")

    count = 0
    for db_id, tmdb_id, title in movies:
        try:
            url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
            res = requests.get(url)
            if res.status_code == 200:
                data = res.json()
                lang = data.get("original_language", "en") # default to en if missing
                
                cursor.execute("UPDATE movies SET original_language = ? WHERE id = ?", (lang, db_id))
                count += 1
                print(f"✅ {title} -> {lang}")
            else:
                print(f"❌ {title} (TMDB Hata): {res.status_code}")
                # Fallback: If title is obviously Turkish (contains Turkish chars or known list), set TR?
                # For now just skip.
        except Exception as e:
            print(f"❌ {title} Hata: {e}")

    conn.commit()
    conn.close()
    print(f"🏁 Tamamlandı! {count} film güncellendi.")

if __name__ == "__main__":
    fix_languages()
