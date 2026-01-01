# app/models/review.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from datetime import datetime
from sqlalchemy.orm import relationship
from app.db import Base

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_spoiler = Column(Boolean, default=False)


    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))

    user = relationship("User", back_populates="reviews")
    movie = relationship("Movie", back_populates="reviews")
