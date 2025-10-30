import pytest 
from app import app, Note, get_db, encrypt_context, decrypt_content
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch 

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health(client):
    rv = client.get('/health')
    assert rv.status_code == 200
    assert 'status' in rv.json

def test_add_get_note(client):
    rv = client.post('/notes', json={"content" :"Test note"})
    assert rv.status_code == 201
    rb = client.get('/notes')
    assert len(rv.json) == 1
    assert rv.json[0]['content'] == 'Test note'

@patch('app.ENCRYPT_KEY', 'testkey')
def test_encrypt_decrypt():
    encrypted = encrypt_context('secret')
    decrypted = decrypt_content(encrypted)
    assert decrypted == "secret"
