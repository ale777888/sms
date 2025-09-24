"""项目选择回调。"""
from __future__ import annotations

import html
from typing import Iterable

from aiogram import F, Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery

from shared import settings
from shared.exceptions import SmsApiError
from shared.sms_client import PriceItem, get_sms_client
from ..keyboards.countries import build_country_keyboard
from ..keyboards.projects import build_project_keyboard

router = Router(name="projects")
_sms_client = get_sms_client(base_url=settings.base_url, token=settings.sms_token)


def _summarise_projects(prices: Iterable[PriceItem]) -> list[tuple[int, str, float]]:
    summary: dict[int, tuple[str, float]] = {}
    for item in prices:
        current = summary.get(item.game_id)
        if current is None or item.game_money < current[1]:
            summary[item.game_id] = (item.game_name, item.game_money)
    data = [(pid, name, price) for pid, (name, price) in summary.items()]
    data.sort(key=lambda e: e[0])
    return data


def _collect_countries(prices: Iterable[PriceItem], project_id: int) -> list[tuple[str, str]]:
    mapping: dict[str, str] = {}
    for item in prices:
        if item.game_id != project_id:
            continue
        mapping[item.country_id] = item.country_title
    countries = [(code, title) for code, title in mapping.items()]
    countries.sort(key=lambda x: x[0])
    return countries


@router.callback_query(Text(startswith="project_page:"))
async def callback_project_page(query: CallbackQuery) -> None:
    try:
        _, page_text = query.data.split(":", 1)
        page = int(page_text)
    except ValueError:
        await query.answer("分页参数解析失败", show_alert=True)
        return
    try:
        price_list = await _sms_client.get_price_list()
    except SmsApiError as exc:
        await query.answer(f"刷新失败：{html.escape(str(exc))}", show_alert=True)
        return
    projects = _summarise_projects(price_list)
    await query.message.edit_reply_markup(
        reply_markup=build_project_keyboard(projects, page=page, currency=settings.price_currency)
    )
    await query.answer()


@router.callback_query(Text(startswith="project:"))
async def callback_project(query: CallbackQuery) -> None:
    payload = query.data.split(":", 1)[1]
    if payload == "fav":
        await query.answer("收藏功能即将上线。", show_alert=True)
        return
    try:
        project_id = int(payload)
    except ValueError:
        await query.answer("项目参数错误", show_alert=True)
        return
    try:
        price_list = await _sms_client.get_price_list()
    except SmsApiError as exc:
        await query.answer(f"加载国家失败：{html.escape(str(exc))}", show_alert=True)
        return
    projects = _summarise_projects(price_list)
    project_name = next((name for pid, name, _ in projects if pid == project_id), None)
    countries = _collect_countries(price_list, project_id)
    if not countries:
        await query.answer("该项目暂未开放号码", show_alert=True)
        return
    await query.message.answer(
        f"请选择 <b>{html.escape(project_name or str(project_id))}</b> 的国家：",
        reply_markup=build_country_keyboard(countries, project_id=project_id),
    )
    await query.answer()
