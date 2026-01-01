# app/services/tmdb.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# V3 API Key kullanılıyor (Poster arama V3 endpoint'idir)
TMDB_API_KEY = os.getenv("TMDB_API_KEY") 

# TMDB_TOKEN (V4) poster aramada kullanılmaz, bu yüzden sadece V3 Key'i kontrol ediyoruz.

def get_poster_url(title: str):
    """Film başlığına göre poster URL bulur. (V3 API Key kullanır)"""
    if not TMDB_API_KEY:
        print("❌ TMDB_API_KEY bulunamadı!")
        return None

    url = "https://api.themoviedb.org/3/search/movie"
    
    params = {
        "query": title, 
        "language": "en-US",
        "api_key": TMDB_API_KEY # V3 Key, URL parametresi olarak gönderilir
    }

    try:
        r = requests.get(url, params=params)
        r.raise_for_status()

        data = r.json().get("results", [])
        if not data:
            return None

        poster_path = data[0].get("poster_path")
        
        # 🛠️ DÜZELTME: Poster URL'si oluşturulurken HTTPS kullanıldığından emin olunur.
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}" 
        
    except Exception as e:
        print(f"❌ Poster API hatası: {e}")

    return None