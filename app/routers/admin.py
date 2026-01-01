from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional

from app.db import get_db
from app.routers.auth import get_current_user
from app.models.users import User
from app.models.movie import Movie
from app.models.review import Review
from app.models.like import Like
from app.models.rating import Rating

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.is_admin != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Admin yetkisi gereklidir."
        )
    return current_user


class MovieCreate(BaseModel):
    title: str
    overview: Optional[str] = None
    release_date: Optional[str] = None
    poster_url: Optional[str] = None
    genres: Optional[str] = None

class UserRoleUpdate(BaseModel):
    is_admin: int  # 1: Admin, 0: User, 2: Moderator

# --- DASHBOARD STATS ---
@router.get("/dashboard")
def get_stats(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return {
        "total_users": db.query(User).count(),
        "total_movies": db.query(Movie).count(),
        "total_reviews": db.query(Review).count()
    }

@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    from datetime import datetime, timedelta
    
    # Calculate last 7 days
    today = datetime.utcnow().date()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    
    weekly_data = []
    
    for d in dates:
        # User count for this day
        # Note: SQLite stores datetime as string usually, so we compare date part
        # Or simple range filter: start of day to end of day
        start_of_day = datetime(d.year, d.month, d.day)
        end_of_day = start_of_day + timedelta(days=1)
        
        user_count = db.query(User).filter(User.created_at >= start_of_day, User.created_at < end_of_day).count()
        review_count = db.query(Review).filter(Review.created_at >= start_of_day, Review.created_at < end_of_day).count()
        
        weekly_data.append({
            "day": d.strftime("%a"), 
            "new_users": user_count,
            "new_reviews": review_count
        })


    geography = [
            {"country": "Türkiye", "count": db.query(User).count()}, 
            {"country": "Diğer", "count": 0}
    ]

    # TOP MOVIES
    top_movies = (
        db.query(Movie)
        .order_by(Movie.vote_average.desc(), Movie.vote_count.desc())
        .limit(10)
        .all()
    )

    # TOP COMMENTED MOVIES
    top_commented = (
        db.query(Movie, func.count(Review.id).label('total_reviews'))
        .join(Review, Review.movie_id == Movie.id)
        .group_by(Movie.id)
        .order_by(func.count(Review.id).desc())
        .limit(10)
        .all()
    )

    # TOP LIKED MOVIES (New)
    top_liked = (
        db.query(Movie, func.count(Like.id).label('total_likes'))
        .join(Like, Like.movie_id == Movie.id)
        .group_by(Movie.id)
        .order_by(func.count(Like.id).desc())
        .limit(10)
        .all()
    )

    # TOP RATED MOVIES (New)
    top_rated = (
        db.query(Movie, func.avg(Rating.score).label('avg_score'), func.count(Rating.id).label('count'))
        .join(Rating, Rating.movie_id == Movie.id)
        .group_by(Movie.id)
        .order_by(func.avg(Rating.score).desc())
        .limit(10)
        .all()
    )
    
    # GENRE DISTRIBUTION
    # Naive implementation: Iterate all movies (OK for ~1500, careful for 1M+)
    import json
    all_movies = db.query(Movie).all()
    genre_counts = {}
    
    genre_map = {
        "Action": "Aksiyon",
        "Adventure": "Macera",
        "Animation": "Animasyon",
        "Comedy": "Komedi",
        "Crime": "Suç",
        "Documentary": "Belgesel",
        "Drama": "Dram",
        "Family": "Aile",
        "Fantasy": "Fantastik",
        "History": "Tarih",
        "Horror": "Korku",
        "Music": "Müzik",
        "Mystery": "Gizem",
        "Romance": "Romantik",
        "Science Fiction": "Bilim Kurgu",
        "TV Movie": "TV Filmi",
        "Thriller": "Gerilim",
        "War": "Savaş",
        "Western": "Western"
    }

    for m in all_movies:
        if m.genres:
            try:
                g_list = json.loads(m.genres)
                for g in g_list:
                    g_name = g['name']
                    # Translate if available, else keep original
                    g_name_tr = genre_map.get(g_name, g_name)
                    genre_counts[g_name_tr] = genre_counts.get(g_name_tr, 0) + 1
            except:
                pass
                
    genre_data = [{"name": k, "value": v} for k, v in genre_counts.items()]
    # Sort by value desc
    genre_data.sort(key=lambda x: x['value'], reverse=True)

    return {
        "weekly_activity": weekly_data, 
        "geography": geography,
        "top_movies": [{"id": m.id, "title": m.title, "rating": m.vote_average, "count": m.vote_count} for m in top_movies],
        "top_commented_movies": [{"id": m.id, "title": m.title, "review_count": count} for m, count in top_commented],
        "top_liked_movies": [{"id": m.id, "title": m.title, "like_count": count} for m, count in top_liked],
        "top_rated_movies": [{"id": m.id, "title": m.title, "avg_score": round(avg, 1), "count": count} for m, avg, count in top_rated],
        "genre_distribution": genre_data[:10] # Top 10 genres
    }


@router.post("/movies")
def add_movie(movie: MovieCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    
    import random
    fake_tmdb_id = random.randint(1000000, 9999999)
    
    new_movie = Movie(
        tmdb_id=fake_tmdb_id,
        title=movie.title,
        overview=movie.overview,
        release_date=movie.release_date,
        poster_url=movie.poster_url,
        genres=movie.genres, 
        popularity=0,
        vote_average=0,
        vote_count=0
    )
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return {"message": "Movie added", "movie_id": new_movie.id}

@router.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(404, "Movie not found")
    
    db.delete(movie)
    db.commit()
    return {"message": "Movie deleted"}


@router.get("/users")
def list_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return db.query(User).all()

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    
    if user.id == admin.id:
        raise HTTPException(400, "Kendinizi silemezsiniz.")

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

@router.put("/users/{user_id}/role")
def update_user_role(user_id: int, role_data: UserRoleUpdate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    user.is_admin = role_data.is_admin
    db.commit()
    return {"message": "User role updated", "is_admin": user.is_admin}
