from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import crud
from database import engine, localSession
from schemas import UserData, UserId
from models import Base

Base.metadata.create_all(bind=engine) # Create the tables in the database if not exist

app = FastAPI()

def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def root():
    return "Hello, World!"

@app.get("/users/", response_model=list[UserId])
def get_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

@app.get("/users/{user_id:int}", response_model=UserId)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/", response_model=UserId)
def create_user(user: UserData, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)