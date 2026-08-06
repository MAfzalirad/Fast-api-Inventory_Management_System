import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from database import Base
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from main import app
from models import Items, Users
from fastapi.testclient import TestClient
import pytest
from passlib.context import CryptContext
from dependencies import get_current_user, get_db, get_required_env

load_dotenv('Inventory_Management_System/.env.test')

SECRET_KEY = get_required_env('SECRET_KEY')
ALGORITHM = get_required_env('ALGORITHM')


SQLALCHEMY_DATABASE_URL = 'sqlite:///./testims.db'

engine = create_engine(SQLALCHEMY_DATABASE_URL,connect_args={"check_same_thread": False}, poolclass=StaticPool)


TestingSessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated = 'auto')


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username':'Abzil', 'id':1, 'role':'admin'}


client = TestClient(app)

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


@pytest.fixture
def test_item():
    item = Items(
        name = 'Cup',
        category = 'Tools',
        price = 1,
        quantity = 30
    )
    
    db = TestingSessionLocal()
    db.add(item)
    db.commit()
    yield db
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM items;"))
        connection.commit()


@pytest.fixture
def test_user():
    user = Users(
        username = 'Abzil',
        email = 'Abzil@gmail.com',
        first_name = 'Abzil',
        last_name = 'Rad',
        hash_password = bcrypt_context.hash('Abzil123'),
        is_active = True,
        role = 'admin',
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()