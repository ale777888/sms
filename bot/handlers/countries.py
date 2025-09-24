"""国家选择相关回调。"""
from __future__ import annotations

import html
from typing import Iterable

from aiogram.filters import Text
from aiogram import Router
from aiogram.types import CallbackQuery

from shared import settings
from shared.exceptions import SmsApiError
from shared.sms_client import PriceItem, get_sms_client
from ..keyboards.countries import build_country_keyboard

router = Router(name="countries")
_sms_client = get_sms_client(base_url=settings.base_url, token=settings.sms_token)


def _collect_countries(prices: Iterable[PriceItem], project_id: int | None = None) -> list[tuple[str, str]]:
    mapping: dict[str, str] = {}
    for item in prices:
        if project_id is not None and item.game_id != project_id:
            continue
        mapping[item.country_id] = item.country_title
    countries = [(code, title) for code, title in mapping.items()]
    countries.sort(key=lambda x: x[0])
    return countries


@router.callback_query(Text(startswith="country_page"))
async def callback_country_page(query: CallbackQuery) -> None:
    parts = query.data.split(":")
    try:
        if len(parts) == 2:
            project_id = None
            page = int(parts[1])
        else:
            project_id = int(parts[1]) if parts[1] else None
            page = int(parts[2])
    except ValueError:
        await query.answer("分页参数错误", show_alert=True)
        return
    try:
        price_list = await _sms_client.get_price_list()
    except SmsApiError as exc:
        await query.answer(f"刷新失败：{html.escape(str(exc))}", show_alert=True)
        return
    countries = _collect_countries(price_list, project_id)
    if not countries:
        await query.answer("没有更多国家", show_alert=True)
        return
    await query.message.edit_reply_markup(
        reply_markup=build_country_keyboard(countries, page=page, project_id=project_id or None)
    )
    await query.answer()


@router.callback_query(Text(startswith="country:"))
async def callback_country(query: CallbackQuery) -> None:
    payload = query.data.split(":", 1)[1]
    await query.answer(f"已选择国家 {payload}，请继续选择项目。", show_alert=True)
