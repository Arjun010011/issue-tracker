from datetime import datetime, timedelta, timezone
import os

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def create_access_token(claims: dict[str, object]) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        **claims,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid token",
            )
        return user_id
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        )
