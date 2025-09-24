"""订单相关回调。"""
from __future__ import annotations

import html

from aiogram import Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery

from shared import settings
from shared.db import async_session
from shared.exceptions import SmsApiError, SmsPendingError
from shared.models import OrderStatus
from shared.repository import (
    create_order,
    ensure_project,
    get_or_create_user,
    get_order,
    update_order_status,
)
from shared.sms_client import get_sms_client
from ..keyboards.orders import build_order_actions
from ..services.state import ActiveOrder, bot_state

router = Router(name="orders")
_sms_client = get_sms_client(base_url=settings.base_url, token=settings.sms_token)


async def _find_price(project_id: int, country_id: str):
    price_list = await _sms_client.get_price_list()
    for item in price_list:
        if item.game_id == project_id and item.country_id == country_id:
            return item
    return None


@router.callback_query(Text(startswith="order:new:"))
async def callback_new_order(query: CallbackQuery) -> None:
    parts = query.data.split(":")
    if len(parts) != 4:
        await query.answer("参数错误", show_alert=True)
        return
    try:
        project_id = int(parts[2])
    except ValueError:
        await query.answer("项目 ID 异常", show_alert=True)
        return
    country_id = parts[3]
    price_item = await _find_price(project_id, country_id)
    if price_item is None:
        await query.answer("未找到对应的价目", show_alert=True)
        return
    try:
        phone_info = await _sms_client.get_phone(country=country_id, project_id=project_id)
    except SmsApiError as exc:
        await query.answer(f"取号失败：{html.escape(str(exc))}", show_alert=True)
        return

    async with async_session() as session:
        user = await get_or_create_user(session, tg_id=query.from_user.id)
        await ensure_project(session, project_id=project_id, name=price_item.game_name)
        order = await create_order(
            session,
            user_id=user.id,
            project_id=project_id,
            country=country_id,
            unit_price=price_item.game_money,
            phone=phone_info.phone,
            pkey=phone_info.pkey,
            status=OrderStatus.polling,
        )
        await session.commit()
        order_id = order.id

    await bot_state.track(
        ActiveOrder(
            chat_id=query.message.chat.id,
            order_id=order_id,
            pkey=phone_info.pkey,
            phone=phone_info.phone,
            project_id=project_id,
            country=country_id,
        )
    )

    text = (
        f"订单 <b>#{order_id}</b> 已创建\n"
        f"项目：{html.escape(price_item.game_name)} ({project_id})\n"
        f"国家：{html.escape(price_item.country_title)} ({country_id})\n"
        f"手机号：<code>{phone_info.phone}</code>\n"
        f"单价：{price_item.game_money:g}{settings.price_currency}\n"
        "状态：收码中"
    )
    await query.message.answer(
        text,
        reply_markup=build_order_actions(order_id=order_id, status=OrderStatus.polling.value),
    )
    await query.answer("手机号已分配，开始收码吧！", show_alert=True)


@router.callback_query(Text(startswith="order:poll:"))
async def callback_poll(query: CallbackQuery) -> None:
    try:
        order_id = int(query.data.split(":")[2])
    except ValueError:
        await query.answer("订单参数错误", show_alert=True)
        return
    async with async_session() as session:
        order = await get_order(session, order_id=order_id)
        if order is None:
            await query.answer("未找到订单", show_alert=True)
            return
        if not order.pkey:
            await query.answer("该订单尚未完成取号", show_alert=True)
            return
        try:
            sms_text = await _sms_client.get_phone_code(pkey=order.pkey)
        except SmsPendingError:
            await query.answer("验证码尚未返回，请稍候再试。", show_alert=True)
            return
        except SmsApiError as exc:
            await query.answer(f"收码失败：{html.escape(str(exc))}", show_alert=True)
            return
        await update_order_status(
            session,
            order_id=order.id,
            status=OrderStatus.received,
            sms_text=sms_text,
            fail_code=None,
        )
        await session.commit()
    await bot_state.release(order_id)
    escaped = html.escape(sms_text)
    await query.message.answer(
        f"订单 <b>#{order_id}</b> 已收到验证码：\n<code>{escaped}</code>",
        reply_markup=build_order_actions(order_id=order_id, status=OrderStatus.received.value),
    )
    await query.answer("验证码已获取", show_alert=True)


@router.callback_query(Text(startswith="order:release:"))
async def callback_release(query: CallbackQuery) -> None:
    try:
        order_id = int(query.data.split(":")[2])
    except ValueError:
        await query.answer("订单参数错误", show_alert=True)
        return
    async with async_session() as session:
        order = await get_order(session, order_id=order_id)
        if order is None or not order.pkey:
            await query.answer("订单不存在或未取号", show_alert=True)
            return
        try:
            await _sms_client.release(pkey=order.pkey)
        except SmsApiError as exc:
            await query.answer(f"释放失败：{html.escape(str(exc))}", show_alert=True)
            return
        await update_order_status(session, order_id=order.id, status=OrderStatus.released)
        await session.commit()
    await bot_state.release(order_id)
    await query.message.answer(
        f"订单 <b>#{order_id}</b> 已释放。",
        reply_markup=build_order_actions(order_id=order_id, status=OrderStatus.released.value),
    )
    await query.answer("号码已释放", show_alert=True)


@router.callback_query(Text(startswith="order:black:"))
async def callback_black(query: CallbackQuery) -> None:
    try:
        order_id = int(query.data.split(":")[2])
    except ValueError:
        await query.answer("订单参数错误", show_alert=True)
        return
    async with async_session() as session:
        order = await get_order(session, order_id=order_id)
        if order is None or not order.pkey:
            await query.answer("订单不存在或未取号", show_alert=True)
            return
        try:
            await _sms_client.add_black(pkey=order.pkey)
        except SmsApiError as exc:
            await query.answer(f"加黑失败：{html.escape(str(exc))}", show_alert=True)
            return
        await update_order_status(session, order_id=order.id, status=OrderStatus.blacklisted)
        await session.commit()
    await bot_state.release(order_id)
    await query.message.answer(
        f"订单 <b>#{order_id}</b> 已加入黑名单。",
        reply_markup=build_order_actions(order_id=order_id, status=OrderStatus.blacklisted.value),
    )
    await query.answer()


@router.callback_query(Text(startswith="order:copy:"))
async def callback_copy(query: CallbackQuery) -> None:
    try:
        order_id = int(query.data.split(":")[2])
    except ValueError:
        await query.answer("订单参数错误", show_alert=True)
        return
    async with async_session() as session:
        order = await get_order(session, order_id=order_id)
        sms_text = order.sms_text if order else None
    if order is None or not sms_text:
        await query.answer("暂无短信内容", show_alert=True)
        return
    escaped = html.escape(sms_text)
    await query.message.answer(
        f"订单 <b>#{order_id}</b> 验证码内容：\n<code>{escaped}</code>"
    )
    await query.answer()
