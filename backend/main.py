from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import crud
from database import engine, localSession
from schemas import UserData, UserId
from models import Base

Base.metadata.create_all(bind=engine) # Create the tables in the database if not exist

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = localSession()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
def root_get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
@app.post("/", response_class=HTMLResponse)
def root_post(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/users", response_model=list[UserId])
def get_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

@app.get("/users/{user_id:int}", response_model=UserId)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users", response_class=RedirectResponse)
def create_user(username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = UserData(username=username, email=email, password=password)
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    crud.create_user(db, user)
    return RedirectResponse(url="/")
   


@app.post("/users/validate", response_model=bool)
def login(username: str, password:str, db: Session = Depends(get_db)):
    db_user = crud.validate_user(db, username, password)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Username or Password Incorrect")
    return True

        
