
import requests
import os
from datetime import date

TMDB_API_KEY = "685991a80391238c318290e42a163178"

def check_upcoming():
    url = "https://api.themoviedb.org/3/movie/upcoming"
    params = {"api_key": TMDB_API_KEY, "language": "tr-TR", "region": "TR", "page": 1}
    
    print(f"Bügün: {date.today()}")
    
    res = requests.get(url, params=params).json()
    results = res.get("results", [])
    
    filtered = [m for m in results if m.get('release_date') > date.today().isoformat()]
    
    print(f"Toplam Gelen: {len(results)}")
    print(f"Gelecek Tarihli (Frontend'de Gözükmeli): {len(filtered)}")
    
    for m in filtered:
        print(f"📅 {m['release_date']} - {m['title']}")

if __name__ == "__main__":
    check_upcoming()
