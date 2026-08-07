from test.conftest import *
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
    response = client.get('/item/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_filter_items_by_category(test_items_multiple):
    response = client.get('/item/?category=Tools')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Hammer'


def test_filter_items_by_price_range(test_items_multiple):
    response = client.get('/item/?min_price=20&max_price=100')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Chair'


def test_filter_items_in_stock_only(test_items_multiple):
    response = client.get('/item/?in_stock_only=true')
    assert response.status_code == status.HTTP_200_OK
    names = [item['name'] for item in response.json()]
    assert 'Chair' not in names
    assert 'Hammer' in names
    assert 'Laptop' in names


def test_filter_items_by_search(test_items_multiple):
    response = client.get('/item/?search=lap')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Laptop'


def test_filter_items_combined(test_items_multiple):
    response = client.get('/item/?category=Electronics&min_price=500')
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Laptop'


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


def test_viewer_cannot_create_item(as_role):
    as_role('viewer')
    item_model = {
        'name' : 'Cup',
        'category' : 'Tools',
        'price' : 1.0,
        'quantity': 30,
    }
    response = client.post('/item/', json=item_model)
    assert response.status_code == status.HTTP_403_FORBIDDEN


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


def test_viewer_cannot_update_item(as_role, test_item):
    as_role('viewer')
    item_model = {
        'name' : 'Cup',
        'category' : 'Tools',
        'price' : 1.5,
        'quantity': 30,
    }
    response = client.put('/item/1', json=item_model)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_todo(test_item):
    response = client.delete('/item/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    model = db.query(Items).filter(Items.id == 1).first()
    assert model is None


def test_delete_todo_not_found():
    response = client.delete('/item/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_viewer_cannot_delete_item(as_role, test_item):
    as_role('viewer')
    response = client.delete('/item/1')
    assert response.status_code == status.HTTP_403_FORBIDDEN
