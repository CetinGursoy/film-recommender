
import sqlite3
import os
import requests
import time
from dotenv import load_dotenv

# Load env from .env file
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
DB_PATH = "app/movies.db"

def update_titles():
    print(f"🚀 Starting Title Localization Script...")
    
    if not TMDB_API_KEY:
        print("❌ Error: TMDB_API_KEY not found.")
        return

    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Get all movies
        cursor.execute("SELECT id, tmdb_id, title FROM movies")
        movies = cursor.fetchall()
        total = len(movies)
        print(f"📊 Found {total} movies to check.")

        updated_count = 0
        
        for i, (db_id, tmdb_id, current_title) in enumerate(movies, 1):
            if not tmdb_id:
                continue

            try:
                # Fetch TR details
                url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
                params = {"api_key": TMDB_API_KEY, "language": "tr-TR"}
                
                response = requests.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    tr_title = data.get("title")
                    
                    if tr_title and tr_title != current_title:
                        cursor.execute("UPDATE movies SET title = ? WHERE id = ?", (tr_title, db_id))
                        updated_count += 1
                        print(f"✅ [{i}/{total}] Updated: '{current_title}' -> '{tr_title}'")
                    else:
                        # Optional: Print progress even if skipped
                        if i % 50 == 0:
                            print(f"🔹 [{i}/{total}] Skipped (Already match): {current_title}")
                else:
                    print(f"❌ [{i}/{total}] API Error {response.status_code} for ID {tmdb_id}")

                # Commit every 50 updates
                if updated_count > 0 and updated_count % 50 == 0:
                    conn.commit()
                
                # Tiny sleep to be nice to API
                time.sleep(0.02)

            except Exception as e:
                print(f"💥 Error on movie {db_id}: {e}")

        conn.commit()
        print(f"\n🎉 Finished! Updated {updated_count} titles to Turkish.")

    except Exception as e:
        print(f"❌ Script Fatal Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_titles()
