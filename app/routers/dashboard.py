from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import get_db
from app.core.security import get_current_user
from app.models.users import User
from app.models.like import Like
from app.models.rating import Rating
from app.models.movie import Movie
from app.models.watched import Watched
from app.recommender.content import recommend_by_content
import json

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)

@router.get("/user")
def get_user_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. User Stats
    total_likes = db.query(Like).filter(Like.user_id == current_user.id).count()
    total_watched = db.query(Watched).filter(Watched.user_id == current_user.id).count()
    
    # 2. Recent Likes (Last 5)
    recent_likes = (
        db.query(Like, Movie)
        .join(Movie, Like.movie_id == Movie.id)
        .filter(Like.user_id == current_user.id)
        .order_by(Like.created_at.desc())
        .limit(5)
        .all()
    )
    
    recent_movies_data = []
    for like, movie in recent_likes:
        recent_movies_data.append({
            "id": movie.id,
            "title": movie.title,
            "poster_path": movie.poster_path,
            "poster_url": movie.poster_url
        })
        
    # 3. Favorite Genres
    # Get all liked movies genres
    liked_movies = (
        db.query(Movie)
        .join(Like, Movie.id == Like.movie_id)
        .filter(Like.user_id == current_user.id)
        .all()
    )
    
    genre_counts = {}
    for m in liked_movies:
        if m.genres:
            try:
                # Genres stored as JSON string: [{"id": 1, "name": "Action"}, ...]
                genres_list = json.loads(m.genres)
                for g in genres_list:
                    g_name = g['name']
                    genre_counts[g_name] = genre_counts.get(g_name, 0) + 1
            except:
                pass
                
    # Sort by count desc and take top 3
    top_genres = sorted(genre_counts.items(), key=lambda item: item[1], reverse=True)[:3]
    top_genres_list = [{"name": name, "count": count} for name, count in top_genres]
    
    # 4. Recommendations with Seeds
    # Use the most recent liked movie as seed
    recommendations = []
    seed_info = None
    
    if recent_likes:
        last_liked_movie = recent_likes[0][1] # (Like, Movie) tuple
        seed_info = {
            "title": last_liked_movie.title,
            "id": last_liked_movie.id
        }
        
        all_movies = db.query(Movie).all()
        # Get content based recs
        recs = recommend_by_content(all_movies, seed_movie=last_liked_movie, top_n=10)
        
        # Filter out already seen/liked/watched
        # For simplicity, just filter out the seed itself from results (recommend_by_content might include it or similar)
        recommendations = [r for r in recs if r['id'] != last_liked_movie.id]
    else:
        # Fallback: Popular movies
        popular = db.query(Movie).order_by(Movie.popularity.desc()).limit(10).all()
        recommendations = [
             {
                "id": m.id,
                "title": m.title,
                "poster_path": m.poster_path,
                "poster_url": m.poster_url,
                "vote_average": m.vote_average
            } for m in popular
        ]
        seed_info = None # Indicates "Popular" fallback

    return {
        "user_profile": {
            "username": current_user.username,
            "joined_at": current_user.created_at,
            "total_likes": total_likes,
            "total_watched": total_watched
        },
        "recent_likes": recent_movies_data,
        "favorite_genres": top_genres_list,
        "recommendations": recommendations,
        "recommendation_seed": seed_info
    }
