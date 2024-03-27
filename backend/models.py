from sqlalchemy import Column, Integer, String, LargeBinary
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    username = Column(String(30), unique=True, index=True,nullable=False)
    email = Column(String(30), unique=True, nullable=False)
    salt = Column(LargeBinary, nullable=False)
    password = Column(String(64), nullable=False)