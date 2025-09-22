"""项目选择回调。"""
from __future__ import annotations

from aiogram import Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery

router = Router(name="projects")


@router.callback_query(Text(startswith="project:"))
async def callback_project(query: CallbackQuery) -> None:
    await query.answer()
    if query.data == "project:fav":
        await query.message.answer("收藏功能将在下一阶段加入用户偏好存储。")
        return
    await query.message.answer("项目已选择，下一阶段将进入单价与确认下单流程。")
