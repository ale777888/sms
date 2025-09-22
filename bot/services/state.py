"""机器人运行状态容器。"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ActiveOrder:
    chat_id: int
    order_id: int
    pkey: str


@dataclass
class BotState:
    active_orders: Dict[str, ActiveOrder] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)

    async def track(self, pkey: str, order: ActiveOrder) -> None:
        async with self._lock:
            self.active_orders[pkey] = order

    async def release(self, pkey: str) -> None:
        async with self._lock:
            self.active_orders.pop(pkey, None)

    async def shutdown(self) -> None:
        async with self._lock:
            self.active_orders.clear()
