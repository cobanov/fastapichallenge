from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from auth import get_current_user

router = APIRouter(prefix="/items", tags=["Items"])

items = [
    {"id": 1, "name": "Laptop", "price": 999.99, "in_stock": True},
    {"id": 2, "name": "Phone", "price": 699.99, "in_stock": True},
    {"id": 3, "name": "Tablet", "price": 449.99, "in_stock": False},
]

class Item(BaseModel):
    name: str
    price: float
    in_stock: bool = True

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    in_stock: Optional[bool] = None


@router.get("/", response_model=list[dict])
def get_items(user: str = Depends(get_current_user)):
    return items


@router.get("/search")
def search_items(name: str, user: str = Depends(get_current_user)):
    results = [item for item in items if name.lower() in item["name"].lower()]
    return results


@router.get("/{item_id}")
def get_item(item_id: int, user: str = Depends(get_current_user)):
    for item in items:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.post("/", status_code=201)
def create_item(item: Item, user: str = Depends(get_current_user)):
    new_id = max(i["id"] for i in items) + 1 if items else 1
    new_item = {"id": new_id, **item.model_dump()}
    items.append(new_item)
    return new_item


@router.put("/{item_id}")
def update_item(item_id: int, item: ItemUpdate, user: str = Depends(get_current_user)):
    for item_entry in items:
        if item_entry["id"] == item_id:
            for key, value in item.model_dump(exclude_unset=True).items():
                item_entry[key] = value
            return item_entry
    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/{item_id}")
def delete_item(item_id: int, user: str = Depends(get_current_user)):
    for index, item_entry in enumerate(items):
        if item_entry["id"] == item_id:
            return items.pop(index)
    raise HTTPException(status_code=404, detail="Item not found")
