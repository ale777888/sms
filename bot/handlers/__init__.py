"""注册所有 handler。"""
from __future__ import annotations

from aiogram import Dispatcher

from . import start, menu, orders, wallet, projects, countries, help_cmd


def register_handlers(dp: Dispatcher) -> None:
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(orders.router)
    dp.include_router(wallet.router)
    dp.include_router(projects.router)
    dp.include_router(countries.router)
    dp.include_router(help_cmd.router)
