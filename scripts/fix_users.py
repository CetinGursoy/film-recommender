from app.db import SessionLocal
from app.models.users import User
from app.models.collection import Collection # Fix relationship error

def fix_users():
    db = SessionLocal()
    users = db.query(User).filter(User.is_verified == 0).all()
    print(f"Found {len(users)} unverified users.")
    
    for u in users:
        print(f"Verifying user: {u.username} ({u.email})")
        u.is_verified = 1
    
    db.commit()
    print("All users verified!")
    db.close()

if __name__ == "__main__":
    fix_users()
