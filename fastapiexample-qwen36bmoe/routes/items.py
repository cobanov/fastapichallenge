from fastapi import APIRouter, Depends, Form, HTTPException, status
from typing import Any, Dict, List, Optional
from auth import get_current_user

router = APIRouter(dependencies=[Depends(get_current_user)])

items_db: List[Dict[str, Any]] = []


def _next_id() -> int:
    return max((item["id"] for item in items_db), default=0) + 1


@router.get("/")
async def list_items():
    return items_db


@router.get("/search")
async def search_items(item_name: str):
    results = [item for item in items_db if item_name.lower() in item["name"].lower()]
    return results


@router.get("/{item_id}")
async def get_item(item_id: int):
    for item in items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item(
    name: str = Form(...),
    price: float = Form(...),
    stock: int = Form(0),
):
    item = {"id": _next_id(), "name": name, "price": price, "stock": stock}
    items_db.append(item)
    return item


@router.put("/{item_id}")
async def update_item(
    item_id: int,
    name: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    stock: Optional[int] = Form(None),
):
    for item in items_db:
        if item["id"] == item_id:
            if name is not None:
                item["name"] = name
            if price is not None:
                item["price"] = price
            if stock is not None:
                item["stock"] = stock
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.delete("/{item_id}")
async def delete_item(item_id: int):
    for i, item in enumerate(items_db):
        if item["id"] == item_id:
            return items_db.pop(i)
    raise HTTPException(status_code=404, detail="Item not found")
