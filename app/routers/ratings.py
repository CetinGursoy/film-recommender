# app/routers/ratings.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db import get_db
from app.core.security import get_current_user
from app.models.rating import Rating
from app.models.users import User
from app.schemas.ratings import RatingCreate

router = APIRouter(prefix="/ratings", tags=["Ratings"])


@router.post("/add", status_code=status.HTTP_201_CREATED)
def add_rating(
    data: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Belirli bir filme, giriş yapmış kullanıcı için puan ekler.
    Varsa günceller (Upsert mantığı daha mantıklı olabilir ama şimdilik yeni ekleme/hata).
    """
    
    
    existing = db.query(Rating).filter(Rating.user_id == current_user.id, Rating.movie_id == data.movie_id).first()
    
    if existing:
        
        existing.score = data.score
        db.commit()
        return {"message": "Puan güncellendi", "id": existing.id, "score": existing.score}

    new_rating = Rating(
        score=data.score,
        movie_id=data.movie_id,
        user_id=current_user.id,
    )
    db.add(new_rating)

    try:
        db.commit()
        db.refresh(new_rating)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sunucu hatası: {e}",
        )

    return {"message": "Rating added", "id": new_rating.id, "score": new_rating.score}


@router.get("/{movie_id}/my-rating")
def get_my_rating(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rating = db.query(Rating).filter(Rating.user_id == current_user.id, Rating.movie_id == movie_id).first()
    if not rating:
        return {"has_rated": False, "score": 0}
    
    return {"has_rated": True, "score": rating.score}
