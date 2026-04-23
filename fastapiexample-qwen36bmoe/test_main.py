import pytest
from httpx import AsyncClient, ASGITransport
from main import app
import base64

TRANSPORT = ASGITransport(app=app)
ADMIN_CREDS = base64.b64encode(b"admin:admin123").decode()
USER_CREDS = base64.b64encode(b"user:user123").decode()
INVALID_CREDS = base64.b64encode(b"admin:wrongpass").decode()

def _auth_header(creds):
    return {"Authorization": f"Basic {creds}"}


@pytest.mark.asyncio
async def test_auth_valid_admin():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.get("/items/", headers=_auth_header(ADMIN_CREDS))
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_auth_valid_user():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.get("/items/", headers=_auth_header(USER_CREDS))
        assert res.status_code == 200


@pytest.mark.asyncio
async def test_auth_invalid_credentials():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.get("/items/", headers=_auth_header(INVALID_CREDS))
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_auth_missing_credentials():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.get("/items/")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_get_items_empty():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.get("/items/", headers=_auth_header(ADMIN_CREDS))
        assert res.json() == []


@pytest.mark.asyncio
async def test_get_items_structure():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.post("/items/", headers=_auth_header(ADMIN_CREDS), data={"name": "Test", "price": 10.0, "stock": 5})
        assert res.status_code == 201
        res = await client.get("/items/", headers=_auth_header(ADMIN_CREDS))
        item = res.json()[0]
        assert "id" in item
        assert "name" in item
        assert "price" in item
        assert "stock" in item


@pytest.mark.asyncio
async def test_get_single_item():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.post("/items/", headers=_auth_header(ADMIN_CREDS), data={"name": "Single", "price": 5.5, "stock": 3})
        item_id = res.json()["id"]
        res = await client.get(f"/items/{item_id}", headers=_auth_header(ADMIN_CREDS))
        assert res.json()["name"] == "Single"


@pytest.mark.asyncio
async def test_get_item_404():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.get("/items/9999", headers=_auth_header(ADMIN_CREDS))
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_create_item():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.post("/items/", headers=_auth_header(ADMIN_CREDS), data={"name": "New Item", "price": 25.0, "stock": 10})
        assert res.status_code == 201
        data = res.json()
        assert data["name"] == "New Item"
        assert data["price"] == 25.0
        assert data["stock"] == 10


@pytest.mark.asyncio
async def test_create_item_default_stock():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.post("/items/", headers=_auth_header(ADMIN_CREDS), data={"name": "Default Stock", "price": 1.0, "stock": 0})
        assert res.json()["stock"] == 0


@pytest.mark.asyncio
async def test_update_item_name():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.post("/items/", headers=_auth_header(ADMIN_CREDS), data={"name": "Old", "price": 10, "stock": 5})
        item_id = res.json()["id"]
        res = await client.put(f"/items/{item_id}", headers=_auth_header(ADMIN_CREDS), data={"name": "Updated"})
        assert res.json()["name"] == "Updated"


@pytest.mark.asyncio
async def test_update_item_price():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.post("/items/", headers=_auth_header(ADMIN_CREDS), data={"name": "Price Test", "price": 10, "stock": 5})
        item_id = res.json()["id"]
        res = await client.put(f"/items/{item_id}", headers=_auth_header(ADMIN_CREDS), data={"price": 99.99})
        assert res.json()["price"] == 99.99


@pytest.mark.asyncio
async def test_update_item_stock():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.post("/items/", headers=_auth_header(ADMIN_CREDS), data={"name": "Stock Test", "price": 10, "stock": 5})
        item_id = res.json()["id"]
        res = await client.put(f"/items/{item_id}", headers=_auth_header(ADMIN_CREDS), data={"stock": 0})
        assert res.json()["stock"] == 0


@pytest.mark.asyncio
async def test_update_item_404():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.put("/items/9999", headers=_auth_header(ADMIN_CREDS), data={"name": "Nope"})
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_delete_item():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.post("/items/", headers=_auth_header(ADMIN_CREDS), data={"name": "To Delete", "price": 10, "stock": 5})
        item_id = res.json()["id"]
        res = await client.delete(f"/items/{item_id}", headers=_auth_header(ADMIN_CREDS))
        assert res.json()["name"] == "To Delete"


@pytest.mark.asyncio
async def test_delete_item_reduces_count():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        await client.post("/items/", headers=_auth_header(ADMIN_CREDS), data={"name": "Count Test", "price": 10, "stock": 5})
        res = await client.get("/items/", headers=_auth_header(ADMIN_CREDS))
        count_before = len(res.json())
        await client.delete(f"/items/{res.json()[0]['id']}", headers=_auth_header(ADMIN_CREDS))
        res = await client.get("/items/", headers=_auth_header(ADMIN_CREDS))
        assert len(res.json()) == count_before - 1


@pytest.mark.asyncio
async def test_delete_item_404():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.delete("/items/9999", headers=_auth_header(ADMIN_CREDS))
        assert res.status_code == 404


@pytest.mark.asyncio
async def test_search_existing():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        await client.post("/items/", headers=_auth_header(ADMIN_CREDS), data={"name": "Laptop", "price": 999, "stock": 3})
        res = await client.get("/items/search", headers=_auth_header(ADMIN_CREDS), params={"item_name": "lap"})
        assert len(res.json()) == 1


@pytest.mark.asyncio
async def test_search_case_insensitive():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        await client.post("/items/", headers=_auth_header(ADMIN_CREDS), data={"name": "Widget", "price": 10, "stock": 5})
        res = await client.get("/items/search", headers=_auth_header(ADMIN_CREDS), params={"item_name": "WID"})
        assert len(res.json()) == 1


@pytest.mark.asyncio
async def test_search_no_results():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.get("/items/search", headers=_auth_header(ADMIN_CREDS), params={"item_name": "nonexistent"})
        assert res.json() == []


@pytest.mark.asyncio
async def test_root_html():
    async with AsyncClient(transport=TRANSPORT, base_url="http://test") as client:
        res = await client.get("/", headers=_auth_header(ADMIN_CREDS))
        assert res.status_code == 200
        assert "text/html" in res.headers["content-type"]
