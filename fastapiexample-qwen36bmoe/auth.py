from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

USERS = {
    "admin": "admin123",
    "user": "user123",
}


def get_current_user(
    credentials: HTTPBasicCredentials = Depends(security),
):
    username = credentials.username
    password = credentials.password
    if username not in USERS or USERS[username] != password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return {"username": username}
