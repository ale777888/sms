"""自定义异常类型。"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SmsApiError(Exception):
    """短信平台接口返回的错误。"""

    code: str
    message: str

    def __str__(self) -> str:  # pragma: no cover - 简单包装
        return f"SMS API error [{self.code}]: {self.message}"


class SmsPendingError(SmsApiError):
    """验证码尚未返回时抛出的异常。"""


__all__ = ["SmsApiError", "SmsPendingError"]
