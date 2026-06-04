from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, Header, HTTPException
from jose import JWTError, jwt
from passlib.context import CryptContext

from . import store
from .settings import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(pw: str) -> str:
    return pwd_context.hash(pw)


def verify_password(pw: str, pw_hash: str) -> bool:
    return pwd_context.verify(pw, pw_hash)


def create_token(username: str) -> str:
    now = datetime.now(tz=timezone.utc)
    payload = {"sub": username, "iat": int(now.timestamp()), "exp": int((now + timedelta(days=7)).timestamp())}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])


async def require_admin_jwt(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")
    except (JWTError, HTTPException) as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(status_code=401, detail="Invalid token") from e

    if username == settings.admin_username:
        return username

    try:
        u = await store.find_admin_by_username(username)
        if not u:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
