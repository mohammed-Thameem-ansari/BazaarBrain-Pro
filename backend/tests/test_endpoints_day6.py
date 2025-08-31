import json
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_auth_login():
    r = client.post('/auth/login', json={"email": "test@example.com", "password": "x"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("success") is True
    assert isinstance(data.get("token"), str)


def _get_token() -> str:
    r = client.post('/auth/login', json={"email": "test@example.com", "password": "x"})
    return r.json()["token"]


def test_collective_order_post_get():
    token = _get_token()
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post('/api/v1/collective_order', json={"product_id": "rice", "quantity": 25}, headers=headers)
    assert r.status_code == 200
    data = r.json()
    assert data["product_id"] == "rice"
    assert data["total_quantity"] >= 25

    r2 = client.get('/api/v1/collective_order', headers=headers)
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2.get("success") is True
    assert isinstance(d2.get("orders"), list)


def test_simulate_post():
    token = _get_token()
    headers = {"Authorization": f"Bearer {token}"}
    r = client.post('/api/v1/simulate', json={"query": "What if I increase rice price by 5%?"}, headers=headers)
    assert r.status_code in (200, 422)
    if r.status_code == 200:
        data = r.json()
        assert data.get("success") is True
        assert data.get("result") is not None
