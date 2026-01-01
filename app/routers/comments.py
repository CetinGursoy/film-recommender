from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.user import User
from app.utils.nlp import is_toxic
from app.core.security import get_current_user, require_admin
from app.db import SessionLocal
from app.db import get_db




router = APIRouter(prefix="/comments", tags=["Comments"])

@router.post("/")
def add_comment(movie_id: int, text: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    if is_toxic(text):
        raise HTTPException(status_code=400, detail="Toxic or inappropriate language detected.")

    comment = Comment(text=text, movie_id=movie_id, user_id=user.id)
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {"message": "Comment added", "comment": comment}


@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(404)

    require_admin(user)  # only admin can delete
    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted"}
