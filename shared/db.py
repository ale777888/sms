"""数据库初始化与会话管理。"""
from __future__ import annotations

from pathlib import Path
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .settings import settings


def _to_async_dsn(dsn: str) -> str:
    if dsn.startswith("sqlite+aiosqlite"):
        return dsn
    if dsn.startswith("sqlite:///"):
        return "sqlite+aiosqlite://" + dsn[len("sqlite://") :]
    return dsn


ASYNC_DATABASE_URL = _to_async_dsn(settings.db_url)


class Base(DeclarativeBase):
    """通用基类。"""


async_engine: AsyncEngine = create_async_engine(ASYNC_DATABASE_URL, future=True, echo=False)
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session


async def init_db() -> None:
    """确保 SQLite 数据文件目录存在。"""

    if settings.db_url.startswith("sqlite"):
        target = settings.db_url.split("///", maxsplit=1)[-1]
        if target == ":memory:":
            return
        path = Path(target).expanduser().resolve().parent
        path.mkdir(parents=True, exist_ok=True)


__all__ = ["Base", "async_engine", "async_session", "get_session", "init_db"]
