import os
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db import Base, DATABASE_URL
from app.models.movie import Movie
from app.models.users import User
from app.models.collection import Collection
from app.models.watched import Watched
from app.models.review import Review
from app.models.rating import Rating
from app.models.like import Like
from app.models.contact import ContactMessage
from app.utils.tmdb import get_movie_details
import time

# Create engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def add_column_if_not_exists():
    try:
        # Check if column exists by trying to select it (SQLite specific hack, or use inspection)
        with engine.connect() as conn:
            conn.execute(text("SELECT original_language FROM movies LIMIT 1"))
            print("Column 'original_language' already exists.")
    except Exception:
        print("Adding 'original_language' column to movies table...")
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE movies ADD COLUMN original_language VARCHAR"))
            conn.commit()
        print("Column added.")

def populate_languages():
    print("Fetching movie details and populating languages...")
    movies = db.query(Movie).filter(Movie.original_language == None).all()
    
    total = len(movies)
    print(f"Found {total} movies to update.")
    
    for i, movie in enumerate(movies):
        try:
            details = get_movie_details(movie.tmdb_id)
            if details and "original_language" in details:
                movie.original_language = details["original_language"]
                db.add(movie)
                
                if i % 10 == 0:
                    db.commit()
                    print(f"Updated {i}/{total}: {movie.title} -> {movie.original_language}")
            
            # Rate limit slightly
            time.sleep(0.05)
            
        except Exception as e:
            print(f"Error updating movie {movie.id}: {e}")

    db.commit()
    print("All movies updated!")

if __name__ == "__main__":
    add_column_if_not_exists()
    populate_languages()
