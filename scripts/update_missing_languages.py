
import sqlite3
import os
import requests
import time
from dotenv import load_dotenv

# Load env from .env file
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# Adjust path if needed. Assuming running from project root.
DB_PATH = "app/movies.db"

def update_missing_languages():
    print(f"🚀 Starting update script...")
    print(f"📂 Database Path: {DB_PATH}")

    if not TMDB_API_KEY:
        print("❌ Error: TMDB_API_KEY not found in environment variables.")
        return

    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Database file not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check current stats
        cursor.execute("SELECT COUNT(*) FROM movies WHERE original_language IS NULL OR original_language = 'None' OR original_language = ''")
        remaining = cursor.fetchone()[0]
        print(f"📊 Movies needing update: {remaining}")

        if remaining == 0:
            print("✅ All movies already have language data.")
            return

        # Fetch movies to update
        cursor.execute("SELECT id, title, tmdb_id FROM movies WHERE original_language IS NULL OR original_language = 'None' OR original_language = ''")
        movies = cursor.fetchall()
        
        count = 0
        success_count = 0
        
        for db_id, title, tmdb_id in movies:
            count += 1
            if not tmdb_id:
                print(f"⚠️ [{count}/{remaining}] Skipping {title} (No TMDB ID)")
                continue

            try:
                # Fetch details from TMDB
                url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    language = data.get("original_language")
                    
                    if language:
                        # Update DB
                        cursor.execute("UPDATE movies SET original_language = ? WHERE id = ?", (language, db_id))
                        success_count += 1
                        print(f"✅ [{count}/{remaining}] Updated: {title} ({language})")
                    else:
                        print(f"❓ [{count}/{remaining}] No language found for: {title}")
                else:
                    print(f"❌ [{count}/{remaining}] API Error {response.status_code} for: {title}")
                
                # Commit every 20 updates
                if success_count % 20 == 0:
                    conn.commit()
                    
                # Small delay
                time.sleep(0.05)
                
            except Exception as e:
                print(f"💥 Error processing {title}: {e}")

        conn.commit()
        print(f"\n🎉 Finished! Successfully updated {success_count} movies.")
        
    except Exception as e:
        print(f"❌ Script Fatal Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_missing_languages()
