from sqlalchemy import Column, Integer, String, LargeBinary
from database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    username = Column(String(30), unique=True, index=True,nullable=False)
    email = Column(String(30), unique=True, nullable=False)
    salt = Column(LargeBinary, nullable=False)
    password = Column(String(64), nullable=False)

class Publication(Base):
    __tablename__ = 'publications'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(String(500), nullable=False)
    author = Column(Integer, nullable=False)
    date = Column(String(10), nullable=False)

class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    content = Column(String(500), nullable=False)
    author = Column(Integer, nullable=False)
    publication = Column(Integer, nullable=False)
    date = Column(String(10), nullable=False)

    