"""订单管理路由（预览版）。"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..services.auth import get_current_user

router = APIRouter(tags=["orders"], dependencies=[Depends(get_current_user)])


class OrderListItem(BaseModel):
    id: int
    user_id: int
    project_id: int
    country: str
    status: str


@router.get("/orders", response_model=List[OrderListItem])
def list_orders() -> list[OrderListItem]:
    return [
        OrderListItem(id=1, user_id=100, project_id=1001, country="chn", status="created"),
    ]
