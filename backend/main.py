from fastapi import FastAPI, Depends, HTTPException, Request, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import crud
from database import engine, localSession
from schemas import UserData, UserId
from models import Base
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from typing import Annotated

load_dotenv()
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
TOKEN_EXP_SECS = os.getenv('TOKEN_EXP_SECS')

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

def create_token(data:dict = {}):
    token_data = data.copy()
    token_data["exp"] = datetime.utcnow() + timedelta(seconds=int(TOKEN_EXP_SECS))
    token_jwt = jwt.encode(token_data, JWT_SECRET_KEY, algorithm="HS256")
    return token_jwt

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
def login(username: str = Form(...), password:str = Form(...), db: Session = Depends(get_db)):
    db_user = crud.validate_user(db, username, password)
    if db_user is None:
        return "Username or Password Incorrect"
    token = create_token({"user": db_user.username})
    return RedirectResponse(url="/users/platform",
                            status_code=302, 
                            headers={"set-cookie": f'access_token={token}; Max-Age={TOKEN_EXP_SECS}; Path=/'})

@app.get("/users/logout")
def logout():
    return RedirectResponse(url="/", status_code=302, headers={"set-cookie": "access_token=; Max-Age=0; Path=/"})

@app.get("/users/platform")
def platform(request: Request, access_token: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    if access_token is None:
        return RedirectResponse(url="/")
    try:
        user_data = jwt.decode(access_token, JWT_SECRET_KEY, algorithms=["HS256"])
        if crud.get_user_by_username(db, user_data["user"]) is None:
            return RedirectResponse(url="/")
        return templates.TemplateResponse("platform.html", {"request": request, 
                                                            "user":user_data["user"], 
                                                            "publications":[{"title":"Title 1", 
                                                                             "content":"Content 1", 
                                                                             "author":"admin", 
                                                                             "date":"2021-10-01", 
                                                                             "comments":[{"content":"Comment 1", "author":"admin", "date":"2021-10-01"},
                                                                                         {"content":"Comment 2", "author":"Author 2", "date":"2021-10-02"}]
                                                                            },
                                                                            {"title":"Title 2", 
                                                                             "content":"Content 2", 
                                                                             "author":"Author 2", 
                                                                             "date":"2021-10-02", 
                                                                             "comments":[]},
                                                                            {"title":"Title 3", 
                                                                             "content":"Content 3", 
                                                                             "author":"Author 3", 
                                                                             "date":"2021-10-03",
                                                                             "comments":[]}
                                                            ]
                                                            })
    except JWTError:
        return RedirectResponse(url="/")

@app.get("/toggleSignup")
def toggleSignup(request: Request):
    return templates.TemplateResponse("signup-form.html", {"request": request})
@app.get("/toggleLogin")
def toggleSignup(request: Request, access_token: Annotated[str | None, Cookie()] = None, db: Session = Depends(get_db)):
    if access_token is None:
        return templates.TemplateResponse("login-form.html", {"request": request})
    try:
        user_data = jwt.decode(access_token, JWT_SECRET_KEY, algorithms=["HS256"])
        if crud.get_user_by_username(db, user_data["user"]) is None:
            return RedirectResponse(url="/")
        return RedirectResponse(url="/users/platform")
    except JWTError:
        return templates.TemplateResponse("login-form.html", {"request": request})
    