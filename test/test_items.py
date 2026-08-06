from conftest import *
from fastapi import status


def test_read_all_items_authenticated(test_item):
    response = client.get('/item/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'id' : 1,
        'name' : 'Cup',
        'category' : 'Tools',
        'price' : 1.0,
        'quantity': 30,
        'description' : None
    }]


def test_get_item_authenticated(test_item):
    response = client.get('/item/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id' : 1,
        'name' : 'Cup',
        'category' : 'Tools',
        'price' : 1.0,
        'quantity': 30,
        'description' : None
    }


def test_read_one_not_found():
    response = client.get('/items/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_item_authentiacted():
    item_model = {
        'name' : 'Cup',
        'category' : 'Tools',
        'price' : 1.0,
        'quantity': 30,
    }
    response = client.post('/item/', json=item_model)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
            'id' : 1,
            'name' : 'Cup',
            'category' : 'Tools',
            'price' : 1.0,
            'quantity': 30,
            'description' : None
        }


def test_update_item_authenticated(test_item):
    item_model = {
            'name' : 'Cup',
            'category' : 'Tools',
            'price' : 1.5,
            'quantity': 30,
        }
    response = client.put('/item/1', json=item_model)
    assert response.status_code == status.HTTP_202_ACCEPTED
    assert response.json() == {
            'id' : 1,
            'name' : 'Cup',
            'category' : 'Tools',
            'price' : 1.5,
            'quantity': 30,
            'description' : None
        }


def test_delete_todo(test_item):
    response = client.delete('item/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Items).filter(Items.id == 1).first()
    assert model is None


def test_delete_todo_not_found():
    response = client.delete('/todos/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND