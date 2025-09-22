"""订单相关回调。"""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery

from ..keyboards.orders import build_order_actions

router = Router(name="orders")


@router.callback_query(Text(startswith="order:poll:"))
async def callback_poll(query: CallbackQuery) -> None:
    await query.answer()
    await query.message.answer("开始轮询短信：功能将在下一阶段实现。")


@router.callback_query(Text(startswith="order:release:"))
async def callback_release(query: CallbackQuery) -> None:
    await query.answer()
    await query.message.answer("已收到释放指令，后续实现将调用短信平台接口。")


@router.callback_query(Text(startswith="order:black:"))
async def callback_black(query: CallbackQuery) -> None:
    await query.answer()
    await query.message.answer("加黑指令已记录，下一阶段将接入真实 API。")


@router.callback_query(Text(startswith="order:copy:"))
async def callback_copy(query: CallbackQuery) -> None:
    await query.answer("短信内容已复制", show_alert=True)


@router.callback_query(Text("menu:orders"))
async def callback_back(query: CallbackQuery) -> None:
    await query.answer()
    await query.message.edit_text(
        "订单功能正在开发中。",
        reply_markup=build_order_actions(order_id=1, status="created"),
    )
