from test.conftest import *
from app.routers.auth import authenticate_user, create_access_token
from datetime import timedelta
from fastapi import status
from jose import jwt

def test_authenticate_user(test_user):
    db = TestingSessionLocal()
    authenticated_user = authenticate_user(db, test_user.username, 'Abzil123')
    assert authenticated_user is not None

    non_existing_user = authenticate_user(db, 'WrongUsername', 'Abzil123')
    assert non_existing_user is False

    wrong_password_user = authenticate_user(db, test_user.username, 'Wrong Password')
    assert wrong_password_user is False

def test_create_access_token():
    db = TestingSessionLocal()
    username = 'testuser'
    id = 1
    role = 'user'
    access_token = create_access_token(username, id, role, expires_delta=timedelta(minutes=30))

    decoded_token = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})

    assert decoded_token['username'] == username
    assert decoded_token['role'] == role
    assert decoded_token['id'] == id


def test_register_user():
    user_data = {
        'username': 'newuser',
        'email': 'newuser@gmail.com',
        'first_name': 'New',
        'last_name': 'User',
        'password': 'newpass123',
    }
    response = client.post('/auth/', json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data['username'] == 'newuser'
    assert data['role'] == 'viewer'
    assert 'password' not in data
    assert 'hash_password' not in data

    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()


def test_register_duplicate_user(test_user):
    user_data = {
        'username': 'Abzil',
        'email': 'different@gmail.com',
        'first_name': 'Dup',
        'last_name': 'User',
        'password': 'password123',
    }
    response = client.post('/auth/', json=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_login_success(test_user):
    response = client.post('/auth/token', data={'username': 'Abzil', 'password': 'Abzil123'})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert 'access_token' in data
    assert data['token_type'] == 'bearer'


def test_login_wrong_password(test_user):
    response = client.post('/auth/token', data={'username': 'Abzil', 'password': 'WrongPass'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_nonexistent_user():
    response = client.post('/auth/token', data={'username': 'Ghost', 'password': 'whatever'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED