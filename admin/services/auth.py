"""后台认证辅助。"""
from __future__ import annotations

from datetime import datetime

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt

from shared import settings

security = HTTPBearer(auto_error=False)


def get_current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict[str, str]:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:  # type: ignore[attr-defined]
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
    if payload.get("exp") and datetime.utcfromtimestamp(payload["exp"]) < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    return {"username": payload.get("sub", "unknown"), "role": payload.get("role", "user")}
