from typing import List

from fastapi import BackgroundTasks, Depends, FastAPI
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1234@db-sync-async-test:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)


class UserBase(BaseModel):
    class Config:
        orm_mode = True

    email: str

# Dependency
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_users(session: Session):
    return session.query(User).all()


def get_one_user(session: Session):
    return session.query(User).first()

Base.metadata.create_all(bind=engine)


def find_user():
    with SessionLocal() as db:
       return get_users(db)


app = FastAPI()


@app.get("/users-con-dependencia", response_model=List[UserBase])
def read_users_con_dependencia(one_user: User = Depends(find_user)):
    with SessionLocal() as session:
        users = get_users(session)
        return users


@app.get("/users", response_model=List[UserBase])
def read_users():
    with SessionLocal() as session:
        users = get_users(session)
        return users



@app.get("/users-va-a-explotar", response_model=List[UserBase])
def read_users_fail(session: Session = Depends(get_session)):
    users = get_users(session)
    return users



@app.get("/users/insert-data-to-test")
def insert_data_to_test():
    with SessionLocal() as session:
        user = User()
        user.email = "teste@teste.com.br"
        session.add(user)
        session.commit()
