from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.core.security import get_current_user
from app.db import Base


class ListItem(Base):
    __tablename__ = "list_items"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="lists")
    movie = relationship("Movie")

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie_list"),
    )
