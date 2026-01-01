from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.orm import relationship
from app.db import Base
from app.models.like import Like
from app.models.lists import ListItem

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, index=True, nullable=False)

    title = Column(String, nullable=False)
    overview = Column(Text)
    overview_tr = Column(Text)  

   
    poster_path = Column(String)
    poster_url = Column(String)
    trailer_url = Column(String) 

    release_date = Column(String)
    original_language = Column(String) # new field

    genres = Column(Text)      
    cast = Column(Text)       
    directors = Column(Text)  

    popularity = Column(Float)
    vote_average = Column(Float)
    vote_count = Column(Integer)

    # Relations (bunlara dokunma)
    ratings = relationship("Rating", back_populates="movie")
    reviews = relationship("Review", back_populates="movie")
    likes = relationship("Like", back_populates="movie", cascade="all, delete-orphan")
    listed_by = relationship("ListItem", back_populates="movie", cascade="all, delete-orphan")
