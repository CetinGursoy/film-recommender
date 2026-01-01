
import os
import sys
import sqlite3
import requests
import re
import urllib.parse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

DB_PATH = "app/movies.db"

def fetch_trailer_from_tmdb(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/videos"
    params = {"api_key": TMDB_API_KEY} 
    try:
        res = requests.get(url, params=params, timeout=5).json()
        results = res.get("results", [])
        
        # 1. Turkish Trailer
        tr = next((v for v in results if v["iso_639_1"] == "tr" and v["type"] == "Trailer" and v["site"] == "YouTube"), None)
        if tr: return f"https://www.youtube.com/watch?v={tr['key']}"
            
        # 2. English Trailer
        en = next((v for v in results if v["iso_639_1"] == "en" and v["type"] == "Trailer" and v["site"] == "YouTube"), None)
        if en: return f"https://www.youtube.com/watch?v={en['key']}"
            
        # 3. Any Trailer
        any_t = next((v for v in results if v["type"] == "Trailer" and v["site"] == "YouTube"), None)
        if any_t: return f"https://www.youtube.com/watch?v={any_t['key']}"

        return None
    except:
        return None

def fetch_trailer_from_youtube_scrape(title):
    try:
        query_string = urllib.parse.quote(f"{title} fragman trailer")
        url = "https://www.youtube.com/results?search_query=" + query_string
        
        # Fake header to avoid bot detection
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=5)
        html = response.text
        
        # Regex to find video IDs
        # "videoId":"VIDEO_ID" pattern common in YouTube JSON response in HTML
        video_ids = re.findall(r'"videoId":"(.*?)"', html)
        
        if video_ids:
            # First one is usually the top result
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
            
    except Exception as e:
        print(f"YT Scrape error for {title}: {e}")
    return None

def update_movies():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Only get files WITHOUT trailer
    c.execute("SELECT id, tmdb_id, title FROM movies WHERE trailer_url IS NULL OR trailer_url = ''")
    movies = c.fetchall()
    
    print(f"Checking fallbacks for {len(movies)} missing trailers...")
    
    count = 0
    updated = 0
    
    for m in movies:
        mid, tmdb_id, title = m
        
        # 1. Try TMDB again (maybe missed?)
        trailer = fetch_trailer_from_tmdb(tmdb_id)
        
        # 2. Fallback to YouTube Scrape
        if not trailer:
             print(f"🔍 Searching YouTube for: {title}")
             trailer = fetch_trailer_from_youtube_scrape(title)
        
        if trailer:
            c.execute("UPDATE movies SET trailer_url = ? WHERE id = ?", (trailer, mid))
            updated += 1
            print(f"✅ Found: {title[:20]} -> {trailer}")
        else:
            print(f"❌ Still no trailer for {title[:20]}")
            
        count += 1
        if count % 10 == 0:
            conn.commit()
            
    conn.commit()
    conn.close()
    print(f"🎉 Done! Filled {updated} gaps.")

if __name__ == "__main__":
    update_movies()
