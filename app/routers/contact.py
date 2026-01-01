# app/routers/contact.py
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db import get_db
from app.models.contact import ContactMessage
from app.routers.auth import get_current_user
from app.models.users import User
import requests
import os
from datetime import datetime

router = APIRouter(prefix="/contact", tags=["Contact"])


RECAPTCHA_SECRET_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"

# -- ADMIN ENDPOINTS --

@router.get("/messages")
def get_all_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Yetkisiz erişim")
    
    messages = db.query(ContactMessage).order_by(desc(ContactMessage.created_at)).all()
    return messages

@router.put("/{message_id}/reply")
def reply_message(
    message_id: int,
    reply: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Yetkisiz erişim")
    
    msg = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Mesaj bulunamadı")
        
    msg.reply = reply
    msg.replied_at = datetime.now()
    
    db.commit()
    db.refresh(msg)
    return msg

# -- USER ENDPOINTS --

@router.get("/my-messages")
def get_my_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    messages = db.query(ContactMessage).filter(
        ContactMessage.email == current_user.email
    ).order_by(desc(ContactMessage.created_at)).all()
    
    return messages

# -- PUBLIC ENDPOINTS --

@router.post("/send")
def send_contact_message(
    name: str = Body(...),
    email: str = Body(...),
    message: str = Body(...),
    captcha_token: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    Verifies google reCAPTCHA and saves the contact message.
    """
  
    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        "secret": RECAPTCHA_SECRET_KEY,
        "response": captcha_token
    }
    
    try:
        response = requests.post(verify_url, data=data)
        result = response.json()
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Captcha doğrulama servisine ulaşılamadı: {str(e)}")

    if not result.get("success"):
        
        raise HTTPException(status_code=400, detail="Captcha doğrulaması başarısız. Lütfen tekrar deneyin.")


    new_message = ContactMessage(
        name=name,
        email=email,
        message=message
    )
    db.add(new_message)
    db.commit()
    
    return {"message": "Mesajınız başarıyla iletildi! 🚀"}
