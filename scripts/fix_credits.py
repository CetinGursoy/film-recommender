
import os
import sys
import sqlite3
import json
import requests
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()
API_V4_TOKEN = os.getenv("TMDB_V4_TOKEN")

DB_PATH = "app/movies.db"
BASE_URL = "https://api.themoviedb.org/3"

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_V4_TOKEN}"
}

def get_json(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {}

def fetch_credits(tmdb_id):
    url = f"{BASE_URL}/movie/{tmdb_id}/credits"
    data = get_json(url)
    
    cast = data.get("cast", [])
    crew = data.get("crew", [])
    
    # Process cast (top 10)
    final_cast = []
    for c in cast[:10]:
        final_cast.append({
            "name": c.get("name"),
            "character": c.get("character"),
            "profile_path": c.get("profile_path")
        })
        
    # Process directors
    final_directors = []
    for c in crew:
        if c.get("job") == "Director":
             final_directors.append({
                "name": c.get("name"),
                "profile_path": c.get("profile_path")
            })
            
    return final_cast, final_directors

def fix_movies():
    conn = sqlite3.connect(DB_PATH)
    # Use Row factory or just tuples
    c = conn.cursor()
    
    # Find movies with empty cast/directors
    # checking for NULL, empty string, or empty JSON array '[]'
    c.execute("""
        SELECT id, tmdb_id, title, "cast", directors 
        FROM movies 
        WHERE "cast" IS NULL OR "cast" = '' OR "cast" = '[]' 
           OR directors IS NULL OR directors = '' OR directors = '[]'
    """)
    movies = c.fetchall()
    
    print(f"Found {len(movies)} movies with missing credits.")
    
    updated_count = 0
    for m in movies:
        mid, tmdb_id, title, cast_val, dir_val = m
        
        print(f"Fetching credits for: {title} (TMDB {tmdb_id})...")
        new_cast, new_directors = fetch_credits(tmdb_id)
        
        # Serialize to JSON
        cast_json = json.dumps(new_cast, ensure_ascii=False)
        dir_json = json.dumps(new_directors, ensure_ascii=False)
        
        if not new_cast and not new_directors:
            print(f"❌ No credits found on TMDB for {title} either.")
        else:
            c.execute("UPDATE movies SET cast = ?, directors = ? WHERE id = ?", (cast_json, dir_json, mid))
            updated_count += 1
            print(f"✅ Updated {title}: {len(new_cast)} cast, {len(new_directors)} directors.")
            
        time.sleep(0.1) # Rate limit friendly
        
        if updated_count % 10 == 0:
            conn.commit()
            
    conn.commit()
    conn.close()
    print(f"\n🎉 Done! Fixed {updated_count} movies.")

if __name__ == "__main__":
    fix_movies()
