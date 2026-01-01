from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db import Base

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    score = Column(Integer)

    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))

    user = relationship("User", back_populates="ratings")
    movie = relationship("Movie", back_populates="ratings")
