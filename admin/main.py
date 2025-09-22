"""FastAPI 后台入口（初版）。"""
from __future__ import annotations

from fastapi import FastAPI

from .routes import auth, stats, orders

app = FastAPI(title="tg-sms-admin", version="0.1.0-preview")

app.include_router(auth.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(orders.router, prefix="/api")


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok"}
