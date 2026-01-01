
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.movie import Movie
from app.models.like import Like
import json

def get_user_favorites_genres(db: Session, user_id: int):
    
    likes = db.query(Like).filter(Like.user_id == user_id).all()
    if not likes:
        return []
    
    movie_ids = [l.movie_id for l in likes]
    movies = db.query(Movie).filter(Movie.id.in_(movie_ids)).all()
    
    genre_counts = {}
    for m in movies:
        try:
            genres = json.loads(m.genres) if m.genres else []
            for g in genres:
                name = g['name'] if isinstance(g, dict) else str(g)
                genre_counts[name] = genre_counts.get(name, 0) + 1
        except:
            continue
            
    
    sorted_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)
    return [g[0] for g in sorted_genres[:3]]

from app.recommender.content import recommend_by_content
from sqlalchemy import desc

def recommend_personal(db: Session, user_id: int, limit=5):
    """
    Kullanıcının SON beğendiği filme göre içerik tabanlı (TF-IDF) öneri yapar.
    """
    
    # 1. Kullanıcının son beğendiği filmi bul
    last_like = db.query(Like).filter(Like.user_id == user_id).order_by(desc(Like.created_at)).first()
    
    if not last_like:
        # Hiç beğenisi yoksa -> En popülerleri döndür
        return db.query(Movie).order_by(Movie.popularity.desc()).limit(limit).all()
    
    # Seed movie (Referans film)
    seed_movie = db.query(Movie).filter(Movie.id == last_like.movie_id).first()
    if not seed_movie:
        return db.query(Movie).order_by(Movie.popularity.desc()).limit(limit).all()

    # 2. Tüm filmleri çek (Content-Based hesaplama için)
    # Not: Büyük veride bu adım cache'lenmeli veya pre-calculated similarity matrix kullanılmalı.
    all_movies = db.query(Movie).all()
    
    # 3. Öneri Motorunu Çalıştır
    # recommend_by_content dict listesi döner, biz DB objelerine çevireceğiz
    recs_dicts = recommend_by_content(all_movies, seed_movie=seed_movie, top_n=limit * 3)
    
    # 4. Kullanıcının zaten beğendiği/izlediği filmleri filtrele
    liked_movie_ids = {l.movie_id for l in db.query(Like).filter(Like.user_id == user_id).all()}
    
    final_movies = []
    for r in recs_dicts:
        if r['id'] not in liked_movie_ids and r['id'] != seed_movie.id:
            # DB objesini bul (all_movies listesinden)
            m_obj = next((m for m in all_movies if m.id == r['id']), None)
            if m_obj:
                final_movies.append(m_obj)
                
        if len(final_movies) >= limit:
            break
            
    return final_movies
