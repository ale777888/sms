"""数据访问封装。"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Iterable, Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .db_models import Order, Project, User
from .models import OrderStatus


async def get_or_create_user(session: AsyncSession, *, tg_id: int) -> User:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
    if user:
        return user
    user = User(tg_id=tg_id, role="user")
    session.add(user)
    await session.flush()
    return user


async def ensure_project(session: AsyncSession, *, project_id: int, name: str, aliases: str | None = None) -> Project:
    project = await session.get(Project, project_id)
    if project is None:
        project = Project(id=project_id, name=name, aliases=aliases or "", enabled=True)
        session.add(project)
        await session.flush()
        return project
    updated = False
    if project.name != name:
        project.name = name
        updated = True
    if aliases and project.aliases != aliases:
        project.aliases = aliases
        updated = True
    if not project.enabled:
        project.enabled = True
        updated = True
    if updated:
        await session.flush()
    return project


async def create_order(
    session: AsyncSession,
    *,
    user_id: int,
    project_id: int,
    country: str,
    unit_price: float,
    phone: str,
    pkey: str,
    status: OrderStatus,
) -> Order:
    order = Order(
        user_id=user_id,
        project_id=project_id,
        country=country,
        unit_price=unit_price,
        phone=phone,
        pkey=pkey,
        status=status.value,
    )
    session.add(order)
    await session.flush()
    return order


async def get_order(session: AsyncSession, *, order_id: int) -> Order | None:
    return await session.get(Order, order_id)


async def update_order_status(
    session: AsyncSession,
    *,
    order_id: int,
    status: OrderStatus,
    sms_text: str | None = None,
    fail_code: str | None = None,
) -> Order | None:
    order = await session.get(Order, order_id)
    if order is None:
        return None
    order.status = status.value
    if sms_text is not None:
        order.sms_text = sms_text
    if fail_code is not None:
        order.fail_code = fail_code
    order.updated_at = datetime.utcnow()
    await session.flush()
    return order


async def list_user_orders(
    session: AsyncSession,
    *,
    user_id: int,
    limit: int = 10,
) -> list[Order]:
    stmt: Select[tuple[Order]] = select(Order).where(Order.user_id == user_id).order_by(Order.id.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars())


async def list_orders(session: AsyncSession, *, limit: int = 100) -> list[Order]:
    stmt: Select[tuple[Order]] = select(Order).order_by(Order.id.desc()).limit(limit)
    result = await session.execute(stmt)
    return list(result.scalars())


async def summarize_orders(session: AsyncSession) -> dict[str, int | float]:
    stmt = select(Order.status, func.count()).group_by(Order.status)
    result = await session.execute(stmt)
    counts = {row[0]: row[1] for row in result}
    total = sum(counts.values())
    received = counts.get(OrderStatus.received.value, 0)
    timeout = counts.get(OrderStatus.timeout.value, 0)
    released = counts.get(OrderStatus.released.value, 0)
    active = counts.get(OrderStatus.polling.value, 0) + counts.get(OrderStatus.created.value, 0)
    failed = counts.get(OrderStatus.failed.value, 0)
    blacklisted = counts.get(OrderStatus.blacklisted.value, 0)

    stmt_income = select(func.coalesce(func.sum(Order.unit_price), 0.0))
    income_result = await session.execute(stmt_income)
    total_income: float = float(income_result.scalar_one() or 0.0)

    return {
        "orders_total": int(total),
        "orders_received": int(received),
        "orders_timeout": int(timeout),
        "orders_released": int(released),
        "orders_active": int(active),
        "orders_failed": int(failed),
        "orders_blacklisted": int(blacklisted),
        "total_income": total_income,
    }


def as_float(value: float | Decimal | None) -> float:
    if value is None:
        return 0.0
    if isinstance(value, Decimal):
        return float(value)
    return float(value)


__all__ = [
    "get_or_create_user",
    "ensure_project",
    "create_order",
    "get_order",
    "update_order_status",
    "list_user_orders",
    "list_orders",
    "summarize_orders",
    "as_float",
]
