from test.conftest import *
from fastapi import status


def test_read_user_info_authenticated(test_user):
    response = client.get('/users/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id' : 1,
        'username' : 'Abzil',
        'email' : 'Abzil@gmail.com',
        'first_name' : 'Abzil',
        'last_name' : 'Rad',
        'role' : 'admin',
        'is_active' : True
    }


def test_change_password_authenticated(test_user):
    response = client.put('/users/password', json={'password':'Abzil123', 'new_password': 'Admin123'})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == test_user.id).first()
    assert bcrypt_context.verify('Admin123', model.hash_password)