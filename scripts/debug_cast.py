
import sys
import os

# Add root to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import SessionLocal
from app.models.movie import Movie
from app.models.users import User
from app.models.collection import Collection
from app.models.watched import Watched
from app.models.lists import ListItem
from app.models.review import Review
from app.models.rating import Rating

def check_cast():
    db = SessionLocal()
    print("\n--- Checking 'cast' column format ---")
    
    # 1. Fetch a movie known to have Cem Yılmaz (or just search for it)
    search_term = "%Yahşi Batı%"
    movies = db.query(Movie).filter(Movie.title.ilike(search_term)).all()
    
    if movies:
        print(f"Found {len(movies)} movies matching '{search_term}':")
        for m in movies:
            print(f"ID: {m.id}, Title: {m.title}")
            print(f"Cast Raw: {m.cast[:500]}") # Print more chars to see Cem Yılmaz
    else:
        print(f"No movies found matching '{search_term}'.")
        
        # 2. Check ANY movie's cast format
        m = db.query(Movie).filter(Movie.cast != None).first()
        if m:
            print(f"\nRandom Movie Cast ({m.title}):")
            print(f"Cast Raw: {m.cast[:200]}")
            
    db.close()

if __name__ == "__main__":
    check_cast()
