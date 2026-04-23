from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Optional
from auth import authenticate

router = APIRouter(prefix="/items", dependencies=[Depends(authenticate)])

class Item(BaseModel):
    id: int
    name: str
    price: float
    stock: int

# In-memory database
items_db = [
    {"id": 1, "name": "Laptop", "price": 999.99, "stock": 10},
    {"id": 2, "name": "Mouse", "price": 25.50, "stock": 0},
    {"id": 3, "name": "Keyboard", "price": 75.00, "stock": 5},
]

@router.get("/", response_model=List[Item])
async def get_items():
    return items_db

@router.get("/search", response_model=List[Item])
async def search_items(name: str = Query(...)):
    return [item for item in items_db if name.lower() in item["name"].lower()]

@router.get("/{item_id}", response_model=Item)
async def get_item(item_id: int):
    item = next((item for item in items_db if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.post("/", response_model=Item, status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    if any(i["id"] == item.id for i in items_db):
        raise HTTPException(status_code=400, detail="Item ID already exists")
    items_db.append(item.dict())
    return item

@router.put("/{item_id}", response_model=Item)
async def update_item(item_id: int, updated_item: Item):
    for index, item in enumerate(items_db):
        if item["id"] == item_id:
            items_db[index] = updated_item.dict()
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    global items_db
    initial_len = len(items_db)
    items_db = [item for item in items_db if item["id"] != item_id]
    if len(items_db) == initial_len:
        raise HTTPException(status_code=404, detail="Item not found")
    return None
