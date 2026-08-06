from test.conftest import *
from app.routers.auth import authenticate_user, create_access_token
from datetime import timedelta
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