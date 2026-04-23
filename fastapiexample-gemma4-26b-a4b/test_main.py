import pytest
from httpx import AsyncClient, ASGITransport
from main import app
import routes.items as items_module

AUTH_HEADER = {"Authorization": "Basic YWRtaW46YWRtaW4xMjM="}

@pytest.fixture(autouse=True)
def reset_db():
    items_module.items_db = [
        {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10},
        {"id": 2, "name": "Mouse", "price": 25.50, "stock": 0},
        {"id": 3, "name": "Keyboard", "price": 75.00, "stock": 5},
    ]

@pytest.fixture
def client():
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

@pytest.mark.asyncio
async def test_01(client):
    response = await client.get("/")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_02(client):
    response = await client.get("/items/", headers={})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_03(client):
    response = await client.get("/items/", headers={"Authorization": "Basic dXNlcjpwYXNz"})
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_04(client):
    response = await client.get("/items/", headers=AUTH_HEADER)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_05(client):
    response = await client.get("/items/", headers=AUTH_HEADER)
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_06(client):
    response = await client.get("/items/1", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert response.json()["name"] == "Laptop"

@pytest.mark.asyncio
async def test_07(client):
    response = await client.get("/items/999", headers=AUTH_HEADER)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_08(client):
    new_item = {"id": 10, "name": "Tablet", "price": 299.99, "stock": 5}
    response = await client.post("/items/", json=new_item, headers=AUTH_HEADER)
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_09(client):
    updated_item = {"id": 1, "name": "Updated", "price": 899.99, "stock": 5}
    response = await client.put("/items/1", json=updated_item, headers=AUTH_HEADER)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_10(client):
    response = await client.delete("/items/2", headers=AUTH_HEADER)
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_11(client):
    response = await client.get("/items/search?name=Laptop", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert len(response.json()) >= 1

@pytest.mark.asyncio
async def test_12(client):
    response = await client.get("/items/search?name=NonExistent", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert len(response.json()) == 0

@pytest.mark.asyncio
async def test_13(client):
    duplicate_item = {"id": 1, "name": "Duplicate", "price": 1.0, "stock": 1}
    response = await client.post("/items/", json=duplicate_item, headers=AUTH_HEADER)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_14(client):
    updated_item = {"id": 999, "name": "No", "price": 1.0, "stock": 1}
    response = await client.put("/items/999", json=updated_item, headers=AUTH_HEADER)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_15(client):
    response = await client.delete("/items/999", headers=AUTH_HEADER)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_16(client):
    response = await client.get("/items/search?name=laptop", headers=AUTH_HEADER)
    assert response.status_code == 200
    assert len(response.json()) >= 1

@pytest.mark.asyncio
async def test_17(client):
    new_item = {"id": 11, "name": "Monitor", "price": 150.0, "stock": 2}
    response = await client.post("/items/", json=new_item, headers=AUTH_HEADER)
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_18(client):
    response = await client.get("/items/", headers=AUTH_HEADER)
    data = response.json()
    assert len(data) >= 1

@pytest.mark.asyncio
async def test_19(client):
    updated_item = {"id": 1, "name": "Laptop", "price": 500.0, "stock": 1}
    response = await client.put("/items/1", json=updated_item, headers=AUTH_HEADER)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_20(client):
    response1 = await client.get("/items/", headers=AUTH_HEADER)
    count1 = len(response1.json())
    await client.delete("/items/3", headers=AUTH_HEADER)
    response2 = await client.get("/items/", headers=AUTH_HEADER)
    count2 = len(response2.json())
    assert count2 == count1 - 1
