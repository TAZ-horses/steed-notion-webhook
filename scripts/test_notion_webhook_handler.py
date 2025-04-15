import os
import hmac
import hashlib
import json
import pytest
from notion_webhook_handler import app  # Make sure this matches your actual file name

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

def generate_signature(secret, payload):
    return hmac.new(
        secret.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()

def test_webhook_success(client):
    payload = json.dumps({'key': 'value'}).encode()
    signature = generate_signature(os.getenv('NOTION_SECRET'), payload)
    response = client.post(
        '/webhook',
        data=payload,
        headers={'X-Notion-Signature': signature, 'Content-Type': 'application/json'}
    )
    assert response.status_code == 200
    assert response.get_json() == {'status': 'success'}

def test_webhook_unauthorized(client):
    payload = json.dumps({'key': 'value'}).encode()
    response = client.post(
        '/webhook',
        data=payload,
        headers={'X-Notion-Signature': 'invalid', 'Content-Type': 'application/json'}
    )
    assert response.status_code == 401

def test_webhook_invalid_payload(client):
    signature = generate_signature(os.getenv('NOTION_SECRET'), b'')
    response = client.post(
        '/webhook',
        data='',
        headers={'X-Notion-Signature': signature, 'Content-Type': 'application/json'}
    )
    assert response.status_code == 400
