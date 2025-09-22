"""认证路由（初版）。"""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import jwt

from shared import settings

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    expires_at: datetime


_FAKE_USERS = {
    "admin": {"password": "admin123", "role": "admin"},
    "support": {"password": "support123", "role": "support"},
}


@router.post("/auth/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    user = _FAKE_USERS.get(payload.username)
    if not user or user["password"] != payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    expires = datetime.utcnow() + timedelta(hours=8)
    token = jwt.encode({"sub": payload.username, "role": user["role"], "exp": expires}, settings.jwt_secret, algorithm="HS256")
    return LoginResponse(token=token, expires_at=expires)
