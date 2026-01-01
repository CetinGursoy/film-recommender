# app/models/contact.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db import Base

class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    message = Column(String, nullable=False)
    reply = Column(String, nullable=True) # Admin's reply
    replied_at = Column(DateTime(timezone=True), nullable=True) # Time of reply
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class CaptchaSession(Base):
    __tablename__ = "captcha_sessions"

    uuid = Column(String, primary_key=True, index=True) # UUID sent to frontend
    answer = Column(Integer, nullable=False) # The correct answer to the math problem
    expires_at = Column(DateTime(timezone=True), nullable=False) # Expiration time
