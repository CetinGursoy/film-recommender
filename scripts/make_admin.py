import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Ensure app is in python path
sys.path.append(os.getcwd())

from app.db import SessionLocal
from app.models.users import User
from app.models.collection import Collection
from app.models.watched import Watched # 🔥 Fix for Watched relation

def make_admin():
    db = SessionLocal()
    print("--- User List ---")
    users = db.query(User).all()
    if not users:
        print("No users found in database!")
        print("Please register a user first via the Frontend.")
        return

    for u in users:
        print(f"ID: {u.id} | Username: {u.username} | Admin: {u.is_admin}")

    username = input("\nEnter username to make ADMIN (or 'q' to quit): ")
    if username.lower() == 'q':
        return

    user = db.query(User).filter(User.username == username).first()
    if user:
        user.is_admin = 1
        db.commit()
        print(f"User '{username}' is now an ADMIN (is_admin=1).")
    else:
        print("User not found!")

    db.close()

if __name__ == "__main__":
    make_admin()
