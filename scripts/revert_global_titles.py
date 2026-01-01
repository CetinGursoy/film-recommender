
import sqlite3
import os
import requests
import time
from dotenv import load_dotenv

# Load env from .env file
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
DB_PATH = "app/movies.db"

def revert_titles():
    print(f"🌍 Starting Global Title Revert Script...")
    
    if not TMDB_API_KEY:
        print("❌ Error: TMDB_API_KEY not found.")
        return

    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Get all movies that are NOT Turkish
        # We assume empty or None might be candidates too, but let's stick to != 'tr' if populated
        # Ideally, we should check if original_language is not 'tr'. 
        # If original_language is NULL, we might skip or fetch to check. 
        # For now, relying on != 'tr'.
        cursor.execute("SELECT id, tmdb_id, title FROM movies WHERE original_language != 'tr' OR original_language IS NULL")
        movies = cursor.fetchall()
        total = len(movies)
        print(f"📊 Found {total} non-Turkish movies to check/revert.")

        updated_count = 0
        
        for i, (db_id, tmdb_id, current_title) in enumerate(movies, 1):
            if not tmdb_id:
                continue

            try:
                # Fetch EN details (US default)
                url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
                params = {"api_key": TMDB_API_KEY, "language": "en-US"}
                
                response = requests.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    en_title = data.get("title")
                    
                    if en_title and en_title != current_title:
                        cursor.execute("UPDATE movies SET title = ? WHERE id = ?", (en_title, db_id))
                        updated_count += 1
                        print(f"✅ [{i}/{total}] Reverted: '{current_title}' -> '{en_title}'")
                    else:
                        if i % 100 == 0:
                            print(f"🔹 [{i}/{total}] Skipped (Match): {current_title}")
                else:
                    print(f"❌ [{i}/{total}] API Error {response.status_code}")

                # Commit periodically
                if updated_count > 0 and updated_count % 50 == 0:
                    conn.commit()
                
                time.sleep(0.02) # Respect API limits

            except Exception as e:
                print(f"💥 Error on movie {db_id}: {e}")

        conn.commit()
        print(f"\n🎉 Finished! Reverted {updated_count} titles to English.")

    except Exception as e:
        print(f"❌ Script Fatal Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    revert_titles()
