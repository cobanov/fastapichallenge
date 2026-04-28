from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional
from auth import get_current_user, security

router = APIRouter(prefix="/items", tags=["items"])

items_db: dict[int, dict] = {
    1: {"id": 1, "name": "Laptop", "price": 999.99, "stock": 50},
    2: {"id": 2, "name": "Mouse", "price": 29.99, "stock": 200},
    3: {"id": 3, "name": "Keyboard", "price": 79.99, "stock": 150},
    4: {"id": 4, "name": "Monitor", "price": 449.99, "stock": 0},
    5: {"id": 5, "name": "Headphones", "price": 149.99, "stock": 75},
}
next_id = 6


class ItemCreate(BaseModel):
    name: str
    price: float
    stock: int = 0


class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None


@router.get("/")
async def list_items(username: str = Depends(get_current_user)):
    return list(items_db.values())


@router.get("/search")
async def search_items(
    name: str = Query(..., min_length=1),
    username: str = Depends(get_current_user),
):
    results = [
        item
        for item in items_db.values()
        if name.lower() in item["name"].lower()
    ]
    return results


@router.get("/{item_id}")
async def get_item(item_id: int, username: str = Depends(get_current_user)):
    item = items_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.post("/", status_code=201)
async def create_item(
    item: ItemCreate, username: str = Depends(get_current_user)
):
    global next_id
    new_item = {"id": next_id, **item.model_dump()}
    items_db[next_id] = new_item
    next_id += 1
    return new_item


@router.put("/{item_id}")
async def update_item(
    item_id: int,
    item_update: ItemUpdate,
    username: str = Depends(get_current_user),
):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    existing = items_db[item_id]
    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        existing[key] = value
    items_db[item_id] = existing
    return existing


@router.delete("/{item_id}")
async def delete_item(item_id: int, username: str = Depends(get_current_user)):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    deleted = items_db.pop(item_id)
    return {"detail": "Item deleted", "item": deleted}
