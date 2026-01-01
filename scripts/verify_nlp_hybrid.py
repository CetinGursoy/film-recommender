
from app.db import SessionLocal
from app.services.nlp_service import generate_embeddings_for_db, semantic_search
from app.models.movie import Movie
from app.models.collection import Collection
from app.models.review import Review
from app.models.rating import Rating
from app.models.lists import ListItem
from app.models.like import Like
from app.models.watched import Watched
import time

def test_nlp_hybrid():
    print("⏳ Veritabanına bağlanıp embeddings hazırlanıyor...")
    db = SessionLocal()
    movies = db.query(Movie).all() # Limit for speed if needed, but we want full test
    
    # 1. Generate Embeddings (Normally happens on startup)
    start = time.time()
    generate_embeddings_for_db(movies)
    print(f"⏱️ Embedding süresi: {time.time() - start:.2f}s")
    
    # 2. Test Semantic Queries
    queries = [
        "beni ağlatan film", 
        "hapishaneden kaçış", 
        "uzayda geçen macera",
        "türk komedisi", # This should ideally be caught by keyword, but let's see nlp fallback
        "Isaac Asimov" # Specific concept
    ]
    
    for q in queries:
        print(f"\n🧠 Sorgu: '{q}'")
        results = semantic_search(q)
        if results:
            for r in results:
                print(f"  - [{r['score']:.2f}] {r['title']}")
        else:
            print("  ❌ Sonuç bulunamadı.")

if __name__ == "__main__":
    test_nlp_hybrid()
