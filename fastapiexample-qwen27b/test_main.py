import base64

import pytest
from fastapi.testclient import TestClient
from main import app
from routes.items import items

VALID_CREDENTIALS = ("admin", "admin123")
INVALID_CREDENTIALS = ("admin", "wrongpass")

AUTH_HEADER = {
    "Authorization": f"Basic {base64.b64encode(f'{VALID_CREDENTIALS[0]}:{VALID_CREDENTIALS[1]}'.encode()).decode()}"
}

INVALID_AUTH_HEADER = {
    "Authorization": f"Basic {base64.b64encode(f'{INVALID_CREDENTIALS[0]}:{INVALID_CREDENTIALS[1]}'.encode()).decode()}"
}

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_items():
    items.clear()
    items.extend([
        {"id": 1, "name": "Laptop", "price": 999.99, "in_stock": True},
        {"id": 2, "name": "Phone", "price": 699.99, "in_stock": True},
        {"id": 3, "name": "Tablet", "price": 449.99, "in_stock": False},
    ])
    yield


class TestAuth:
    def test_valid_credentials(self):
        response = client.get("/items/", headers=AUTH_HEADER)
        assert response.status_code == 200

    def test_invalid_credentials(self):
        response = client.get("/items/", headers=INVALID_AUTH_HEADER)
        assert response.status_code == 401

    def test_no_credentials(self):
        response = client.get("/items/")
        assert response.status_code == 401


class TestGetItems:
    def test_get_all_items(self):
        response = client.get("/items/", headers=AUTH_HEADER)
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_item_structure(self):
        response = client.get("/items/", headers=AUTH_HEADER)
        item = response.json()[0]
        assert "id" in item
        assert "name" in item
        assert "price" in item
        assert "in_stock" in item


class TestGetItem:
    def test_get_existing_item(self):
        response = client.get("/items/1", headers=AUTH_HEADER)
        assert response.status_code == 200
        assert response.json()["name"] == "Laptop"

    def test_get_nonexistent_item(self):
        response = client.get("/items/999", headers=AUTH_HEADER)
        assert response.status_code == 404


class TestCreateItem:
    def test_create_item(self):
        response = client.post("/items/", json={"name": "Camera", "price": 599.99}, headers=AUTH_HEADER)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Camera"
        assert data["price"] == 599.99
        assert data["in_stock"] is True
        assert data["id"] == 4

    def test_create_item_in_stock_false(self):
        response = client.post("/items/", json={"name": "Drone", "price": 799.99, "in_stock": False}, headers=AUTH_HEADER)
        assert response.status_code == 201
        assert response.json()["in_stock"] is False


class TestUpdateItem:
    def test_update_item_name(self):
        response = client.put("/items/1", json={"name": "Gaming Laptop"}, headers=AUTH_HEADER)
        assert response.status_code == 200
        assert response.json()["name"] == "Gaming Laptop"
        assert response.json()["price"] == 999.99

    def test_update_item_price(self):
        response = client.put("/items/1", json={"price": 899.99}, headers=AUTH_HEADER)
        assert response.status_code == 200
        assert response.json()["price"] == 899.99

    def test_update_item_stock(self):
        response = client.put("/items/1", json={"in_stock": False}, headers=AUTH_HEADER)
        assert response.status_code == 200
        assert response.json()["in_stock"] is False

    def test_update_nonexistent_item(self):
        response = client.put("/items/999", json={"name": "foo"}, headers=AUTH_HEADER)
        assert response.status_code == 404


class TestDeleteItem:
    def test_delete_item(self):
        response = client.delete("/items/1", headers=AUTH_HEADER)
        assert response.status_code == 200
        assert response.json()["name"] == "Laptop"

    def test_delete_item_reduces_count(self):
        client.delete("/items/1", headers=AUTH_HEADER)
        response = client.get("/items/", headers=AUTH_HEADER)
        assert len(response.json()) == 2

    def test_delete_nonexistent_item(self):
        response = client.delete("/items/999", headers=AUTH_HEADER)
        assert response.status_code == 404


class TestSearch:
    def test_search_existing(self):
        response = client.get("/items/search", params={"name": "lap"}, headers=AUTH_HEADER)
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Laptop"

    def test_search_case_insensitive(self):
        response = client.get("/items/search", params={"name": "PHONE"}, headers=AUTH_HEADER)
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_search_no_results(self):
        response = client.get("/items/search", params={"name": "xyz"}, headers=AUTH_HEADER)
        assert response.status_code == 200
        assert response.json() == []


class TestRoot:
    def test_root_returns_html(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "Item Manager" in response.text
