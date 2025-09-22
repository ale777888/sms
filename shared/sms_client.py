"""短信平台请求封装。"""
from __future__ import annotations

import asyncio
import logging
import random
import time
from typing import Dict
from urllib.parse import urlencode

import httpx


LOGGER = logging.getLogger("tg_sms_suite.sms")


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

    def _build_url(self, params: Dict[str, str]) -> str:
        query = urlencode({"token": self._token, **params})
        return f"{self._base_url}?{query}"

    async def _get(self, params: Dict[str, str]) -> str:
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

    async def get_phone(self, *, country: str, project_id: str) -> str:
        return await self._get({"act": "getPhone", "country": country, "gameid": project_id})

    async def get_message(self, *, pkey: str) -> str:
        return await self._get({"act": "getPhoneCode", "pkey": pkey})

    async def release(self, *, pkey: str) -> str:
        return await self._get({"act": "setRel", "pkey": pkey})

    async def add_black(self, *, pkey: str) -> str:
        return await self._get({"act": "addBlack", "pkey": pkey})

    async def close(self) -> None:
        await self._client.aclose()


__all__ = ["SmsClient", "mask_token"]
