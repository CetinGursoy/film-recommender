from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base

class Watched(Base):
    __tablename__ = "watched_movies"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="watched")
    movie = relationship("Movie")

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie_watched"),
    )
