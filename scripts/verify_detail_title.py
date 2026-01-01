
from app.db import SessionLocal
from app.routers.movies import get_movie
from app.models.movie import Movie

def test_detail_logic():
    db = SessionLocal()
    try:
        # 1. Get Godfather (TMDB 238)
        movie = db.query(Movie).filter(Movie.tmdb_id == 238).first()
        if not movie:
            print("❌ Godfather not found in DB")
            return

        # Simulate route logic
        # We need to manually replicate the route since we can't easily mock Depends(get_db) here cleanly for quick script
        # But we can verify the logic we just wrote:
        
        from app.utils.tmdb import get_movie_details
        tmdb_extra = get_movie_details(movie.tmdb_id)
        
        print(f"🎬 Fetched from TMDB directly: {tmdb_extra.get('title')} (Should be 'Baba')")
        
        # Apply Logic
        if movie.original_language != "tr":
            tmdb_extra.pop("title", None)
            
        final_title = tmdb_extra.get("title") if tmdb_extra.get("title") else movie.title
        
        print(f"✅ Final Logic Title: {final_title}")
        
        if final_title == "The Godfather":
            print("🎉 SUCCESS: Logic forces English title.")
        else:
            print("❌ FAIL: Still showing Turkish title.")

    except Exception as e:
        print(f"💥 Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_detail_logic()
