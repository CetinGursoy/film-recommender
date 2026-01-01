
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models.movie import Movie
# Import other models to ensure SQLAlchemy registry is populated and relationships work
from app.models.users import User
from app.models.collection import Collection
from app.models.watched import Watched
from app.models.like import Like
from app.models.lists import ListItem
from app.models.review import Review
from app.models.rating import Rating
from app.services.nlp_service import generate_embeddings_for_db

def update_embeddings():
    print("🧠 Chatbot veritabanı güncelleniyor...")
    db = SessionLocal()
    try:
        movies = db.query(Movie).all()
        print(f"📂 Toplam {len(movies)} film bulundu.")
        
        # Force re-generation
        # We delete the old pickle file to ensure fresh generation or rely on the logic if key count mismatch
        # But looking at nlp_service.py, it checks cache first. 
        # To be safe, let's delete the pickle file first to force update.
        if os.path.exists("movie_embeddings.pkl"):
            os.remove("movie_embeddings.pkl")
            print("🗑️ Eski önbellek temizlendi.")
            
        generate_embeddings_for_db(movies)
        print("✅ Yeni filmler chatbot'a öğretildi!")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_embeddings()
