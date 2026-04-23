from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from routes.items import router as items_router
from auth import get_current_user

app = FastAPI(title="Item Manager API")

security = HTTPBasic()

app.include_router(items_router, prefix="/items", tags=["items"])


@app.get("/")
async def root(credentials: HTTPBasicCredentials = Depends(security)):
    get_current_user(credentials)
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/items/")
async def list_items_public():
    return []
