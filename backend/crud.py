from sqlalchemy.orm import Session
from models import User
from schemas import UserData
import hashlib
import os


def get_users(db: Session):
    return db.query(User).all()

def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: UserData):
    salt = os.urandom(16)
    hashed_password = hashlib.sha256((user.password).encode('utf-8')+salt).hexdigest()
    new_user = User(username=user.username, email=user.email, salt=salt, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.flush(new_user)
    return new_user

def validate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if user:
        check_pass = hashlib.sha256((password).encode('utf-8')+user.salt).hexdigest()
        if check_pass == user.password:
            return user
    return None