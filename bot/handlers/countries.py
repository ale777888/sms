"""国家选择回调。"""
from aiogram import Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery

router = Router(name="countries")


@router.callback_query(Text(startswith="country:"))
async def callback_country(query: CallbackQuery) -> None:
    await query.answer()
    await query.message.answer("国家已选择，下一阶段将加载对应项目列表。")


@router.callback_query(Text(startswith="country_page:"))
async def callback_country_page(query: CallbackQuery) -> None:
    await query.answer("分页功能将在下一阶段整合真实数据", show_alert=True)
