"""主菜单消息处理。"""
from __future__ import annotations

import html
from collections import defaultdict
from typing import Iterable

from aiogram import F, Router
from aiogram.types import Message

from shared import settings
from shared.db import async_session
from shared.exceptions import SmsApiError
from shared.repository import get_or_create_user, list_user_orders
from shared.sms_client import PriceItem, get_sms_client
from ..keyboards.projects import build_project_keyboard

router = Router(name="menu")
_sms_client = get_sms_client(base_url=settings.base_url, token=settings.sms_token)

STATUS_LABELS = {
    "created": "待领取",
    "polling": "收码中",
    "received": "已收码",
    "released": "已释放",
    "timeout": "已超时",
    "failed": "失败",
    "blacklisted": "已加黑",
}


def _summarise_projects(prices: Iterable[PriceItem]) -> list[tuple[int, str, float]]:
    summary: dict[int, tuple[str, float]] = {}
    for item in prices:
        current = summary.get(item.game_id)
        if current is None or item.game_money < current[1]:
            summary[item.game_id] = (item.game_name, item.game_money)
    data = [(pid, name, price) for pid, (name, price) in summary.items()]
    data.sort(key=lambda e: e[0])
    return data


@router.message(F.text.in_({"📲 取号", "🧩 项目"}))
async def handle_pick_project(message: Message) -> None:
    try:
        price_list = await _sms_client.get_price_list()
    except SmsApiError as exc:
        await message.answer(f"获取价目失败：{html.escape(str(exc))}")
        return
    projects = _summarise_projects(price_list)
    if not projects:
        await message.answer("未获取到任何项目，请稍后再试。")
        return
    await message.answer(
        "请选择项目：",
        reply_markup=build_project_keyboard(projects, currency=settings.price_currency),
    )


@router.message(F.text == "🧾 订单")
async def handle_orders(message: Message) -> None:
    async with async_session() as session:
        user = await get_or_create_user(session, tg_id=message.from_user.id)
        orders = await list_user_orders(session, user_id=user.id, limit=5)
        await session.commit()
    if not orders:
        await message.answer("暂无订单记录，先去取号试试吧。")
        return
    lines = ["<b>最近订单</b>"]
    for order in orders:
        status = STATUS_LABELS.get(order.status, order.status)
        lines.append(
            f"#{order.id} · 项目 {order.project_id} · {order.country} · {status}"
        )
        phone = order.phone or "待分配"
        lines.append(
            f"号码：{phone}  单价：{order.unit_price:g}{settings.price_currency}"
        )
        if order.sms_text:
            escaped = html.escape(order.sms_text)
            lines.append(f"短信：<code>{escaped}</code>")
        lines.append("")
    lines.append("如需收码/释放，请使用订单消息中的按钮。")
    await message.answer("\n".join(lines))


@router.message(F.text == "📩 收码")
async def handle_collect_hint(message: Message) -> None:
    await message.answer("请选择具体订单的“开始收码”按钮，系统会自动为您轮询验证码。")


@router.message(F.text == "💳 余额")
async def handle_wallet(message: Message) -> None:
    try:
        info = await _sms_client.my_info()
    except SmsApiError as exc:
        await message.answer(f"查询余额失败：{html.escape(str(exc))}")
        return
    await message.answer(f"账户余额：{info.balance:g}{settings.price_currency}")


@router.message(F.text == "🌍 国家")
async def handle_country(message: Message) -> None:
    try:
        prices = await _sms_client.get_price_list()
    except SmsApiError as exc:
        await message.answer(f"加载国家列表失败：{html.escape(str(exc))}")
        return
    countries: dict[str, list[str]] = defaultdict(list)
    for item in prices:
        countries[item.country_id].append(item.country_title)
    if not countries:
        await message.answer("尚未获取到国家数据。")
        return
    lines = ["<b>支持的国家</b>"]
    for code, names in sorted(countries.items()):
        label = sorted(set(names))[0]
        lines.append(f"{code} · {label}")
    await message.answer("\n".join(lines))


@router.message(F.text == "🛒 充值")
async def handle_recharge(message: Message) -> None:
    await message.answer(
        "充值功能暂未开放，请联系管理员获取 USDT(TRC20) 充值指引。"
    )


@router.message(F.text == "🆘 帮助")
async def handle_help_hint(message: Message) -> None:
    await message.answer(
        "如需帮助，请使用 /help 命令查看详细指引或联系管理员。",
    )
