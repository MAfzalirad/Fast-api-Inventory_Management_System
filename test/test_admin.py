from ..test.conftest import *
from fastapi import status


def test_get_all_users_authenticated(test_user):
    response = client.get('/admin/users')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'id' : 1,
        'username' : 'Abzil',
        'email' : 'Abzil@gmail.com',
        'first_name' : 'Abzil',
        'last_name' : 'Rad',
        'role' : 'admin',
        'is_active' : True
    }]


def test_get_user_by_id_authenticated(test_user):
    response = client.get('/admin/users/1')
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


def test_change_user_role_authenticated(test_user):
    response = client.put('/admin/users/1/role', json={'new_role': 'manager'})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == test_user.id).first()
    assert model.role == 'manager'


def test_deactivate_user_authenticated(test_user, test_viewer_user):
    response = client.put('/admin/users/2/deactivate')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == test_viewer_user.id).first()
    assert not model.is_active

def test_own_user_deactivate_authenticated(test_user):
    response = client.put('/admin/users/1/deactivate')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_user_authenticated(test_user, test_viewer_user):
    response = client.delete('/admin/users/2')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == 2).first()
    assert model is None


def test_own_user_delete_authenticated(test_user):
    response = client.delete('/admin/users/1')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_user_authenticated():
    user_model = {
        'username': 'admin2',
        'email': 'admin2@gmail.com',
        'first_name': 'admin',
        'last_name': 'second',
        'password': 'admin123',
        'role': 'admin',
    }
    response = client.post('/admin/create-user', json=user_model)
    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()
    assert response_data['username'] == 'admin2'
    assert response_data['email'] == 'admin2@gmail.com'
    assert response_data['first_name'] == 'admin'
    assert response_data['last_name'] == 'second'
    assert response_data['role'] == 'admin'
    assert response_data['is_active'] == True
    assert 'password' not in response_data
    assert 'hash_password' not in response_data

    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.username == 'admin2').first()
    assert model is not None
    assert model.email == 'admin2@gmail.com'
    assert model.first_name == 'admin'
    assert model.last_name == 'second'
    assert model.role == 'admin'
    assert model.is_active == True
    assert bcrypt_context.verify('admin123', model.hash_password)
