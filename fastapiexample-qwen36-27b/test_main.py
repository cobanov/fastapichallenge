import base64
import pytest
from fastapi.testclient import TestClient
from main import app
from auth import VALID_CREDENTIALS

client = TestClient(app)


def b64(user, pwd):
    return "Basic " + base64.b64encode(f"{user}:{pwd}".encode()).decode()


def valid_auth():
    return {"Authorization": b64("admin", VALID_CREDENTIALS["admin"])}


# --- Auth Tests ---

def test_auth_valid_credentials():
    r = client.get("/items/", headers={"Authorization": b64("admin", VALID_CREDENTIALS["admin"])})
    assert r.status_code == 200


def test_auth_invalid_password():
    r = client.get("/items/", headers={"Authorization": b64("admin", "wrongpass")})
    assert r.status_code == 401


def test_auth_invalid_username():
    r = client.get("/items/", headers={"Authorization": b64("nobody", "nopass")})
    assert r.status_code == 401


def test_auth_missing_credentials():
    r = client.get("/items/")
    assert r.status_code == 401


# --- Root Endpoint ---

def test_root_returns_html():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


# --- Get Items ---

def test_list_items():
    r = client.get("/items/", headers=valid_auth())
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_single_item():
    r = client.get("/items/1", headers=valid_auth())
    assert r.status_code == 200
    assert r.json()["id"] == 1


def test_item_has_required_fields():
    r = client.get("/items/1", headers=valid_auth())
    data = r.json()
    assert "id" in data
    assert "name" in data
    assert "price" in data
    assert "stock" in data


def test_get_item_404():
    r = client.get("/items/9999", headers=valid_auth())
    assert r.status_code == 404


# --- Create Item ---

def test_create_item():
    r = client.post("/items/", json={"name": "USB Cable", "price": 9.99}, headers=valid_auth())
    assert r.status_code == 201
    assert r.json()["name"] == "USB Cable"


def test_create_item_defaults_stock():
    r = client.post("/items/", json={"name": "Webcam", "price": 49.99}, headers=valid_auth())
    assert r.status_code == 201
    assert r.json()["stock"] == 0


def test_create_item_custom_stock():
    r = client.post("/items/", json={"name": "Speaker", "price": 89.99, "stock": 30}, headers=valid_auth())
    assert r.status_code == 201
    assert r.json()["stock"] == 30


# --- Update Item ---

def test_update_item_name():
    r = client.put("/items/1", json={"name": "Gaming Laptop"}, headers=valid_auth())
    assert r.status_code == 200
    assert r.json()["name"] == "Gaming Laptop"


def test_update_item_price():
    r = client.put("/items/2", json={"price": 39.99}, headers=valid_auth())
    assert r.status_code == 200
    assert r.json()["price"] == 39.99


def test_update_item_stock():
    r = client.put("/items/3", json={"stock": 100}, headers=valid_auth())
    assert r.status_code == 200
    assert r.json()["stock"] == 100


def test_update_item_404():
    r = client.put("/items/9999", json={"name": "Ghost"}, headers=valid_auth())
    assert r.status_code == 404


# --- Delete Item ---

def test_delete_item():
    initial = len(client.get("/items/", headers=valid_auth()).json())
    r = client.delete("/items/5", headers=valid_auth())
    assert r.status_code == 200
    after = len(client.get("/items/", headers=valid_auth()).json())
    assert after == initial - 1


def test_delete_item_count_reduces():
    before = len(client.get("/items/", headers=valid_auth()).json())
    client.delete("/items/4", headers=valid_auth())
    after = len(client.get("/items/", headers=valid_auth()).json())
    assert after == before - 1


def test_delete_item_404():
    r = client.delete("/items/9999", headers=valid_auth())
    assert r.status_code == 404


# --- Search ---

def test_search_existing():
    r = client.get("/items/search?name=Laptop", headers=valid_auth())
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_search_case_insensitive():
    r = client.get("/items/search?name=mouse", headers=valid_auth())
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_search_no_results():
    r = client.get("/items/search?name=zzzznonexistent", headers=valid_auth())
    assert r.status_code == 200
    assert r.json() == []
