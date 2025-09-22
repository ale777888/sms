"""领域模型定义。"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class OrderStatus(str, Enum):
    created = "created"
    polling = "polling"
    received = "received"
    released = "released"
    timeout = "timeout"
    failed = "failed"
    blacklisted = "blacklisted"


class TransactionType(str, Enum):
    recharge = "recharge"
    freeze = "freeze"
    unfreeze = "unfreeze"
    consume = "consume"
    refund = "refund"
    adjust = "adjust"


@dataclass
class Project:
    id: int
    name: str
    aliases: list[str]
    enabled: bool = True


@dataclass
class PriceRule:
    id: int
    project_id: int
    country: str
    price: float
    currency: str
    active_from: Optional[datetime] = None
    active_to: Optional[datetime] = None
    overrides: Dict[str, Any] | None = None


@dataclass
class Order:
    id: int
    user_id: int
    country: str
    project_id: int
    unit_price: float
    phone: Optional[str] = None
    pkey: Optional[str] = None
    status: OrderStatus = OrderStatus.created
    sms_text: Optional[str] = None
    fail_code: Optional[str] = None
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()


@dataclass
class Transaction:
    id: int
    user_id: int
    order_id: Optional[int]
    tx_type: TransactionType
    amount: float
    meta: Dict[str, Any]
    created_at: datetime = datetime.utcnow()
