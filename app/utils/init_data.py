# app/utils/init_data.py

import json
import os
from app.db import SessionLocal
from app.models.movie import Movie

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "movies_1500.json"))


def import_local_movies():
    print("📥 Yerel 1500 film içe aktarılıyor...")

    if not os.path.exists(JSON_PATH):
        print("❌ movies_1500.json bulunamadı:", JSON_PATH)
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        movies = json.load(f)

    db = SessionLocal()
    added = 0
    skipped = 0

    for m in movies:
        tmdb_id = m.get("tmdb_id")   # ✔ DOĞRU FIELD

        if not tmdb_id:
            print("❌ ID bulunamadı, film atlandı:", m.get("title"))
            skipped += 1
            continue

        # Duplicate kontrolü
        if db.query(Movie).filter(Movie.tmdb_id == tmdb_id).first():
            skipped += 1
            continue

        movie = Movie(
            tmdb_id=tmdb_id,
            title=m.get("title"),
            overview=m.get("overview"),
            release_date=m.get("release_date"),

            genres=json.dumps(m.get("genres") or []),

            # JSON’daki cast ve directors ZATEN VAR — direkt kaydediyoruz
            cast=json.dumps(m.get("cast") or []),
            directors=json.dumps(m.get("directors") or []),

            poster_path=m.get("poster_path"),
            poster_url="https://image.tmdb.org/t/p/w500" + m["poster_path"]
                if m.get("poster_path") else None,

            vote_average=m.get("vote_average"),
            popularity=m.get("popularity"),
            vote_count=m.get("vote_count"),
        )

        try:
            db.add(movie)
            db.commit()
            added += 1
        except Exception as e:
            print("❌ Hata:", e)
            db.rollback()
            skipped += 1
            continue

    db.close()

    print(f"🔥 EKLENEN: {added}")
    print(f"⏭️ ATLANAN: {skipped}")
    print("✔ Yerel film import tamamlandı!")


def update_movie_posters():
    print("🎨 Poster güncelleme fonksiyonu çalıştı (dummy).")
