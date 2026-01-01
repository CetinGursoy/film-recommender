
import sys
import os
import json
from sqlalchemy import or_

# Add root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import SessionLocal
from app.models.movie import Movie
from app.models.users import User
from app.models.collection import Collection
from app.models.watched import Watched
from app.models.lists import ListItem
from app.models.review import Review
from app.models.rating import Rating

def check_escaped_search():
    db = SessionLocal()
    query_text = "Cem Yılmaz"
    
    # 1. Standard search (Failed before)
    print(f"\n--- Searching for '{query_text}' (Standard) ---")
    movies = db.query(Movie).filter(Movie.cast.ilike(f"%{query_text}%")).all()
    print(f"Standard match count: {len(movies)}")

    # 2. Escaped search
    # json.dumps ensures headers like characters are escaped as \uXXXX
    # e.g., "ı" -> "\u0131"
    # we slice [1:-1] to remove surrounding quotes
    escaped_val = json.dumps(query_text).strip('"')
    # Use explicit string replacement to be safe about backslashes if needed, 
    # but exact json string should match the DB content.
    
    print(f"\n--- Searching for '{escaped_val}' (Escaped) ---")
    # For SQL LIKE, backslash might need to be escaped again? 
    # In SQLAlchemy ilike, let's try raw string.
    
    movies_esc = db.query(Movie).filter(Movie.cast.ilike(f"%{escaped_val}%")).all()
    print(f"Escaped match count: {len(movies_esc)}")
    for m in movies_esc:
        print(f"  - {m.title}")

    db.close()

if __name__ == "__main__":
    check_escaped_search()
