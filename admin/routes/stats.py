"""统计路由。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shared.db import get_session
from shared.repository import summarize_orders
from ..services.auth import get_current_user

router = APIRouter(tags=["stats"], dependencies=[Depends(get_current_user)])


@router.get("/stats/summary")
async def summary(session: AsyncSession = Depends(get_session)) -> dict[str, int | float]:
    return await summarize_orders(session)
