from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base

class UserLikedMovie(Base):
    __tablename__ = "user_liked_movies"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))

    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="unique_like"),)

class UserWatchList(Base):
    __tablename__ = "user_watchlist"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))

    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="unique_watchlist"),)
