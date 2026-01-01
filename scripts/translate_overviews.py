
import os
import sys
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db import SessionLocal

from app.models.users import User
from app.models.movie import Movie
from app.models.collection import Collection
from app.models.review import Review
from app.models.like import Like
from app.models.lists import ListItem
from app.models.watched import Watched
from app.models.rating import Rating

from app.utils.tmdb import get_movie_details 
import requests
from deep_translator import GoogleTranslator


from dotenv import load_dotenv
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

def fetch_tmdb_tr(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY, "language": "tr-TR"}
    try:
        res = requests.get(url, params=params).json()
        return res.get("overview", "")
    except:
        return ""

def fetch_tmdb_tr_title(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY, "language": "tr-TR"}
    try:
        res = requests.get(url, params=params).json()
        return res.get("title", "")
    except:
        return ""

def translate_movies():
    db: Session = SessionLocal()
    movies = db.query(Movie).all()
    
    translator = GoogleTranslator(source='auto', target='tr')
    
    count = 0
    updated = 0
    
    print(f"Checking {len(movies)} movies...")
    
    for m in movies:
        
        current_tr = m.overview_tr
        
       
        tmdb_overview = fetch_tmdb_tr(m.tmdb_id)
        
        final_tr = ""
        
        if tmdb_overview and len(tmdb_overview) > 10:
            final_tr = tmdb_overview
        
        
        # tmdb_title = fetch_tmdb_tr_title(m.tmdb_id)
        # if tmdb_title and tmdb_title != m.title:
        #      print(f"  Title Change: {m.title} -> {tmdb_title}")
        #      m.title = tmdb_title
        #      updated += 1
             
        
        if not final_tr:
           
            english_ov = m.overview
            if english_ov and len(english_ov) > 5:
                try:
                    translated = translator.translate(english_ov)
                    final_tr = translated
                except Exception as e:
                    print(f"Translation failed for {m.title}: {e}")
                    
        
        if final_tr:
            m.overview_tr = final_tr
            
            m.overview = final_tr 
            updated += 1
            print(f"✅ Translated Overview: {m.title[:20]}...")
            
        count += 1
        if count % 10 == 0:
            db.commit()
            print(f"--- Processed {count} movies ---")
            
        if count % 10 == 0:
            db.commit()
            print(f"--- Processed {count} movies ---")
        
        time.sleep(0.5)

    db.commit()
    print(f"🎉 Done! Updated {updated} movies.")

if __name__ == "__main__":
    translate_movies()
