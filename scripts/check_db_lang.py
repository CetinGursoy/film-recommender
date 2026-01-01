
from app.db import SessionLocal
from app.models.movie import Movie
from sqlalchemy import func

def check_languages():
    db = SessionLocal()
    try:
        results = db.query(Movie.original_language, func.count(Movie.id)).group_by(Movie.original_language).all()
        print("Language Distribution:")
        for lang, count in results:
            print(f"'{lang}': {count}")
            
        # Also list titles of 'tr' movies
        tr_movies = db.query(Movie.title, Movie.original_language).filter(Movie.original_language == 'tr').all()
        print("\nMovies with 'tr':")
        for m in tr_movies:
            print(f"- {m.title} ({m.original_language})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_languages()
