from pydantic import BaseModel

class UserData(BaseModel):
    username: str
    email: str
    password: str

class UserId(UserData):
    id: int