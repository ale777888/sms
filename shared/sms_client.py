"""短信平台请求封装。"""
from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, Iterable, List
from urllib.parse import urlencode

import httpx

from .exceptions import SmsApiError, SmsPendingError


LOGGER = logging.getLogger("tg_sms_suite.sms")


ERROR_MESSAGES: Dict[str, str] = {
    "-1": "Token 不允许为空",
    "-2": "账号已被禁用",
    "-3": "Token 不存在",
    "-4": "项目 ID 不允许为空",
    "-5": "项目 ID 不存在或等待验证码",
    "-6": "国家代码不允许为空",
    "-7": "国家代码有误",
    "-8": "余额不足，请充值",
    "-9": "占号过多，请先释放或补充余额",
    "-10": "指定号码有误",
    "-11": "指定号段有误",
    "-12": "暂时无号码",
}


@dataclass(slots=True)
class UserInfo:
    balance: float


@dataclass(slots=True)
class PriceItem:
    game_id: int
    game_name: str
    game_money: float
    country_id: str
    country_title: str


@dataclass(slots=True)
class PhoneOrder:
    pkey: str
    phone: str


def mask_token(token: str) -> str:
    if len(token) <= 6:
        return "***"
    return f"{token[:3]}***{token[-3:]}"


class SmsClient:
    """封装短信平台所有 GET 调用。"""

    def __init__(self, *, base_url: str, token: str, timeout: float = 12.0, retries: int = 3) -> None:
        self._base_url = base_url.rstrip("?")
        self._token = token
        self._timeout = timeout
        self._retries = retries
        self._client = httpx.AsyncClient(timeout=timeout)

    def _build_url(self, params: Dict[str, Any]) -> str:
        query = urlencode({"token": self._token, **params})
        return f"{self._base_url}?{query}"

    async def _get(self, params: Dict[str, Any]) -> str:
        attempt = 0
        delay = 1.5
        while True:
            attempt += 1
            url = self._build_url(params)
            started = time.perf_counter()
            try:
                response = await self._client.get(url)
                elapsed = int((time.perf_counter() - started) * 1000)
                LOGGER.info(
                    "sms_call",
                    extra={
                        "url": url.replace(self._token, mask_token(self._token)),
                        "status": response.status_code,
                        "elapsed_ms": elapsed,
                    },
                )
                response.raise_for_status()
                return response.text.strip()
            except Exception as exc:  # noqa: BLE001
                LOGGER.warning(
                    "sms_retry",
                    extra={"attempt": attempt, "params": params, "error": repr(exc)},
                )
                if attempt >= self._retries:
                    raise
                await asyncio.sleep(delay + random.uniform(0, delay / 2))
                delay = min(delay * 2, 30)

    def _raise_error(self, code: str) -> None:
        message = ERROR_MESSAGES.get(code, f"接口返回错误代码 {code}")
        raise SmsApiError(code=code, message=message)

    async def _request(self, *, act: str, **params: Any) -> List[str]:
        raw = await self._get({"act": act, **params})
        if not raw:
            raise SmsApiError(code="empty", message="接口返回空响应")
        parts = raw.split("|")
        flag = parts[0]
        if flag == "1":
            return parts[1:]
        if flag == "0":
            code = parts[1] if len(parts) > 1 else "unknown"
            if act == "getPhoneCode" and code == "-5":
                raise SmsPendingError(code=code, message="等待验证码")
            self._raise_error(code)
        raise SmsApiError(code="unexpected", message=f"无法解析接口响应: {raw}")

    async def my_info(self) -> UserInfo:
        payload = await self._request(act="myInfo")
        if not payload:
            raise SmsApiError(code="format", message="用户信息为空")
        try:
            balance = float(payload[0])
        except (TypeError, ValueError) as exc:  # pragma: no cover - 防御性处理
            raise SmsApiError(code="format", message=f"无法解析余额: {payload[0]}") from exc
        return UserInfo(balance=balance)

    async def get_price_list(self, *, key: str | None = None) -> list[PriceItem]:
        payload = await self._request(act="getItem", **({"key": key} if key else {}))
        if not payload:
            return []
        data = payload[0]
        try:
            raw_items = json.loads(data)
        except json.JSONDecodeError as exc:
            raise SmsApiError(code="format", message="无法解析价格列表 JSON") from exc
        items: list[PriceItem] = []
        for entry in raw_items if isinstance(raw_items, Iterable) else []:
            try:
                items.append(
                    PriceItem(
                        game_id=int(entry["Game_ID"]),
                        game_name=str(entry["Game_Name"]),
                        game_money=float(entry["Game_Money"]),
                        country_id=str(entry["Country_ID"]),
                        country_title=str(entry["Country_Title"]),
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                LOGGER.warning("price_parse_error", extra={"entry": entry, "error": repr(exc)})
        return items

    async def get_phone(self, *, country: str, project_id: int, mobile: str | None = None, seq: str | None = None) -> PhoneOrder:
        params: Dict[str, Any] = {"country": country, "gameid": project_id}
        if mobile:
            params["mobile"] = mobile
        if seq:
            params["seq"] = seq
        payload = await self._request(act="getPhone", **params)
        if len(payload) < 2:
            raise SmsApiError(code="format", message=f"获取手机号返回异常: {payload}")
        return PhoneOrder(pkey=payload[0], phone=payload[1])

    async def get_phone_code(self, *, pkey: str) -> str:
        payload = await self._request(act="getPhoneCode", pkey=pkey)
        if not payload:
            raise SmsApiError(code="format", message="验证码返回为空")
        return payload[0]

    async def send_code(self, *, pkey: str, receiver: str, smscontent: str) -> None:
        await self._request(act="sendCode", pkey=pkey, receiver=receiver, smscontent=smscontent)

    async def release(self, *, pkey: str) -> None:
        await self._request(act="setRel", pkey=pkey)

    async def add_black(self, *, pkey: str) -> None:
        await self._request(act="addBlack", pkey=pkey)

    async def close(self) -> None:
        await self._client.aclose()


@lru_cache(maxsize=1)
def get_sms_client(*, base_url: str, token: str) -> SmsClient:
    """按配置创建单例客户端。"""

    return SmsClient(base_url=base_url, token=token)


__all__ = [
    "SmsClient",
    "UserInfo",
    "PriceItem",
    "PhoneOrder",
    "mask_token",
    "get_sms_client",
]
