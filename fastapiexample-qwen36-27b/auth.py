from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBasic

security = HTTPBasic()

VALID_CREDENTIALS = {
    "admin": "admin123",
    "user": "user123",
}


async def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username not in VALID_CREDENTIALS:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if credentials.password != VALID_CREDENTIALS[credentials.username]:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials.username
