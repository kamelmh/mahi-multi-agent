import pytest
import json
import datetime as dt
from unittest.mock import patch, MagicMock
import bcrypt
import jwt

from app import app, db, User, Category, Transaction, Budget, create_access_token, create_refresh_token, decode_token

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

@pytest.fixture
def auth_headers(client):
    def _make_headers(email='test@example.com', password='testpass123'):
        # Register user
        client.post('/api/auth/register', 
                   json={'email': email, 'password': password},
                   content_type='application/json')
        
        # Login to get tokens
        resp = client.post('/api/auth/login',
                          json={'email': email, 'password': password},
                          content_type='application/json')
        data = json.loads(resp.data)
        access_token = data['access_token']
        return {'Authorization': f'Bearer {access_token}'}
    return _make_headers

@pytest.fixture
def test_user(client):
    user = User(email='test@example.com')
    user.set_password('testpass123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_category(client, auth_headers):
    headers = auth_headers()
    resp = client.post('/api/categories',
                      json={'name': 'Food', 'type': 'expense'},
                      headers=headers,
                      content_type='application/json')
    data = json.loads(resp.data)
    return Category.query.get(data['id'])

@pytest.fixture
def test_transaction(client, auth_headers, test_category):
    headers = auth_headers()
    resp = client.post('/api/transactions',
                      json={
                          'amount': 25.50,
                          'date': '2023-01-15',
                          'category_id': test_category.id,
                          'description': 'Groceries'
                      },
                      headers=headers,
                      content_type='application/json')
    data = json.loads(resp.data)
    return Transaction.query.get(data['id'])

def test_register_success(client):
    resp = client.post('/api/auth/register',
                      json={'email': 'new@example.com', 'password': 'securepass123'},
                      content_type='application/json')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert 'access_token' in data
    assert 'refresh_token' in data
    assert data['user']['email'] == 'new@example.com'
    assert User.query.filter_by(email='new@example.com').first() is not None

def test_register_duplicate_email(client, test_user):
    resp = client.post('/api/auth/register',
                      json={'email': 'test@example.com', 'password': 'anotherpass'},
                      content_type='application/json')
    assert resp.status_code == 400
    data = json.loads(resp.data)
    assert 'Email already registered' in data

def test_login_success(client, test_user):
    resp = client.post('/api/auth/login',
                      json={'email': 'test@example.com', 'password': 'testpass123'},
                      content_type='application/json')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert 'access_token' in data
    assert 'refresh_token' in data

def test_login_invalid_credentials(client, test_user):
    resp = client.post('/api/auth/login',
                      json={'email': 'test@example.com', 'password': 'wrongpass'},
                      content_type='application/json')
    assert resp.status_code == 401

def test_refresh_token(client, test_user):
    # Get initial tokens
    resp = client.post('/api/auth/login',
                      json={'email': 'test@example.com', 'password': 'testpass123'},
                      content_type='application/json')
    data = json.loads(resp.data)
    refresh_token = data['refresh_token']
    
    # Use refresh token
    resp = client.post('/api/auth/refresh',
                      headers={'Authorization': f'Bearer {refresh_token}'},
                      content_type='application/json')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert 'access_token' in data
    # New access token should be different
    assert data['access_token'] != json.loads(
        client.post('/api/auth/login',
                   json={'email': 'test@example.com', 'password': 'testpass123'},
                   content_type='application/json').data)['access_token']

def test_refresh_with_access_token_fails(client, test_user):
    resp = client.post('/api/auth/login',
                      json={'email': 'test@example.com', 'password': 'testpass123'},
                      content_type='application/json')
    data = json.loads(resp.data)
    access_token = data['access_token']
    
    resp = client.post('/api/auth/refresh',
                      headers={'Authorization': f'Bearer {access_token}'},
                      content_type='application/json')
    assert resp.status_code == 401

def test_logout(client, auth_headers):
    headers = auth_headers()
    resp = client.post('/api/auth/logout', headers=headers)
    assert resp.status_code == 200

def test_get_me(client, auth_headers, test_user):
    headers = auth_headers()
    resp = client.get('/api/users/me', headers=headers)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data['id'] == test_user.id
    assert data['email'] == test_user.email

def test_get_me_unauthorized(client):
    resp = client.get('/api/users/me')
    assert resp.status_code == 401

def test_list_categories_empty(client, auth_headers):
    headers = auth_headers()
    resp = client.get('/api/categories', headers=headers)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data == []

def test_create_category(client, auth_headers):
    headers = auth_headers()
    resp = client.post('/api/categories',
                      json={'name': 'Entertainment', 'type': 'expense'},
                      headers=headers,
                      content_type='application/json')
    assert resp.status_code == 201
    data = json.loads(resp.data)
    assert 'id' in data
    category = Category.query.get(data['id'])
    assert category.name == 'Entertainment'
    assert category.type == 'expense'

def test_create_category_duplicate_name(client, auth_headers, test_category):
    headers = auth_headers()
    resp = client.post('/api/categories',
                      json={'name': test_category.name, 'type': 'expense'},
                      headers=headers,
                      content_type='application/json')
    assert resp.status_code == 400

def test_create_category_invalid_type(client, auth_headers):
    headers = auth_headers()
    resp = client.post('/api/categories',
                      json={'name': 'Invalid', 'type': 'invalid'},
                      headers=headers,
                      content_type='application/json')
    assert resp.status_code == 400

def test_update_category(client, auth_headers, test_category):
    headers = auth_headers()
    resp = client.put(f'/api/categories/{test_category.id}',
                      json={'name': 'Updated Food', 'type': 'income'},
                      headers=headers,
                      content_type='application/json')
    assert resp.status_code == 200
    updated = Category.query.get(test_category.id)
    assert updated.name == 'Updated Food'
    assert updated.type == 'income'

def test_update_category_duplicate_name(client, auth_headers):
    headers = auth_headers()
    # Create first category
    resp1 = client.post('/api/categories',
                       json={'name': 'Category1', 'type': 'expense'},
                       headers=headers,
                       content_type='application/json')
    cat1_id = json.loads(resp1.data)['id']
    # Create second category
    resp2 = client.post('/api/categories',
                       json={'name': 'Category2', 'type': 'expense'},
                       headers=headers,
                       content_type='application/json')
    cat2_id = json.loads(resp2.data)['id']
    # Try to update cat2 to cat1's name
    resp = client.put(f'/api/categories/{cat2_id}',
                     json={'name': 'Category1'},
                     headers=headers,
                     content_type='application/json')
    assert resp.status_code == 400

def test_update_category_not_found(client, auth_headers):
    headers = auth_headers()
    resp = client.put('/api/categories/999',
                     json={'name': 'Nonexistent'},
                     headers=headers,
                     content_type='application/json')
    assert resp.status_code == 404

def test_delete_category(client, auth_headers, test_category):
    headers = auth_headers()
    resp = client.delete(f'/api/categories/{test_category.id}', headers=headers)
    assert resp.status_code == 204
    assert Category.query.get(test_category.id) is None

def test_delete_category_not_found(client, auth_headers):
    headers = auth_headers()
    resp = client.delete('/api/categories/999', headers=headers)
    assert resp.status_code == 404

def test_list_transactions(client, auth_headers, test_transaction):
    headers = auth_headers()
    resp = client.get('/api/transactions', headers=headers)
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert len(data) == 1
    assert data[0]['id'] == test_transaction.id
    assert float(data[0]['amount']) == 25.50
    assert data[0]['date'] == '2023-01-15'
    assert data[0]['description'] == 'Groceries'
    assert data[0]['category']['id'] == test_transaction.category_id

def test_list_transactions_with_filters(client, auth_headers, test_transaction, test_category):
    headers = auth_headers()
    # Create income category and transaction
    income_cat = Category(user_id=1, name='Salary', type='income')
    db.session.add(income_cat)
    db.session.commit()
    income_txn = Transaction(
        user_id=1,
        category_id=income_cat.id,
        amount=1000.00,
        date=dt.date(2023, 1, 1),
        description='Monthly salary'
    )
    db.session.add(income_txn)
    db.session.commit()
    
    # Filter by type
    resp = client.get('/api/transactions?type=expense', headers=headers)
    data = json.loads(resp.data)
    assert len(data) == 1
    assert data[0]['category']['type'] == 'expense'
    
    resp = client.get('/api/transactions?type=income', headers=headers)
    data = json.loads(resp.data)
    assert len(data) == 1
    assert data[0]['category']['type'] == 'income'
    
    # Filter by category_id
    resp = client.get(f'/api/transactions?category_id={test_category.id}', headers=headers)
    data = json.loads(resp.data)
    assert len(data) == 1
    assert data[0]['category']['id'] == test_category.id
    
    # Filter by date range
    resp = client.get('/api/transactions?start=2023-01-01&end=2023-01-31', headers=headers)
    data = json.loads(resp.data)
    assert len(data) == 2  # Both transactions
    
    resp = client.get('/api/transactions?start=2023-02-01&end=2023-02-28', headers=headers)
    data = json.loads(resp.data)
    assert len(data) == 0

def test_create_transaction(client, auth_headers, test_category):
    headers = auth_headers()
    resp = client.post('/api/transactions',
                      json={
                          'amount': 15.99,
                          'date': '2023-02-10',
                          'category_id': test_category.id,
                          'description': 'Movie ticket'
                      },
                      headers=headers,
                      content_type='application/json')
    assert resp.status_code == 201
    data = json.loads(resp.data)
    assert 'id' in data
    txn = Transaction.query.get(data['id'])
    assert txn.amount == 15.99
    assert txn.date == dt.date(2023, 2, 10)
    assert txn.description == 'Movie ticket'

def test_create_transaction_invalid_date(client, auth_headers, test_category):
    headers = auth_headers()
    resp = client.post('/api/transactions',
                      json={
                          'amount': 10.00,
                          'date': '2023/10/05',  # Invalid format
                          'category_id': test_category.id
                      },
                      headers=headers,
                      content_type='application/json')
    assert resp.status_code == 400

def test_create_transaction_nonexistent_category(client, auth_headers):
    headers = auth_headers()
    resp = client.post('/api/transactions',
                      json={
                          'amount': 10.00,
                          'date': '2023-01-01',
                          'category_id': 999
                      },
                      headers=headers,
                      content_type='application/json')
    assert resp.status_code == 404

def test_update_transaction(client, auth_headers, test_transaction):
    headers = auth_headers()
    resp = client.put(f'/api/transactions/{test_transaction.id}',
                      json={
                          'amount': 30.00,
                          'date': '2023-01-20',
                          'description': 'Updated groceries'
                      },
                      headers=headers,
                      content_type='application/json')
    assert resp