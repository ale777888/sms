"""定价匹配引擎。"""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional

from .models import PriceRule


class PricingEngine:
    """根据项目与国家选择适用价格。"""

    def __init__(self, rules: Iterable[PriceRule]) -> None:
        self._rules = list(rules)

    def match_price(self, project_id: int, country: str, user_id: Optional[int] = None) -> Optional[PriceRule]:
        now = datetime.utcnow()
        candidates: list[PriceRule] = []
        for rule in self._rules:
            if rule.project_id != project_id or rule.country.lower() != country.lower():
                continue
            if rule.active_from and rule.active_from > now:
                continue
            if rule.active_to and rule.active_to < now:
                continue
            if user_id and rule.overrides and str(user_id) in rule.overrides:
                return rule
            candidates.append(rule)
        if not candidates:
            return None
        return min(candidates, key=lambda item: item.price)


__all__ = ["PricingEngine"]
