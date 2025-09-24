"""订单管理路由。"""
from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db import get_session
from shared.repository import as_float, list_orders
from ..services.auth import get_current_user

router = APIRouter(tags=["orders"], dependencies=[Depends(get_current_user)])


class OrderListItem(BaseModel):
    id: int
    user_id: int
    project_id: int
    country: str
    status: str
    phone: str | None
    unit_price: float
    created_at: datetime


@router.get("/orders", response_model=List[OrderListItem])
async def list_orders_route(
    session: AsyncSession = Depends(get_session),
) -> list[OrderListItem]:
    orders = await list_orders(session, limit=100)
    return [
        OrderListItem(
            id=order.id,
            user_id=order.user_id,
            project_id=order.project_id,
            country=order.country,
            status=order.status,
            phone=order.phone,
            unit_price=as_float(order.unit_price),
            created_at=order.created_at,
        )
        for order in orders
    ]
