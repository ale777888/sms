"""机器人运行状态容器。"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ActiveOrder:
    chat_id: int
    order_id: int
    pkey: str
    phone: str
    project_id: int
    country: str


@dataclass
class BotState:
    active_orders: Dict[int, ActiveOrder] = field(default_factory=dict)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, repr=False)

    async def track(self, order: ActiveOrder) -> None:
        async with self._lock:
            self.active_orders[order.order_id] = order

    async def release(self, order_id: int) -> None:
        async with self._lock:
            self.active_orders.pop(order_id, None)

    async def get(self, order_id: int) -> Optional[ActiveOrder]:
        async with self._lock:
            return self.active_orders.get(order_id)

    async def snapshot(self) -> List[ActiveOrder]:
        async with self._lock:
            return list(self.active_orders.values())

    async def shutdown(self) -> List[ActiveOrder]:
        async with self._lock:
            pending = list(self.active_orders.values())
            self.active_orders.clear()
            return pending


bot_state = BotState()

__all__ = ["bot_state", "BotState", "ActiveOrder"]
