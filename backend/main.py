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
@app.post("/users", response_class=RedirectResponse)
def create_user(username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = UserData(username=username, email=email, password=password)
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    crud.create_user(db, user)
    return RedirectResponse(url="/")

@app.post("/users/login")
def login(request: Request, username: str = Form(...), password:str = Form(...), db: Session = Depends(get_db)):
    db_user = crud.validate_user(db, username, password)
    if db_user is None:
        return "Username or Password Incorrect"
    return templates.TemplateResponse("platform.html", {"request": request, "user":db_user})

@app.get("/toggleSignup")
def toggleSignup(request: Request):
    return templates.TemplateResponse("signup-form.html", {"request": request})
@app.get("/toggleLogin")
def toggleSignup(request: Request):
    return templates.TemplateResponse("login-form.html", {"request": request})