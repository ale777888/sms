"""统计路由（预览版）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from ..services.auth import get_current_user

router = APIRouter(tags=["stats"], dependencies=[Depends(get_current_user)])


@router.get("/stats/summary")
def summary() -> dict[str, int]:
    return {
        "orders_today": 0,
        "orders_success": 0,
        "orders_timeout": 0,
        "income": 0,
    }
