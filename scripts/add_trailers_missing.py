
import os
import sqlite3
import requests
import re
import urllib.parse
import time

TMDB_API_KEY = "685991a80391238c318290e42a163178"

def fetch_trailer_from_tmdb(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/videos"
    params = {"api_key": TMDB_API_KEY} 
    try:
        res = requests.get(url, params=params, timeout=5)
        if res.status_code != 200: return None
        
        results = res.json().get("results", [])
        
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
        # Search specifically for Turkish trailer if possible
        query_string = urllib.parse.quote(f"{title} fragman trailer türkçe")
        url = "https://www.youtube.com/results?search_query=" + query_string
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=5)
        html = response.text
        
        video_ids = re.findall(r'"videoId":"(.*?)"', html)
        
        if video_ids:
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
            
    except Exception as e:
        print(f"YT hata: {e}")
    return None

def update_movies():
    db_path = os.path.join(os.path.dirname(__file__), "../app/movies.db")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get only movies with missing trailers
    c.execute("SELECT id, tmdb_id, title FROM movies WHERE trailer_url IS NULL OR trailer_url = ''")
    movies = c.fetchall()
    
    print(f"🎬 {len(movies)} film için fragman aranıyor...")
    
    count = 0
    updated_count = 0
    
    for m in movies:
        mid, tmdb_id, title = m
        
        # 1. Try TMDB
        trailer = fetch_trailer_from_tmdb(tmdb_id)
        
        # 2. Fallback to YouTube Scrape
        if not trailer:
             print(f"🔍 YouTube'da aranıyor: {title}")
             trailer = fetch_trailer_from_youtube_scrape(title)
             time.sleep(1) # Be nice to YT
        
        if trailer:
            c.execute("UPDATE movies SET trailer_url = ? WHERE id = ?", (trailer, mid))
            updated_count += 1
            print(f"✅ Bulundu: {title} -> {trailer}")
        else:
            print(f"❌ Bulunamadı: {title}")
            
        count += 1
        if count % 5 == 0:
            conn.commit()
            
    conn.commit()
    conn.close()
    print(f"🏁 İşlem tamamlandı! {updated_count} yeni fragman eklendi.")

if __name__ == "__main__":
    update_movies()
